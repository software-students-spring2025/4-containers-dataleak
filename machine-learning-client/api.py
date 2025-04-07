from flask import Flask, request, jsonify
from flask_cors import CORS
from database_ml import DataBaseML
from food_detection import FoodDetector
import cv2
import numpy as np
import uuid

app = Flask(__name__)
CORS(app)
db_handler = DataBaseML()
detector = FoodDetector()

@app.route("/detect/<food_id>", methods=["POST"])
def detect_food(food_id):
    """
    Process the food image based on the food item ID, detect food.
    The food_id is used to look up the food item and extract the image URL.
    """

    try:
        # Fetch the food item from the database using food_id
        food_item = db.food_items.find_one({"_id": ObjectId(food_id)})

        if not food_item:
            return jsonify({"status": "error", "message": "Food item not found"}), 404

        # Get the image URL from the food item
        image_url = food_item.get("image_url")

        if not image_url:
            return jsonify({"status": "error", "message": "No image URL available for this food item"}), 400

        # Pass the image URL to the FoodDetector
        results = detector.detect_food(image_url)

        if results[0] == "Success":
            image_id = str(uuid.uuid4())  # Generate a unique image ID
            user_id = food_item["user_id"]  # Use the user_id from the food item document

            for food in results[1]:
                # Save the food detection result in the database
                db_handler.save_food_result(image_id, food, user_id)

            return jsonify(
                {"status": "success", "image_id": image_id, "food_detected": results[1]}
            )

        return jsonify({"status": "error", "message": "Food detection failed"}), 500

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

