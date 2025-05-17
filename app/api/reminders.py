from flask import Blueprint, request, jsonify, current_app
from flask_login import login_required, current_user
from bson import ObjectId, json_util
from app.models.reminders import Reminder
from datetime import datetime
import json

reminders_bp = Blueprint('reminders_api', __name__, url_prefix='/api/reminders')

@reminders_bp.route('', methods=['GET'])
@login_required
def get_reminders():
    """Get all reminders for the current user"""
    try:
        reminders = Reminder.get_reminders(current_user.id)
        
        return jsonify({
            "success": True,
            "reminders": json.loads(json_util.dumps(reminders))
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Error retrieving reminders: {str(e)}")
        return jsonify({"error": "Failed to retrieve reminders"}), 500

@reminders_bp.route('', methods=['POST'])
@login_required
def create_reminder():
    """Create a new reminder"""
    try:
        data = request.get_json()
        
        # Validate required fields
        if 'title' not in data or not data['title']:
            return jsonify({"error": "Title is required"}), 400
        
        if 'datetime' not in data:
            return jsonify({"error": "Datetime is required"}), 400
        
        # Parse datetime if provided as string
        if isinstance(data['datetime'], str):
            try:
                data['datetime'] = datetime.fromisoformat(data['datetime'].replace('Z', '+00:00'))
            except ValueError:
                return jsonify({"error": "Invalid datetime format"}), 400
        
        reminder_id = Reminder.create_reminder(current_user.id, data)
        
        return jsonify({
            "success": True,
            "message": "Reminder created successfully",
            "reminder_id": reminder_id
        }), 201
        
    except Exception as e:
        current_app.logger.error(f"Error creating reminder: {str(e)}")
        return jsonify({"error": "Failed to create reminder"}), 500

@reminders_bp.route('/<reminder_id>', methods=['GET', 'PUT', 'DELETE'])
@login_required
def manage_reminder(reminder_id):
    """Get, update or delete a specific reminder"""
    try:
        # Get reminder
        reminder = Reminder.get_reminder(reminder_id)
        
        if not reminder:
            return jsonify({"error": "Reminder not found"}), 404
        
        # Check if reminder belongs to current user
        if str(reminder['user_id']) != current_user.id:
            return jsonify({"error": "Unauthorized access"}), 403
        
        # GET request - Return reminder details
        if request.method == 'GET':
            return jsonify({
                "success": True,
                "reminder": json.loads(json_util.dumps(reminder))
            }), 200
        
        # PUT request - Update reminder
        elif request.method == 'PUT':
            data = request.get_json()
            
            # Parse datetime if provided as string
            if 'datetime' in data and isinstance(data['datetime'], str):
                try:
                    data['datetime'] = datetime.fromisoformat(data['datetime'].replace('Z', '+00:00'))
                except ValueError:
                    return jsonify({"error": "Invalid datetime format"}), 400
            
            success = Reminder.update_reminder(reminder_id, data)
            
            if success:
                return jsonify({
                    "success": True,
                    "message": "Reminder updated successfully"
                }), 200
            else:
                return jsonify({"error": "Failed to update reminder"}), 500
        
        # DELETE request - Delete reminder
        elif request.method == 'DELETE':
            success = Reminder.delete_reminder(reminder_id)
            
            if success:
                return jsonify({
                    "success": True,
                    "message": "Reminder deleted successfully"
                }), 200
            else:
                return jsonify({"error": "Failed to delete reminder"}), 500
                
    except Exception as e:
        current_app.logger.error(f"Error managing reminder: {str(e)}")
        return jsonify({"error": f"Operation failed: {str(e)}"}), 500