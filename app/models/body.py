# app/models/body.py
from datetime import datetime
from bson import ObjectId
from app import mongo

class Body:
    @staticmethod
    def log_weight(user_id, weight_data):
        """Log a weight entry"""
        entry = {
            "user_id": ObjectId(user_id),
            "weight": weight_data.get("weight"),  # in kg
            "unit": weight_data.get("unit", "kg"),
            "date": weight_data.get("date", datetime.now()),
            "notes": weight_data.get("notes", ""),
            "created_at": datetime.now()
        }
        result = mongo.db.body_logs.insert_one(entry)
        return str(result.inserted_id)
    
    @staticmethod
    def get_weight_history(user_id, start_date=None, end_date=None, limit=30):
        """Get weight history for a user"""
        query = {"user_id": ObjectId(user_id), "weight": {"$exists": True}}
        
        if start_date and end_date:
            query["date"] = {
                "$gte": start_date,
                "$lte": end_date
            }
        
        weights = mongo.db.body_logs.find(query).sort("date", -1).limit(limit)
        return list(weights)
    
    @staticmethod
    def log_measurements(user_id, measurement_data):
        """Log body measurements"""
        entry = {
            "user_id": ObjectId(user_id),
            "date": measurement_data.get("date", datetime.now()),
            "chest": measurement_data.get("chest"),
            "waist": measurement_data.get("waist"),
            "hips": measurement_data.get("hips"),
            "arms": measurement_data.get("arms"),
            "legs": measurement_data.get("legs"),
            "neck": measurement_data.get("neck"),
            "shoulders": measurement_data.get("shoulders"),
            "unit": measurement_data.get("unit", "cm"),
            "notes": measurement_data.get("notes", ""),
            "created_at": datetime.now()
        }
        result = mongo.db.body_logs.insert_one(entry)
        return str(result.inserted_id)
    
    @staticmethod
    def get_measurements_history(user_id, limit=10):
        """Get measurement history for a user"""
        # Query for documents that have at least one measurement field
        query = {
            "user_id": ObjectId(user_id),
            "$or": [
                {"chest": {"$exists": True}},
                {"waist": {"$exists": True}},
                {"hips": {"$exists": True}},
                {"arms": {"$exists": True}},
                {"legs": {"$exists": True}},
                {"neck": {"$exists": True}},
                {"shoulders": {"$exists": True}}
            ]
        }
        
        measurements = mongo.db.body_logs.find(query).sort("date", -1).limit(limit)
        return list(measurements)
    
    @staticmethod
    def log_body_composition(user_id, composition_data):
        """Log body composition metrics"""
        entry = {
            "user_id": ObjectId(user_id),
            "date": composition_data.get("date", datetime.now()),
            "body_fat_percentage": composition_data.get("body_fat_percentage"),
            "muscle_mass": composition_data.get("muscle_mass"),
            "bone_mass": composition_data.get("bone_mass"),
            "water_percentage": composition_data.get("water_percentage"),
            "bmi": composition_data.get("bmi"),
            "bmr": composition_data.get("bmr"),
            "visceral_fat": composition_data.get("visceral_fat"),
            "method": composition_data.get("method", "manual"),  # manual, scale, dexa, etc.
            "notes": composition_data.get("notes", ""),
            "created_at": datetime.now()
        }
        result = mongo.db.body_logs.insert_one(entry)
        return str(result.inserted_id)
    
    @staticmethod
    def get_body_composition_history(user_id, limit=10):
        """Get body composition history for a user"""
        query = {
            "user_id": ObjectId(user_id),
            "$or": [
                {"body_fat_percentage": {"$exists": True}},
                {"muscle_mass": {"$exists": True}},
                {"bone_mass": {"$exists": True}},
                {"water_percentage": {"$exists": True}},
                {"bmi": {"$exists": True}},
                {"bmr": {"$exists": True}},
                {"visceral_fat": {"$exists": True}}
            ]
        }
        
        compositions = mongo.db.body_logs.find(query).sort("date", -1).limit(limit)
        return list(compositions)
    
    @staticmethod
    def save_progress_photo(user_id, photo_data):
        """Save a progress photo"""
        entry = {
            "user_id": ObjectId(user_id),
            "date": photo_data.get("date", datetime.now()),
            "photo_url": photo_data.get("photo_url"),
            "category": photo_data.get("category", "front"),  # front, back, side
            "weight": photo_data.get("weight"),
            "notes": photo_data.get("notes", ""),
            "created_at": datetime.now()
        }
        result = mongo.db.progress_photos.insert_one(entry)
        return str(result.inserted_id)
    
    @staticmethod
    def get_progress_photos(user_id, category=None, limit=20):
        """Get progress photos for a user"""
        query = {"user_id": ObjectId(user_id)}
        
        if category:
            query["category"] = category
            
        photos = mongo.db.progress_photos.find(query).sort("date", -1).limit(limit)
        return list(photos)
    
    @staticmethod
    def set_body_goal(user_id, goal_data):
        """Set body metrics goals"""
        goal = {
            "user_id": ObjectId(user_id),
            "target_weight": goal_data.get("target_weight"),
            "target_body_fat": goal_data.get("target_body_fat"),
            "target_measurements": goal_data.get("target_measurements", {}),
            "deadline": goal_data.get("deadline"),
            "notes": goal_data.get("notes", ""),
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        }
        
        result = mongo.db.body_goals.update_one(
            {"user_id": ObjectId(user_id)},
            {"$set": goal},
            upsert=True
        )
        
        return result.modified_count > 0 or result.upserted_id is not None
    
    @staticmethod
    def get_body_goal(user_id):
        """Get body metrics goals for a user"""
        goal = mongo.db.body_goals.find_one({"user_id": ObjectId(user_id)})
        return goal