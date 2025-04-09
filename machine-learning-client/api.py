from flask import Flask, request, jsonify
from flask_cors import CORS
from food_detection import FoodDetector
import requests
import uuid
import base64
import os

app = Flask(__name__)
CORS(app)
detector = FoodDetector()


@app.route("/detect-food", methods=["POST"])
def detect_food():
    """
    Handle incoming food detection requests via base64-encoded image.
    """
    try:
        data = request.get_json()
        print("Incoming JSON to /detect-food:", data)
        image_data = data.get("image_data")
        image_id = data.get("image_id")  # The unique image ID
        image_url = data.get("image_url")

        if not image_data:
            return jsonify({"status": "error", "message": "Missing image data"}), 400
        if not image_id:
            return jsonify({"status": "error", "message": "Missing image id"}), 400
        if not image_url:
            return jsonify({"status": "error", "message": "Missing image url"}), 400

        results = detector.detect_food(image_data)
        print(f"here are the {results}")
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


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5001)
