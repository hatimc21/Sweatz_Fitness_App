# app/models/workouts.py
from datetime import datetime
from bson import ObjectId
from app import mongo

class Workout:
    @staticmethod
    def create_routine(user_id, routine_data):
        """Create a workout routine"""
        routine = {
            "user_id": ObjectId(user_id),
            "name": routine_data.get("name"),
            "description": routine_data.get("description", ""),
            "type": routine_data.get("type", "custom"),  # custom, split, full-body
            "days": routine_data.get("days", []),  # Array of day objects with exercises
            "is_public": routine_data.get("is_public", False),
            "tags": routine_data.get("tags", []),
            "created_at": datetime.now()
        }
        
        result = mongo.db.workout_routines.insert_one(routine)
        return str(result.inserted_id)
    
    @staticmethod
    def get_routines(user_id, include_public=True):
        """Get workout routines for a user"""
        query = {
            "$or": [
                {"user_id": ObjectId(user_id)}
            ]
        }
        
        if include_public:
            query["$or"].append({"is_public": True})
        
        routines = mongo.db.workout_routines.find(query).sort("created_at", -1)
        return list(routines)
    
    @staticmethod
    def get_routine(routine_id):
        """Get a specific workout routine"""
        return mongo.db.workout_routines.find_one({"_id": ObjectId(routine_id)})
    
    @staticmethod
    def update_routine(routine_id, user_id, routine_data):
        """Update a workout routine"""
        # Check if routine exists and belongs to the user
        routine = mongo.db.workout_routines.find_one({
            "_id": ObjectId(routine_id),
            "user_id": ObjectId(user_id)
        })
        
        if not routine:
            return False
        
        result = mongo.db.workout_routines.update_one(
            {"_id": ObjectId(routine_id)},
            {"$set": {
                "name": routine_data.get("name"),
                "description": routine_data.get("description"),
                "type": routine_data.get("type"),
                "days": routine_data.get("days"),
                "is_public": routine_data.get("is_public"),
                "tags": routine_data.get("tags"),
                "updated_at": datetime.now()
            }}
        )
        
        return result.modified_count > 0
    
    @staticmethod
    def delete_routine(routine_id, user_id):
        """Delete a workout routine"""
        result = mongo.db.workout_routines.delete_one({
            "_id": ObjectId(routine_id),
            "user_id": ObjectId(user_id)
        })
        
        return result.deleted_count > 0
    
    @staticmethod
    def schedule_workout(user_id, schedule_data):
        """Schedule a workout"""
        scheduled = {
            "user_id": ObjectId(user_id),
            "routine_id": ObjectId(schedule_data.get("routine_id")) if schedule_data.get("routine_id") else None,
            "date": schedule_data.get("date"),
            "start_time": schedule_data.get("start_time"),
            "end_time": schedule_data.get("end_time"),
            "title": schedule_data.get("title"),
            "notes": schedule_data.get("notes", ""),
            "completed": schedule_data.get("completed", False),
            "notify": schedule_data.get("notify", True),
            "created_at": datetime.now()
        }
        
        result = mongo.db.scheduled_workouts.insert_one(scheduled)
        return str(result.inserted_id)
    
    @staticmethod
    def get_scheduled_workouts(user_id, start_date=None, end_date=None):
        """Get scheduled workouts for a date range"""
        query = {"user_id": ObjectId(user_id)}
        
        if start_date and end_date:
            query["date"] = {
                "$gte": start_date,
                "$lte": end_date
            }
        
        workouts = mongo.db.scheduled_workouts.find(query).sort("date", 1)
        return list(workouts)
    
    @staticmethod
    def update_scheduled_workout(workout_id, user_id, data):
        """Update a scheduled workout"""
        result = mongo.db.scheduled_workouts.update_one(
            {"_id": ObjectId(workout_id), "user_id": ObjectId(user_id)},
            {"$set": {
                "date": data.get("date"),
                "start_time": data.get("start_time"),
                "end_time": data.get("end_time"),
                "title": data.get("title"),
                "notes": data.get("notes"),
                "completed": data.get("completed"),
                "notify": data.get("notify"),
                "updated_at": datetime.now()
            }}
        )
        
        return result.modified_count > 0
    
    @staticmethod
    def delete_scheduled_workout(workout_id, user_id):
        """Delete a scheduled workout"""
        result = mongo.db.scheduled_workouts.delete_one({
            "_id": ObjectId(workout_id),
            "user_id": ObjectId(user_id)
        })
        
        return result.deleted_count > 0
    
    @staticmethod
    def log_completed_workout(user_id, workout_data):
        """Log a completed workout"""
        completed = {
            "user_id": ObjectId(user_id),
            "routine_id": ObjectId(workout_data.get("routine_id")) if workout_data.get("routine_id") else None,
            "scheduled_id": ObjectId(workout_data.get("scheduled_id")) if workout_data.get("scheduled_id") else None,
            "date": workout_data.get("date", datetime.now()),
            "duration": workout_data.get("duration", 0),  # in minutes
            "exercises": workout_data.get("exercises", []),
            "notes": workout_data.get("notes", ""),
            "rating": workout_data.get("rating", 0),  # 1-5 stars
            "created_at": datetime.now()
        }
        
        result = mongo.db.completed_workouts.insert_one(completed)
        
        # If this is linked to a scheduled workout, mark it as completed
        if workout_data.get("scheduled_id"):
            mongo.db.scheduled_workouts.update_one(
                {"_id": ObjectId(workout_data.get("scheduled_id"))},
                {"$set": {"completed": True}}
            )
            
        return str(result.inserted_id)
    
    @staticmethod
    def get_workout_history(user_id, limit=10):
        """Get workout history for a user"""
        workouts = mongo.db.completed_workouts.find(
            {"user_id": ObjectId(user_id)}
        ).sort("date", -1).limit(limit)
        
        return list(workouts)
    
    @staticmethod
    def get_exercises(filters=None, limit=100, skip=0):
        """Get exercises with optional filters"""
        query = {}
        
        if filters:
            if 'muscle_group' in filters:
                query['muscle_group'] = filters['muscle_group']
            if 'difficulty' in filters:
                query['difficulty'] = filters['difficulty']
            if 'equipment' in filters and filters['equipment']:
                query['equipment'] = {'$in': filters['equipment']}
            if 'search' in filters and filters['search']:
                query['name'] = {'$regex': filters['search'], '$options': 'i'}
        
        exercises = mongo.db.exercises.find(query).sort("name", 1).skip(skip).limit(limit)
        total = mongo.db.exercises.count_documents(query)
        
        return list(exercises), total
    
    @staticmethod
    def get_exercise_categories():
        """Get all exercise categories/muscle groups"""
        return mongo.db.exercises.distinct("muscle_group")
    
    @staticmethod
    def get_equipment_types():
        """Get all equipment types"""
        equipment = []
        pipeline = [
            {"$unwind": "$equipment"},
            {"$group": {"_id": "$equipment"}},
            {"$sort": {"_id": 1}}
        ]
        results = mongo.db.exercises.aggregate(pipeline)
        
        for result in results:
            equipment.append(result["_id"])
        
        return equipment
    
    @staticmethod
    def get_workout_stats(user_id, period="all"):
        """Get workout statistics for a user"""
        # Define the date range based on the period
        match_query = {"user_id": ObjectId(user_id)}
        
        if period == "week":
            # Last 7 days
            start_date = datetime.now() - timedelta(days=7)
            match_query["date"] = {"$gte": start_date}
        elif period == "month":
            # Last 30 days
            start_date = datetime.now() - timedelta(days=30)
            match_query["date"] = {"$gte": start_date}
        elif period == "year":
            # Last 365 days
            start_date = datetime.now() - timedelta(days=365)
            match_query["date"] = {"$gte": start_date}
        
        # Pipeline to get workout statistics
        pipeline = [
            {"$match": match_query},
            {"$group": {
                "_id": None,
                "total_workouts": {"$sum": 1},
                "total_duration": {"$sum": "$duration"},
                "avg_rating": {"$avg": "$rating"}
            }}
        ]
        
        stats = list(mongo.db.completed_workouts.aggregate(pipeline))
        
        if stats:
            stats = stats[0]
            stats.pop("_id", None)  # Remove _id field
        else:
            stats = {
                "total_workouts": 0,
                "total_duration": 0,
                "avg_rating": 0
            }
        
        # Get most trained muscle groups
        if period == "all":
            muscle_group_pipeline = [
                {"$match": {"user_id": ObjectId(user_id)}},
                {"$unwind": "$exercises"},
                {"$lookup": {
                    "from": "exercises",
                    "localField": "exercises.exercise_id",
                    "foreignField": "_id",
                    "as": "exercise_info"
                }},
                {"$unwind": "$exercise_info"},
                {"$group": {
                    "_id": "$exercise_info.muscle_group",
                    "count": {"$sum": 1}
                }},
                {"$sort": {"count": -1}},
                {"$limit": 5}
            ]
            
            muscle_groups = list(mongo.db.completed_workouts.aggregate(muscle_group_pipeline))
            stats["top_muscle_groups"] = muscle_groups
        
        return stats