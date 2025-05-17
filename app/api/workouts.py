# app/api/workouts.py
from flask import Blueprint, request, jsonify, current_app
from flask_login import login_required, current_user
from bson import ObjectId, json_util
from app.models.workouts import Workout
from datetime import datetime, timedelta
import json

workouts_bp = Blueprint('workouts', __name__, url_prefix='/api/workouts')

@workouts_bp.route('/routines', methods=['POST'])
@login_required
def create_routine():
    """Create a workout routine"""
    try:
        data = request.get_json()
        
        # Validate required fields
        if 'name' not in data or not data['name']:
            return jsonify({"error": "Name is required"}), 400
        
        if 'days' not in data or not isinstance(data['days'], list):
            return jsonify({"error": "Days array is required"}), 400
        
        routine_id = Workout.create_routine(current_user.id, data)
        
        return jsonify({
            "success": True,
            "message": "Workout routine created successfully",
            "routine_id": routine_id
        }), 201
        
    except Exception as e:
        current_app.logger.error(f"Error creating workout routine: {str(e)}")
        return jsonify({"error": "Failed to create workout routine"}), 500

@workouts_bp.route('/routines', methods=['GET'])
@login_required
def get_routines():
    """Get workout routines"""
    try:
        include_public = request.args.get('include_public', 'true').lower() == 'true'
        
        routines = Workout.get_routines(current_user.id, include_public)
        
        return jsonify({
            "success": True,
            "routines": json.loads(json_util.dumps(routines))
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Error retrieving workout routines: {str(e)}")
        return jsonify({"error": "Failed to retrieve workout routines"}), 500

@workouts_bp.route('/routines/<routine_id>', methods=['GET'])
@login_required
def get_routine(routine_id):
    """Get a specific workout routine"""
    try:
        routine = Workout.get_routine(routine_id)
        
        if not routine:
            return jsonify({"error": "Routine not found"}), 404
        
        # Check if routine belongs to user or is public
        if str(routine['user_id']) != current_user.id and not routine.get('is_public', False):
            return jsonify({"error": "Unauthorized access"}), 403
        
        return jsonify({
            "success": True,
            "routine": json.loads(json_util.dumps(routine))
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Error retrieving workout routine: {str(e)}")
        return jsonify({"error": "Failed to retrieve workout routine"}), 500

@workouts_bp.route('/routines/<routine_id>', methods=['PUT'])
@login_required
def update_routine(routine_id):
    """Update a workout routine"""
    try:
        data = request.get_json()
        
        # Validate required fields
        if 'name' not in data or not data['name']:
            return jsonify({"error": "Name is required"}), 400
        
        if 'days' not in data or not isinstance(data['days'], list):
            return jsonify({"error": "Days array is required"}), 400
        
        success = Workout.update_routine(routine_id, current_user.id, data)
        
        if not success:
            return jsonify({"error": "Routine not found or you don't have permission to update it"}), 404
        
        return jsonify({
            "success": True,
            "message": "Workout routine updated successfully"
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Error updating workout routine: {str(e)}")
        return jsonify({"error": "Failed to update workout routine"}), 500

@workouts_bp.route('/routines/<routine_id>', methods=['DELETE'])
@login_required
def delete_routine(routine_id):
    """Delete a workout routine"""
    try:
        success = Workout.delete_routine(routine_id, current_user.id)
        
        if not success:
            return jsonify({"error": "Routine not found or you don't have permission to delete it"}), 404
        
        return jsonify({
            "success": True,
            "message": "Workout routine deleted successfully"
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Error deleting workout routine: {str(e)}")
        return jsonify({"error": "Failed to delete workout routine"}), 500

@workouts_bp.route('/schedule', methods=['POST'])
@login_required
def schedule_workout():
    """Schedule a workout"""
    try:
        data = request.get_json()
        
        # Validate required fields
        if 'date' not in data:
            return jsonify({"error": "Date is required"}), 400
        
        if 'title' not in data or not data['title']:
            return jsonify({"error": "Title is required"}), 400
        
        # Parse date if string
        if isinstance(data['date'], str):
            try:
                data['date'] = datetime.fromisoformat(data['date'].replace('Z', '+00:00'))
            except ValueError:
                return jsonify({"error": "Invalid date format"}), 400
        
        # Parse times if strings
        for time_field in ['start_time', 'end_time']:
            if time_field in data and isinstance(data[time_field], str):
                try:
                    data[time_field] = datetime.fromisoformat(data[time_field].replace('Z', '+00:00'))
                except ValueError:
                    return jsonify({"error": f"Invalid {time_field} format"}), 400
        
        workout_id = Workout.schedule_workout(current_user.id, data)
        
        return jsonify({
            "success": True,
            "message": "Workout scheduled successfully",
            "workout_id": workout_id
        }), 201
        
    except Exception as e:
        current_app.logger.error(f"Error scheduling workout: {str(e)}")
        return jsonify({"error": "Failed to schedule workout"}), 500

@workouts_bp.route('/schedule', methods=['GET'])
@login_required
def get_scheduled_workouts():
    """Get scheduled workouts for a date range"""
    try:
        start_date_str = request.args.get('start_date')
        end_date_str = request.args.get('end_date')
        
        start_date = None
        end_date = None
        
        # Parse start date
        if start_date_str:
            try:
                start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
            except ValueError:
                return jsonify({"error": "Invalid start_date format. Use YYYY-MM-DD"}), 400
        else:
            # Default to today
            start_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        
        # Parse end date
        if end_date_str:
            try:
                end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
                # Set to end of day
                end_date = end_date.replace(hour=23, minute=59, second=59)
            except ValueError:
                return jsonify({"error": "Invalid end_date format. Use YYYY-MM-DD"}), 400
        else:
            # Default to 30 days from start date
            end_date = start_date + timedelta(days=30)
            end_date = end_date.replace(hour=23, minute=59, second=59)
        
        workouts = Workout.get_scheduled_workouts(current_user.id, start_date, end_date)
        
        return jsonify({
            "success": True,
            "workouts": json.loads(json_util.dumps(workouts))
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Error retrieving scheduled workouts: {str(e)}")
        return jsonify({"error": "Failed to retrieve scheduled workouts"}), 500

@workouts_bp.route('/schedule/<workout_id>', methods=['PUT'])
@login_required
def update_scheduled_workout(workout_id):
    """Update a scheduled workout"""
    try:
        data = request.get_json()
        
        # Parse date if string
        if 'date' in data and isinstance(data['date'], str):
            try:
                data['date'] = datetime.fromisoformat(data['date'].replace('Z', '+00:00'))
            except ValueError:
                return jsonify({"error": "Invalid date format"}), 400
        
        # Parse times if strings
        for time_field in ['start_time', 'end_time']:
            if time_field in data and isinstance(data[time_field], str):
                try:
                    data[time_field] = datetime.fromisoformat(data[time_field].replace('Z', '+00:00'))
                except ValueError:
                    return jsonify({"error": f"Invalid {time_field} format"}), 400
        
        success = Workout.update_scheduled_workout(workout_id, current_user.id, data)
        
        if not success:
            return jsonify({"error": "Workout not found or you don't have permission to update it"}), 404
        
        return jsonify({
            "success": True,
            "message": "Scheduled workout updated successfully"
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Error updating scheduled workout: {str(e)}")
        return jsonify({"error": "Failed to update scheduled workout"}), 500

@workouts_bp.route('/schedule/<workout_id>', methods=['DELETE'])
@login_required
def delete_scheduled_workout(workout_id):
    """Delete a scheduled workout"""
    try:
        success = Workout.delete_scheduled_workout(workout_id, current_user.id)
        
        if not success:
            return jsonify({"error": "Workout not found or you don't have permission to delete it"}), 404
        
        return jsonify({
            "success": True,
            "message": "Scheduled workout deleted successfully"
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Error deleting scheduled workout: {str(e)}")
        return jsonify({"error": "Failed to delete scheduled workout"}), 500

@workouts_bp.route('/log', methods=['POST'])
@login_required
def log_workout():
    """Log a completed workout"""
    try:
        data = request.get_json()
        
        # Parse date if string
        if 'date' in data and isinstance(data['date'], str):
            try:
                data['date'] = datetime.fromisoformat(data['date'].replace('Z', '+00:00'))
            except ValueError:
                return jsonify({"error": "Invalid date format"}), 400
        
        # Validate exercise data
        if 'exercises' in data and not isinstance(data['exercises'], list):
            return jsonify({"error": "Exercises must be an array"}), 400
        
        workout_id = Workout.log_completed_workout(current_user.id, data)
        
        return jsonify({
            "success": True,
            "message": "Workout logged successfully",
            "workout_id": workout_id
        }), 201
        
    except Exception as e:
        current_app.logger.error(f"Error logging workout: {str(e)}")
        return jsonify({"error": "Failed to log workout"}), 500

@workouts_bp.route('/history', methods=['GET'])
@login_required
def get_workout_history():
    """Get workout history"""
    try:
        limit = int(request.args.get('limit', 10))
        
        workouts = Workout.get_workout_history(current_user.id, limit)
        
        return jsonify({
            "success": True,
            "workouts": json.loads(json_util.dumps(workouts))
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Error retrieving workout history: {str(e)}")
        return jsonify({"error": "Failed to retrieve workout history"}), 500

@workouts_bp.route('/exercises', methods=['GET'])
@login_required
def get_exercises():
    """Get exercises with optional filters"""
    try:
        filters = {}
        
        # Parse query parameters
        if request.args.get('muscle_group'):
            filters['muscle_group'] = request.args.get('muscle_group')
        
        if request.args.get('difficulty'):
            filters['difficulty'] = request.args.get('difficulty')
        
        if request.args.get('equipment'):
            filters['equipment'] = request.args.get('equipment').split(',')
        
        if request.args.get('search'):
            filters['search'] = request.args.get('search')
        
        limit = int(request.args.get('limit', 100))
        skip = int(request.args.get('skip', 0))
        
        exercises, total = Workout.get_exercises(filters, limit, skip)
        
        return jsonify({
            "success": True,
            "exercises": json.loads(json_util.dumps(exercises)),
            "total": total,
            "limit": limit,
            "skip": skip
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Error retrieving exercises: {str(e)}")
        return jsonify({"error": "Failed to retrieve exercises"}), 500

@workouts_bp.route('/exercise-categories', methods=['GET'])
@login_required
def get_exercise_categories():
    """Get all exercise categories/muscle groups"""
    try:
        categories = Workout.get_exercise_categories()
        
        return jsonify({
            "success": True,
            "categories": categories
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Error retrieving exercise categories: {str(e)}")
        return jsonify({"error": "Failed to retrieve exercise categories"}), 500

@workouts_bp.route('/equipment-types', methods=['GET'])
@login_required
def get_equipment_types():
    """Get all equipment types"""
    try:
        equipment = Workout.get_equipment_types()
        
        return jsonify({
            "success": True,
            "equipment": equipment
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Error retrieving equipment types: {str(e)}")
        return jsonify({"error": "Failed to retrieve equipment types"}), 500

@workouts_bp.route('/stats', methods=['GET'])
@login_required
def get_workout_stats():
    """Get workout statistics"""
    try:
        period = request.args.get('period', 'all')
        if period not in ['all', 'week', 'month', 'year']:
            return jsonify({"error": "Invalid period. Use 'all', 'week', 'month', or 'year'"}), 400
        
        stats = Workout.get_workout_stats(current_user.id, period)
        
        return jsonify({
            "success": True,
            "stats": json.loads(json_util.dumps(stats)),
            "period": period
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Error retrieving workout stats: {str(e)}")
        return jsonify({"error": "Failed to retrieve workout stats"}), 500