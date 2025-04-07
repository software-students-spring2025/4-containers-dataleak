from flask import Flask, request, jsonify
from flask_cors import CORS
from database_ml import DataBaseML
from food_detection import FoodDetector
import requests
import uuid
import base64
import os

app = Flask(__name__)
CORS(app)
db_handler = DataBaseML()
detector = FoodDetector()

@app.route("/detect-food", methods=["POST"])
def detect_food():
    """
    Handle incoming food detection requests via base64-encoded image.

    Returns:
        JSON: Detection result including food labels or error message
    """
    try:
        data = request.get_json()
        image_data_url = data.get("image_data")

        if not image_data_url:
            return jsonify({"status": "error", "message": "No image data provided"}), 400

        # Decode the base64 string to binary
        image_data = image_data_url.split(",")[1]
        image_binary = base64.b64decode(image_data)

        # Save the image to disk
        image_id = str(uuid.uuid4())
        filename = f"food_image_{image_id}.png"
        image_path = os.path.join("static", "food_images", filename)
        with open(image_path, "wb") as f:
            f.write(image_binary)

        image_url = f"/{image_path.replace('static/', '')}"
        results = detector.detect_food(image_url)

        if results[0] == "Success":
            food_id = str(uuid.uuid4())
            user_id = "user_id_here"  # Replace with actual user_id when integrated

            for food_item in results[1]:
                db_handler.save_food_result(food_id, food_item, user_id)

            return jsonify({
                "status": "success",
                "food_detected": results[1],
                "image_url": image_url,
            })

        return jsonify({"status": "error", "message": "Food detection failed"}), 500

    except Exception as e:
        print(f"Error in detect_food: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500
