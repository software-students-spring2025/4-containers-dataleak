import os
from dotenv import load_dotenv, dotenv_values
from flask import Flask, render_template, request, redirect, url_for, session
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
from datetime import datetime
import json
from food_categories import CATEGORIES, category_icons
from collections import defaultdict

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

    @app.route("/manual_add_food", methods=["POST"])
    def manual_add_food():
        user_id = current_user.id
        food_name = request.form["food_name"].lower()  # Convert food name to lowercase
        category = request.form["category"]

        # Ensure the category is valid by checking if it exists in CATEGORIES
        if category not in CATEGORIES:
            category = "Other"  # Default to "Other" if the category is not valid

        new_food = {
            "food_name": food_name,
            "category": category,
            "added_at": datetime.utcnow(),
            "user_id": ObjectId(
                user_id
            ),  # Store the user_id to associate food with the logged-in user
        }

        # Insert into the correct collection
        db.foods.insert_one(new_food)
        return redirect(url_for("fridge"))

    @app.route("/fridge")
    @login_required
    def fridge():
        """
        Get user's virtual fridge items
        """
        user_id = current_user.id
        # Fetch items from the database for the logged-in user
        print("Fetching and categorizing items...")
        items = list(db.foods.find({"user_id": ObjectId(user_id)}).sort("added_at", -1))
        print("Items fetched:", items)

        # Mapping food items to their respective categories
        food_to_category = {}
        for category, foods in CATEGORIES.items():
            for food in foods:
                food_to_category[food.lower()] = category

        # Categorizing the food items
        categorized = defaultdict(list)
        print(categorized)
        # Add items to their respective categories
        for item in items:
            name = item.get(
                "food_name", ""
            ).lower()  # Ensure the food_name is also lowercase
            category = food_to_category.get(
                name, "Other"
            )  # If not found, categorize as "Other"
            categorized[category].append(item)

        # Ensure every category in CATEGORIES has an entry in categorized (even if empty)
        for category in CATEGORIES:
            if category not in categorized:
                categorized[category] = []

        return render_template(
            "fridge.html",
            categorized_items=categorized,
            category_icons=category_icons,
            categories=CATEGORIES,
        )

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
            decode = image_data.split(",")[1]  # Remove base64 prefix
            image_bytes = base64.b64decode(decode)

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

            ##Converting image_byes to JSON Serializable
            image_bytes_b64 = base64.b64encode(image_bytes).decode("utf-8")

            # Save the image URL and other data in the database
            food_images_collection.insert_one(
                {
                    "image_id": image_id,  # Unique ID for the image
                    "image_data": image_bytes_b64,  # Store the URL of the image
                    "image_url": image_url,
                    "created_at": datetime.utcnow(),
                }
            )

            return image_id, image_url, image_bytes_b64  # Return the unique image ID

        except Exception as e:
            print(f"Error saving image: {e}")  # Print any errors to debug
            return None, None, None

    @app.route("/add-food", methods=["GET", "POST"])
    def add_food():
        if request.method == "GET":
            return render_template("add_food.html")
        else:
            try:
                user_id = current_user.id
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
                image_id, image_url, image_data = save_image_to_db(image_data)
                print("Image Succesfully Added to Database")

                # Send image data to ML service for detection
                detect_url = "http://ml-client:5001/detect-food"
                response = requests.post(
                    detect_url,
                    json={
                        "image_data": image_data,  # URL to image
                        "image_id": image_id,  # Unique image ID
                        "image_url": image_url,  # URL to the image
                    },
                    timeout=30,
                )

                if response.status_code == 200:
                    print("Image Succesfully Sent to ML Client")
                    detection_result = response.json()
                    if detection_result["status"] == "success":
                        food_detected = detection_result.get("food_detected", [])
                        if food_detected:
                            ##Add Found Foods to User Food List
                            for i in food_detected:
                                category = next(
                                    (
                                        cat
                                        for cat, items in CATEGORIES.items()
                                        if i.lower() in [x.lower() for x in items]
                                    ),
                                    "Uncategorized",
                                )
                                new_food = {
                                    "food_name": i,
                                    "category": category,
                                    "image_id": image_id,
                                    "added_at": datetime.utcnow(),
                                    "user_id": ObjectId(
                                        user_id
                                    ),  # Store the user_id to associate food with the logged-in user
                                }
                                db.foods.insert_one(new_food)
                            # Return food detection results to a new page (food_results.html)
                            return jsonify(
                                {
                                    "status": "success",
                                    "image_id": image_id,
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
                    print(response.json())
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
        image_id = request.args.get("image_id")

        # Decode the food_detected list from JSON
        try:
            food_list = json.loads(food_detected)
        except:
            food_list = []

        return render_template(
            "food_results.html",
            food_detected=food_list,
            image_url=image_url,
            image_id=image_id,
        )

    @app.route("/confirm-detected-food", methods=["POST"])
    @login_required
    def confirm_detected_food():
        action = request.form.get("action")
        image_id = request.form.get("image_id")
        user_id = current_user.id

        print(f"Image ID: {image_id}, User ID: {user_id}")

        if action == "add":
            selected_foods = request.form.getlist("selected_foods")

            db.foods.delete_many({"image_id": image_id})

            if selected_foods:
                for food in selected_foods:
                    add_food_to_fridge(food, image_id, user_id)

            return redirect(url_for("fridge"))
        else:
            db.foods.delete_many({"image_id": image_id})
            return redirect(url_for("add_food"))

    def add_food_to_fridge(food, image_id, user_id):
        """Function to add selected food to the fridge (database)."""
        category = next(
            (
                cat
                for cat, items in CATEGORIES.items()
                if food.lower() in [x.lower() for x in items]
            ),
            "Uncategorized",
        )
        new_food = {
            "food_name": food,
            "category": category,
            "image_id": image_id,
            "added_at": datetime.utcnow(),
            "user_id": ObjectId(user_id),
        }

        # Insert the food into the database
        db.foods.insert_one(new_food)

    @app.route("/delete-food/<food_id>", methods=["POST"])
    @login_required
    def delete_food(food_id):
        """
        Deletes a food item from fridge given id
        """
        db.foods.delete_one(
            {"_id": ObjectId(food_id), "user_id": ObjectId(current_user.id)}
        )
        return redirect(url_for("fridge"))

    return app


app = create_app()

if __name__ == "__main__":
    FLASK_PORT = os.getenv("FLASK_PORT", "5000")
    FLASK_ENV = os.getenv("FLASK_ENV")
    print(f"FLASK_ENV: {FLASK_ENV}, FLASK_PORT: {FLASK_PORT}")
    app.run(debug=True, host="0.0.0.0", port=int(FLASK_PORT))
