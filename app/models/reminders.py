from datetime import datetime
from bson import ObjectId
from app import mongo

class Reminder:
    @staticmethod
    def create_reminder(user_id, reminder_data):
        """Create a new reminder"""
        reminder = {
            "user_id": ObjectId(user_id),
            "title": reminder_data.get("title", ""),
            "description": reminder_data.get("description", ""),
            "datetime": reminder_data.get("datetime", datetime.now()),
            "type": reminder_data.get("type", "workout"),  # workout, water, meal, etc.
            "is_recurring": reminder_data.get("is_recurring", False),
            "recurring_pattern": reminder_data.get("recurring_pattern", None),  # daily, weekly, etc.
            "is_active": reminder_data.get("is_active", True),
            "created_at": datetime.now()
        }
        
        result = mongo.db.reminders.insert_one(reminder)
        return str(result.inserted_id)
    
    @staticmethod
    def get_reminders(user_id):
        """Get all reminders for a user"""
        reminders = mongo.db.reminders.find({"user_id": ObjectId(user_id)}).sort("datetime", 1)
        return list(reminders)
    
    @staticmethod
    def get_reminder(reminder_id):
        """Get a specific reminder"""
        return mongo.db.reminders.find_one({"_id": ObjectId(reminder_id)})
    
    @staticmethod
    def update_reminder(reminder_id, reminder_data):
        """Update a reminder"""
        update_data = {
            "title": reminder_data.get("title"),
            "description": reminder_data.get("description"),
            "datetime": reminder_data.get("datetime"),
            "type": reminder_data.get("type"),
            "is_recurring": reminder_data.get("is_recurring"),
            "recurring_pattern": reminder_data.get("recurring_pattern"),
            "is_active": reminder_data.get("is_active"),
            "updated_at": datetime.now()
        }
        
        result = mongo.db.reminders.update_one(
            {"_id": ObjectId(reminder_id)},
            {"$set": update_data}
        )
        
        return result.modified_count > 0
    
    @staticmethod
    def delete_reminder(reminder_id):
        """Delete a reminder"""
        result = mongo.db.reminders.delete_one({"_id": ObjectId(reminder_id)})
        return result.deleted_count > 0