"""
Module for interacting with the MongoDB database to save and retrieve food detection results.

This module provides the `DataBaseML` class to interface with a MongoDB database.
It allows saving food detection results and retrieving them by image ID. The database
connection details are loaded from environment variables.

Dependencies:
- pymongo: For MongoDB connection and operations.
- dotenv: For loading environment variables.
"""
from datetime import datetime
import os
import pymongo
from dotenv import load_dotenv

class DataBaseML:
    """
    Class for handling food detection results in the MongoDB database.

    This class provides methods to save and retrieve food detection results in a MongoDB database.
    It uses environment variables to connect to the database and ensure secure operation.

    Methods:
        save_food_result(foods, user_id=None): Saves food detection results to the database.
        get_detection_result(image_id): Retrieves food results by image ID from the database.
    """
    def __init__(self):
        """
        Initialize database connection and load environment variables.
        """
        load_dotenv()
        cxn = pymongo.MongoClient(os.getenv("MONGO_URI"))
        self.db = cxn[os.getenv("MONGO_DBNAME")]

    def save_food_result(self, foods, user_id=None):
        """
        Save food detection results to the database.

        Args:
            foods (list): List of detected foods.
            user_id (str, optional): Optional user identifier.

        Returns:
            Inserted result object.
        """
        collection = self.db.detection_results

        document = {
            "foods": foods,
            "timestamp": datetime.utcnow(),
        }

        if user_id:
            document["user_id"] = user_id

        return collection.insert_one(document)

    def get_detection_result(self, image_id):
        """
        Get food detection results from the database by image_id.

        Args:
            image_id (str): Unique identifier for the image.

        Returns:
            dict or None: Food results or None if not found.
        """
        collection = self.db.detection_results
        result = collection.find_one({"image_id": image_id})

        if result:
            # Convert ObjectId to string for JSON serialization
            result["_id"] = str(result["_id"])
            return result
        return None
