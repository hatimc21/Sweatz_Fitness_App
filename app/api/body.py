# app/api/body.py
from flask import Blueprint, request, jsonify, current_app
from flask_login import login_required, current_user
from bson import ObjectId, json_util
from app.models.body import Body
from datetime import datetime
import json

body_bp = Blueprint('body', __name__, url_prefix='/api/body')

@body_bp.route('/weight', methods=['POST'])
@login_required
def log_weight():
    """Log a weight entry"""
    try:
        data = request.get_json()
        
        # Validate required fields
        if 'weight' not in data or not isinstance(data['weight'], (int, float)) or data['weight'] <= 0:
            return jsonify({"error": "Valid weight required"}), 400
        
        # Parse date if provided
        if 'date' in data and isinstance(data['date'], str):
            try:
                data['date'] = datetime.fromisoformat(data['date'].replace('Z', '+00:00'))
            except ValueError:
                return jsonify({"error": "Invalid date format"}), 400
        
        entry_id = Body.log_weight(current_user.id, data)
        
        return jsonify({
            "success": True,
            "message": "Weight logged successfully",
            "entry_id": entry_id
        }), 201
        
    except Exception as e:
        current_app.logger.error(f"Error logging weight: {str(e)}")
        return jsonify({"error": "Failed to log weight"}), 500

@body_bp.route('/weight', methods=['GET'])
@login_required
def get_weight_history():
    """Get weight history"""
    try:
        # Parse query parameters
        start_date_str = request.args.get('start_date')
        end_date_str = request.args.get('end_date')
        limit = request.args.get('limit', 30, type=int)
        
        start_date = None
        end_date = None
        
        # Parse start date if provided
        if start_date_str:
            try:
                start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
            except ValueError:
                return jsonify({"error": "Invalid start_date format. Use YYYY-MM-DD"}), 400
        
        # Parse end date if provided
        if end_date_str:
            try:
                end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
                # Set to end of day
                end_date = end_date.replace(hour=23, minute=59, second=59)
            except ValueError:
                return jsonify({"error": "Invalid end_date format. Use YYYY-MM-DD"}), 400
        
        weights = Body.get_weight_history(current_user.id, start_date, end_date, limit)
        
        return jsonify({
            "success": True,
            "weights": json.loads(json_util.dumps(weights))
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Error retrieving weight history: {str(e)}")
        return jsonify({"error": "Failed to retrieve weight history"}), 500

@body_bp.route('/measurements', methods=['POST'])
@login_required
def log_measurements():
    """Log body measurements"""
    try:
        data = request.get_json()
        
        # Validate that at least one measurement is provided
        measurement_fields = ['chest', 'waist', 'hips', 'arms', 'legs', 'neck', 'shoulders']
        if not any(field in data for field in measurement_fields):
            return jsonify({"error": "At least one measurement is required"}), 400
        
        # Parse date if provided
        if 'date' in data and isinstance(data['date'], str):
            try:
                data['date'] = datetime.fromisoformat(data['date'].replace('Z', '+00:00'))
            except ValueError:
                return jsonify({"error": "Invalid date format"}), 400
        
        entry_id = Body.log_measurements(current_user.id, data)
        
        return jsonify({
            "success": True,
            "message": "Measurements logged successfully",
            "entry_id": entry_id
        }), 201
        
    except Exception as e:
        current_app.logger.error(f"Error logging measurements: {str(e)}")
        return jsonify({"error": "Failed to log measurements"}), 500

@body_bp.route('/measurements', methods=['GET'])
@login_required
def get_measurements():
    """Get measurements history"""
    try:
        limit = request.args.get('limit', 10, type=int)
        
        measurements = Body.get_measurements_history(current_user.id, limit)
        
        return jsonify({
            "success": True,
            "measurements": json.loads(json_util.dumps(measurements))
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Error retrieving measurements: {str(e)}")
        return jsonify({"error": "Failed to retrieve measurements"}), 500

@body_bp.route('/composition', methods=['POST'])
@login_required
def log_composition():
    """Log body composition data"""
    try:
        data = request.get_json()
        
        # Validate that at least one composition metric is provided
        composition_fields = ['body_fat_percentage', 'muscle_mass', 'bone_mass', 
                             'water_percentage', 'bmi', 'bmr', 'visceral_fat']
        if not any(field in data for field in composition_fields):
            return jsonify({"error": "At least one composition metric is required"}), 400
        
        # Parse date if provided
        if 'date' in data and isinstance(data['date'], str):
            try:
                data['date'] = datetime.fromisoformat(data['date'].replace('Z', '+00:00'))
            except ValueError:
                return jsonify({"error": "Invalid date format"}), 400
        
        entry_id = Body.log_body_composition(current_user.id, data)
        
        return jsonify({
            "success": True,
            "message": "Body composition logged successfully",
            "entry_id": entry_id
        }), 201
        
    except Exception as e:
        current_app.logger.error(f"Error logging body composition: {str(e)}")
        return jsonify({"error": "Failed to log body composition"}), 500

@body_bp.route('/composition', methods=['GET'])
@login_required
def get_composition():
    """Get body composition history"""
    try:
        limit = request.args.get('limit', 10, type=int)
        
        compositions = Body.get_body_composition_history(current_user.id, limit)
        
        return jsonify({
            "success": True,
            "compositions": json.loads(json_util.dumps(compositions))
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Error retrieving body composition history: {str(e)}")
        return jsonify({"error": "Failed to retrieve body composition history"}), 500

@body_bp.route('/photos', methods=['POST'])
@login_required
def upload_photo():
    """Save a progress photo"""
    try:
        data = request.get_json()
        
        # Validate required fields
        if 'photo_url' not in data or not data['photo_url']:
            return jsonify({"error": "Photo URL is required"}), 400
        
        # Parse date if provided
        if 'date' in data and isinstance(data['date'], str):
            try:
                data['date'] = datetime.fromisoformat(data['date'].replace('Z', '+00:00'))
            except ValueError:
                return jsonify({"error": "Invalid date format"}), 400
        
        photo_id = Body.save_progress_photo(current_user.id, data)
        
        return jsonify({
            "success": True,
            "message": "Progress photo saved successfully",
            "photo_id": photo_id
        }), 201
        
    except Exception as e:
        current_app.logger.error(f"Error saving progress photo: {str(e)}")
        return jsonify({"error": "Failed to save progress photo"}), 500

@body_bp.route('/photos', methods=['GET'])
@login_required
def get_photos():
    """Get progress photos"""
    try:
        category = request.args.get('category')
        limit = request.args.get('limit', 20, type=int)
        
        photos = Body.get_progress_photos(current_user.id, category, limit)
        
        return jsonify({
            "success": True,
            "photos": json.loads(json_util.dumps(photos))
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Error retrieving progress photos: {str(e)}")
        return jsonify({"error": "Failed to retrieve progress photos"}), 500

@body_bp.route('/goals', methods=['GET', 'POST'])
@login_required
def manage_goals():
    """Get or set body goals"""
    try:
        # GET request - return current goals
        if request.method == 'GET':
            goals = Body.get_body_goal(current_user.id)
            
            return jsonify({
                "success": True,
                "goals": json.loads(json_util.dumps(goals)) if goals else None
            }), 200
        
        # POST request - set new goals
        elif request.method == 'POST':
            data = request.get_json()
            
            # Parse deadline if provided
            if 'deadline' in data and isinstance(data['deadline'], str):
                try:
                    data['deadline'] = datetime.fromisoformat(data['deadline'].replace('Z', '+00:00'))
                except ValueError:
                    return jsonify({"error": "Invalid deadline format"}), 400
            
            success = Body.set_body_goal(current_user.id, data)
            
            if success:
                return jsonify({
                    "success": True,
                    "message": "Body goals set successfully"
                }), 200
            else:
                return jsonify({"error": "Failed to set body goals"}), 500
                
    except Exception as e:
        current_app.logger.error(f"Error managing body goals: {str(e)}")
        return jsonify({"error": f"Operation failed: {str(e)}"}), 500