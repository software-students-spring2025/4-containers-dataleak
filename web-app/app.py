import os
from dotenv import load_dotenv, dotenv_values
from flask import Flask, request, redirect, url_for, render_template
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import pymongo
from bson.objectid import ObjectId
import base64
import requests
from io import BytesIO
from PIL import Image

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
   app.config['TEMPLATES_AUTO_RELOAD'] = True  # Auto reload templates for development

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
                  return render_template("index.html", error="Incorrect Password. Try again.")
               
            # if user is not found
            else:
               return render_template("index.html", error="User not found. Create a new account")
            
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
                  return render_template("register.html", error="Username already exists.")
               
               # add new user to database
               user_doc = {
                  "username": username,
                     "password": password
               }
               added_user = db.users.insert_one(user_doc)

               # track new user
               user = User()
               user.id = str(added_user.inserted_id)
               login_user(user)

               # redirect to fridge page for user
               return redirect(url_for("fridge"))
            else:
               ##Displaying error
               return render_template("register.html", error="Passwords do not match.")
         else:
            return render_template("register.html", error="All form fields are required")
      
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
      items = list(db.food_items.find({"user_id": ObjectId(user_id)}).sort("added_at", -1))
      return render_template("fridge.html", food_items=items)

   @app.route("/add-food", methods=["POST", "GET"])
   @login_required
   def add_food():
      """
      Render the add food page and handle image upload and detection.

      Returns:
         Response: Rendered HTML page or redirect after detection
      """
      if request.method == "POST":
         try:
               image_data_url = request.form.get("image_data")
               if not image_data_url:
                  return render_template("add_food.html", error="No image data provided")

               # Decode base64 image data
               image_data = image_data_url.split(",")[1]
               image_binary = base64.b64decode(image_data)

               # Generate a unique filename and save the image
               filename = f"food_image_{current_user.id}_{str(ObjectId())}.png"
               image_path = os.path.join("static", "food_images", filename)
               with open(image_path, "wb") as f:
                  f.write(image_binary)

               # Save metadata to MongoDB
               food_doc = {
                  "user_id": ObjectId(current_user.id),
                  "image_url": f"/{image_path.replace('static/', '')}",
                  "added_at": datetime.datetime.now()
               }
               db.food_items.insert_one(food_doc)

               # Send image to ML service
               detect_url = "http://ml-client:5001/detect-food"
               response = requests.post(detect_url, json={"image_data": image_data_url})

               if response.status_code == 200:
                  return redirect(url_for("fridge"))
               return render_template("add_food.html", error="Food detection failed")

         except Exception as e:
               print(f"Error in add_food: {e}")
               return render_template("add_food.html", error="An unexpected error occurred")

      return render_template("add_food.html")



   @app.route("/delete-food/<food_id>")
   @login_required
   def delete_food(food_id):
      """
      Deletes a food item from fridge given id
      """
      db.food_items.delete_one({
         "_id": ObjectId(food_id), 
         "user_id": ObjectId(current_user.id)
      })
      return redirect(url_for("fridge"))


   # more functions go here
   return app

app = create_app()

if __name__ == "__main__":
   FLASK_PORT = os.getenv("FLASK_PORT", "5100")
   FLASK_ENV = os.getenv("FLASK_ENV")
   print(f"FLASK_ENV: {FLASK_ENV}, FLASK_PORT: {FLASK_PORT}")
   app.run(debug=True, host="0.0.0.0", port=int(FLASK_PORT))
