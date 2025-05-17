# app/models/workouts.py
from datetime import datetime
from bson import ObjectId
from app import mongo

class Workout:
    @staticmethod
    def create_exercise(exercise_data):
        """Create a new exercise in the database"""
        exercise = {
            "name": exercise_data.get("name"),
            "muscle_group": exercise_data.get("muscle_group", "other"),
            "difficulty": exercise_data.get("difficulty", "intermediate"),
            "description": exercise_data.get("description", ""),
            "instruction": exercise_data.get("instruction", ""),
            "video_url": exercise_data.get("video_url", ""),
            "equipment": exercise_data.get("equipment", []),
            "created_by": exercise_data.get("created_by"),  # Admin ID
            "created_at": datetime.now()
        }
        
        result = mongo.db.exercises.insert_one(exercise)
        return str(result.inserted_id)
    
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
    def get_exercise(exercise_id):
        """Get a specific exercise by ID"""
        return mongo.db.exercises.find_one({"_id": ObjectId(exercise_id)})
    
    @staticmethod
    def update_exercise(exercise_id, exercise_data):
        """Update an exercise"""
        result = mongo.db.exercises.update_one(
            {"_id": ObjectId(exercise_id)},
            {"$set": {
                "name": exercise_data.get("name"),
                "muscle_group": exercise_data.get("muscle_group"),
                "difficulty": exercise_data.get("difficulty"),
                "description": exercise_data.get("description"),
                "instruction": exercise_data.get("instruction"),
                "video_url": exercise_data.get("video_url"),
                "equipment": exercise_data.get("equipment"),
                "updated_at": datetime.now(),
                "updated_by": exercise_data.get("updated_by")
            }}
        )
        return result.modified_count > 0
    
    @staticmethod
    def delete_exercise(exercise_id):
        """Delete an exercise"""
        result = mongo.db.exercises.delete_one({"_id": ObjectId(exercise_id)})
        return result.deleted_count > 0
    
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

# Add or enhance these methods in app/models/workouts.py

@staticmethod
def create_workout_template(user_id, template_data):
    """Create a workout template"""
    template = {
        "created_by": ObjectId(user_id),
        "name": template_data.get("name"),
        "description": template_data.get("description", ""),
        "type": template_data.get("type", "custom"),  # custom, split, full-body, etc.
        "is_public": template_data.get("is_public", False),
        "tags": template_data.get("tags", []),
        "days": template_data.get("days", []),  # Array of day objects with exercises
        "created_at": datetime.now()
    }
    
    result = mongo.db.workout_routines.insert_one(template)
    return str(result.inserted_id)

@staticmethod
def get_workout_templates(include_public=True, limit=20, skip=0):
    """Get workout templates"""
    query = {}
    
    if not include_public:
        query["is_public"] = True
    
    templates = mongo.db.workout_routines.find(query).sort("created_at", -1).skip(skip).limit(limit)
    return list(templates)

@staticmethod
def get_workout_template(template_id):
    """Get a specific workout template"""
    return mongo.db.workout_routines.find_one({"_id": ObjectId(template_id)})

@staticmethod
def update_workout_template(template_id, user_id, template_data):
    """Update a workout template"""
    update_data = {
        "name": template_data.get("name"),
        "description": template_data.get("description"),
        "type": template_data.get("type"),
        "is_public": template_data.get("is_public", False),
        "tags": template_data.get("tags", []),
        "days": template_data.get("days", []),
        "updated_at": datetime.now(),
        "updated_by": ObjectId(user_id)
    }
    
    result = mongo.db.workout_routines.update_one(
        {"_id": ObjectId(template_id)},
        {"$set": update_data}
    )
    
    return result.modified_count > 0

@staticmethod
def delete_workout_template(template_id):
    """Delete a workout template"""
    result = mongo.db.workout_routines.delete_one({"_id": ObjectId(template_id)})
    return result.deleted_count > 0

@staticmethod
def parse_template_form_data(form_data):
    """Parse complex nested form data for workout templates"""
    days = []
    
    # Logic to extract days and exercises from form data
    # This is where you'd handle complex form data processing
    
    return days