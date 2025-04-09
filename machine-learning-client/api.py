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
    """
    try:
        data = request.get_json()
        image_data = data.get("image_data")
        image_id = data.get("image_id")  # The unique image ID
        image_url = data.get("image_url")

        if not image_data or not image_id or not image_url:
            return (
                jsonify({"status": "error", "message": "Missing required parameters"}),
                400,
            )

        results = detector.detect_food(image_url)

        if results[0] == "Success":
            food_detected = results[1]  # List of detected foods
            return jsonify(
                {
                    "status": "success",
                    "food_detected": food_detected,
                    "image_id": image_id,
                    "image_url": image_url,
                }
            )
        else:
            return jsonify({"status": "error", "message": "Food detector failed"}), 500
    except Exception as e:
        # logging.error(f"Error during food detection: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/get-detection/<image_id>", methods=["GET"])
def get_detection(image_id):
    try:
        result = db_handler.get_detection_result(image_id)

        if result is None:
            return jsonify({"status": "error", "message": "Image ID not found"}), 404

        return jsonify({"status": "success", "data": result})

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)
