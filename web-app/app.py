
import os
from dotenv import load_dotenv, dotenv_values
from flask import Flask, request, redirect, url_for, render_template
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import pymongo
from bson.objectid import ObjectId


# get env variables from .env
load_dotenv()

def create_app():
   """
   Create the Flask Application
   returns: app: the Flask application object
   """

   app = Flask(__name__)

   # set flask config from env variables
   config = dotenv_values()
   app.config.from_mapping(config)

   # set up for flask login
   app.secret_key = os.getenv("KEY")
   login_manager = LoginManager()
   login_manager.init_app(app)
   login_manager.login_view = "index"

   # connect to mongo db using .env file
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
            return render_template("register.html", error="Passwords do not match.")
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
      items = list(db.food_items.find({"user_id": ObjectId(user_id)}).sort("added_at", -1))
      return render_template("fridge.html", food_items = items)
   
   @app.route("/add-food")
   @login_required
   def add_food():
      """
      Page to add food with user camera
      """
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
   app.run(debug=True, port=FLASK_PORT)
