import pymongo
from pymongo import MongoClient
from datetime import datetime
import os
from dotenv import load_dotenv, dotenv_values


class DataBaseML:
    def __init__(self):
        import pymongo
        from pymongo import MongoClient
        from dotenv import load_dotenv, dotenv_values

        load_dotenv()
        cxn = pymongo.MongoClient(os.getenv("MONGO_URI"))
        self.db = cxn[os.getenv("MONGO_DBNAME")]

    def save_food_result(self, foods, user_id=None):
        """
        Save food detection results to database

        Args:
            image_id: Unique identifier for the image
            emotions: List containing detected foods
            user_id: Optional user identifier
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
        Get food detection results from database by image_id

        Args:
            image_id: Unique identifier for the image

        Returns:
            list: Food results or None if not found
        """
        collection = self.db.detection_results
        result = collection.find_one({"image_id": image_id})

        if result:
            # Convert ObjectId to string for JSON serialization
            result["_id"] = str(result["_id"])
            return result
        return None
