from datetime import datetime
from bson import ObjectId
from app import mongo

class Nutrition:
    @staticmethod
    def create_meal(user_id, meal_data):
        """Create a new meal entry"""
        meal = {
            "user_id": ObjectId(user_id),
            "name": meal_data.get("name", ""),
            "time": meal_data.get("time", datetime.now()),
            "calories": meal_data.get("calories", 0),
            "protein": meal_data.get("protein", 0),
            "carbs": meal_data.get("carbs", 0),
            "fats": meal_data.get("fats", 0),
            "foods": meal_data.get("foods", []),
            "created_at": datetime.now()
        }
        result = mongo.db.meals.insert_one(meal)
        return str(result.inserted_id)
    
    @staticmethod
    def get_meals_by_date(user_id, date):
        """Get all meals for a user on a specific date"""
        start_date = datetime.combine(date, datetime.min.time())
        end_date = datetime.combine(date, datetime.max.time())
        
        meals = mongo.db.meals.find({
            "user_id": ObjectId(user_id),
            "time": {
                "$gte": start_date,
                "$lte": end_date
            }
        }).sort("time", 1)
        
        return list(meals)
    
    @staticmethod
    def get_meal(meal_id):
        """Get a specific meal by ID"""
        return mongo.db.meals.find_one({"_id": ObjectId(meal_id)})
    
    @staticmethod
    def update_meal(meal_id, meal_data):
        """Update a meal entry"""
        result = mongo.db.meals.update_one(
            {"_id": ObjectId(meal_id)},
            {"$set": {
                "name": meal_data.get("name"),
                "time": meal_data.get("time"),
                "calories": meal_data.get("calories"),
                "protein": meal_data.get("protein"),
                "carbs": meal_data.get("carbs"),
                "fats": meal_data.get("fats"),
                "foods": meal_data.get("foods"),
                "updated_at": datetime.now()
            }}
        )
        return result.modified_count > 0
    
    @staticmethod
    def delete_meal(meal_id):
        """Delete a meal entry"""
        result = mongo.db.meals.delete_one({"_id": ObjectId(meal_id)})
        return result.deleted_count > 0
    
    @staticmethod
    def log_water_intake(user_id, intake_data):
        """Log water intake for a user"""
        intake = {
            "user_id": ObjectId(user_id),
            "amount": intake_data.get("amount", 0),  # in ml
            "time": intake_data.get("time", datetime.now()),
            "created_at": datetime.now()
        }
        result = mongo.db.water_intake.insert_one(intake)
        return str(result.inserted_id)
    
    @staticmethod
    def get_daily_water_intake(user_id, date):
        """Get total water intake for a specific date"""
        start_date = datetime.combine(date, datetime.min.time())
        end_date = datetime.combine(date, datetime.max.time())
        
        pipeline = [
            {
                "$match": {
                    "user_id": ObjectId(user_id),
                    "time": {
                        "$gte": start_date,
                        "$lte": end_date
                    }
                }
            },
            {
                "$group": {
                    "_id": None,
                    "total_amount": {"$sum": "$amount"}
                }
            }
        ]
        
        result = list(mongo.db.water_intake.aggregate(pipeline))
        if result:
            return result[0].get("total_amount", 0)
        return 0
    
    @staticmethod
    def set_nutrition_goal(user_id, goal_data):
        """Create or update nutrition goal for a user"""
        goal = {
            "user_id": ObjectId(user_id),
            "calories": goal_data.get("calories", 0),
            "protein": goal_data.get("protein", 0),
            "carbs": goal_data.get("carbs", 0),
            "fats": goal_data.get("fats", 0),
            "water": goal_data.get("water", 0),
            "updated_at": datetime.now()
        }
        
        result = mongo.db.nutrition_goals.update_one(
            {"user_id": ObjectId(user_id)},
            {"$set": goal},
            upsert=True
        )
        
        return result.modified_count > 0 or result.upserted_id is not None
    
    @staticmethod
    def get_nutrition_goal(user_id):
        """Get nutrition goal for a user"""
        goal = mongo.db.nutrition_goals.find_one({"user_id": ObjectId(user_id)})
        if not goal:
            # Return default goals if none set
            return {
                "calories": 2000,
                "protein": 150,
                "carbs": 200,
                "fats": 65,
                "water": 2000
            }
        return goal
    
    @staticmethod
    def get_daily_nutrition_summary(user_id, date):
        """Get nutrition summary for a specific date"""
        start_date = datetime.combine(date, datetime.min.time())
        end_date = datetime.combine(date, datetime.max.time())
        
        pipeline = [
            {
                "$match": {
                    "user_id": ObjectId(user_id),
                    "time": {
                        "$gte": start_date,
                        "$lte": end_date
                    }
                }
            },
            {
                "$group": {
                    "_id": None,
                    "total_calories": {"$sum": "$calories"},
                    "total_protein": {"$sum": "$protein"},
                    "total_carbs": {"$sum": "$carbs"},
                    "total_fats": {"$sum": "$fats"},
                    "meals_count": {"$sum": 1}
                }
            }
        ]
        
        result = list(mongo.db.meals.aggregate(pipeline))
        
        if result:
            return result[0]
        
        return {
            "total_calories": 0,
            "total_protein": 0,
            "total_carbs": 0,
            "total_fats": 0,
            "meals_count": 0
        }