import os
from dotenv import load_dotenv, dotenv_values
from flask import Flask, request, redirect, url_for, render_template
from flask_login import (
    LoginManager,
    UserMixin,
    login_user,
    login_required,
    logout_user,
    current_user,
)
import pymongo
from bson.objectid import ObjectId
import base64
import requests
from io import BytesIO
from PIL import Image
import uuid
from flask import jsonify, send_from_directory
import datetime
import json

# get env variables from .env
load_dotenv()


def create_app():
    """
    Create the Flask Application
    returns: app: the Flask application object
    """

    app = Flask(__name__)

    # set flask config from env variables
    app.secret_key = os.urandom(24)  # Secret key for session management
    app.config["TEMPLATES_AUTO_RELOAD"] = True  # Auto reload templates for development

    # set up for flask login
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = "index"

    cxn = pymongo.MongoClient(os.getenv("MONGO_URI"))
    db = cxn[os.getenv("MONGO_DBNAME")]

    # testing for mongoDB connection
    try:
        cxn.admin.command("ping")
        print(" * Connected to MongoDB")
    except Exception as e:
        print(" * Error connecting to MongodDB", e)

    food_images_collection = db.food_images

    UPLOAD_FOLDER = "uploads"
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)

    # class for user login
    class User(UserMixin):
        pass

    @login_manager.user_loader
    def user_loader(id):
        if db is None:
            return None

        user_file = db.users.find_one({"_id": ObjectId(id)})
        if not user_file:
            return None
        user = User()
        user.id = str(user_file["_id"])
        return user

    @app.route("/", methods=["GET", "POST"])
    def index():
        """
        index is the home route, the login page.
        """
        # try to get user when form is submitted
        if request.method == "POST":
            username = request.form.get("username")
            password = request.form.get("password")

            if username and password:
                user_doc = db.users.find_one({"username": username})
                if user_doc:

                    # redirect user if login was successfull
                    if user_doc["password"] == password:
                        user = User()
                        user.id = str(user_doc["_id"])
                        login_user(user)
                        return redirect(url_for("fridge"))

                    # if user found but incorrect password
                    else:
                        return render_template(
                            "index.html", error="Incorrect Password. Try again."
                        )

                # if user is not found
                else:
                    return render_template(
                        "index.html", error="User not found. Create a new account"
                    )

        return render_template("index.html")

    @app.route("/register", methods=["GET", "POST"])
    def register():
        """
        Route for user registration
        """
        if request.method == "POST":
            username = request.form.get("username").strip()
            password = request.form.get("password").strip()
            confirm_password = request.form.get("confirm_password").strip()

            if username and password and confirm_password:
                if password == confirm_password:
                    existing_user = db.users.find_one({"username": username})

                    # if existing user found, show error
                    if existing_user:
                        return render_template(
                            "register.html", error="Username already exists."
                        )

                    # add new user to database
                    user_doc = {"username": username, "password": password}
                    added_user = db.users.insert_one(user_doc)

                    # track new user
                    user = User()
                    user.id = str(added_user.inserted_id)
                    login_user(user)

                    # redirect to fridge page for user
                    return redirect(url_for("fridge"))
                else:
                    ##Displaying error
                    return render_template(
                        "register.html", error="Passwords do not match."
                    )
            else:
                return render_template(
                    "register.html", error="All form fields are required"
                )

        # render register page when not a post request
        return render_template("register.html")

    @app.route("/logout")
    @login_required
    def logout():
        """
        Route for logging user out
        """
        logout_user()
        return redirect(url_for("index"))

    @app.route("/fridge")
    @login_required
    def fridge():
        """
        Get user's virtual fridge items
        """
        user_id = current_user.id
        # Fetch items from the database for the logged-in user
        items = list(
            db.food_items.find({"user_id": ObjectId(user_id)}).sort("added_at", -1)
        )
        return render_template("fridge.html", food_items=items)

    @app.route("/uploads/<filename>")
    def uploaded_file(filename):
        return send_from_directory("uploads", filename)

    def save_image_to_db(image_data):
        """
        Save the image to a URL (by saving the image to a file) and store the URL in the database.
        The image is saved in the 'uploads' folder with a unique name.
        """
        try:
            # Decode the base64 image data
            image_data = image_data.split(",")[1]  # Remove base64 prefix
            image_bytes = base64.b64decode(image_data)

            # Create a unique filename for the image
            image_id = str(uuid.uuid4())
            image_filename = f"{image_id}.png"
            image_path = os.path.join(UPLOAD_FOLDER, image_filename)

            # Save the image to the 'uploads' directory
            with open(image_path, "wb") as image_file:
                image_file.write(image_bytes)

            print(f"Image saved at: {image_path}")  # Add this to check if file is saved

            # Generate a URL for the saved image
            image_url = f"http://localhost:5000/uploads/{image_filename}"  # Adjust this URL if you're using cloud storage

            print(image_url)
            # Save the image URL and other data in the database
            food_images_collection.insert_one(
                {
                    "image_id": image_id,  # Unique ID for the image
                    "image_data": image_url,  # Store the URL of the image
                    "created_at": datetime.datetime.utcnow(),
                }
            )

            return image_id, image_url  # Return the unique image ID

        except Exception as e:
            print(f"Error saving image: {e}")  # Print any errors to debug
            return None, None

    @app.route("/add-food", methods=["GET", "POST"])
    def add_food():
        if request.method == "GET":
            return render_template("add_food.html")
        else:
            try:
                # Get the image data from the request
                data = request.get_json()
                image_data = data.get("image_data")

                if not image_data:
                    return (
                        jsonify(
                            {"status": "error", "message": "No image data provided"}
                        ),
                        400,
                    )

                # Save the image to the database and get the unique image ID
                image_id, image_url = save_image_to_db(image_data)

                # Send image data to ML service for detection
                detect_url = "http://ml-client:5001/detect"
                response = requests.post(
                    detect_url,
                    json={
                        "image_data": image_url,  # URL to image
                        "image_id": image_id,  # Unique image ID
                        "image_url": image_url,  # URL to the image
                    },
                )

                if response.status_code == 200:
                    detection_result = response.json()
                    if detection_result["status"] == "success":
                        food_detected = detection_result.get("food_detected", [])
                        if food_detected:
                            # Return food detection results to a new page (food_results.html)
                            return jsonify(
                                {
                                    "status": "success",
                                    "image_url": image_url,
                                    "food_detected": food_detected,
                                }
                            )
                        else:
                            return jsonify(
                                {
                                    "status": "error",
                                    "message": "No foods detected",
                                    "image_url": image_url,
                                }
                            )
                    else:
                        return jsonify(
                            {
                                "status": "error",
                                "message": "Food detection failed",
                                "image_url": image_url,
                            }
                        )
                else:
                    return jsonify(
                        {
                            "status": "error",
                            "message": "Food detection failed",
                            "image_url": image_url,
                        }
                    )

            except Exception as e:
                print(f"Error in detect_food: {e}")
                return jsonify(
                    {"status": "error", "message": "An unexpected error occurred"}
                )

    @app.route("/food-results")
    def food_results():
        food_detected = request.args.get("food_detected")
        image_url = request.args.get("image_url")

        # Decode the food_detected list from JSON
        try:
            food_list = json.loads(food_detected)
        except:
            food_list = []

        return render_template(
            "food_results.html", food_detected=food_list, image_url=image_url
        )

    @app.route("/delete-food/<food_id>")
    @login_required
    def delete_food(food_id):
        """
        Deletes a food item from fridge given id
        """
        db.food_items.delete_one(
            {"_id": ObjectId(food_id), "user_id": ObjectId(current_user.id)}
        )
        return redirect(url_for("fridge"))

    # more functions go here
    return app


app = create_app()

if __name__ == "__main__":
    FLASK_PORT = os.getenv("FLASK_PORT", "5000")
    FLASK_ENV = os.getenv("FLASK_ENV")
    print(f"FLASK_ENV: {FLASK_ENV}, FLASK_PORT: {FLASK_PORT}")
    app.run(debug=True, host="0.0.0.0", port=int(FLASK_PORT))
