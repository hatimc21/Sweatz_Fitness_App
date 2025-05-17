from flask import Blueprint, request, jsonify, current_app
from flask_login import login_required, current_user
from bson import ObjectId, json_util
from app.models.nutrition import Nutrition
from datetime import datetime
import json

# Changed name to avoid blueprint name conflict
nutrition_bp = Blueprint('nutrition_api', __name__, url_prefix='/api/nutrition')

@nutrition_bp.route('/meals', methods=['POST'])
@login_required
def add_meal():
    """Add a new meal"""
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data.get('name'):
            return jsonify({"error": "Meal name is required"}), 400
        
        # Parse time if needed
        if 'time' in data and isinstance(data['time'], str):
            try:
                data['time'] = datetime.fromisoformat(data['time'].replace('Z', '+00:00'))
            except ValueError:
                return jsonify({"error": "Invalid time format"}), 400
        
        meal_id = Nutrition.create_meal(current_user.id, data)
        
        return jsonify({
            "success": True,
            "message": "Meal added successfully",
            "meal_id": meal_id
        }), 201
        
    except Exception as e:
        current_app.logger.error(f"Error adding meal: {str(e)}")
        return jsonify({"error": "Failed to add meal"}), 500

@nutrition_bp.route('/meals/<date>', methods=['GET'])
@login_required
def get_meals(date):
    """Get meals for a specific date"""
    try:
        # Parse date
        try:
            date_obj = datetime.strptime(date, '%Y-%m-%d').date()
        except ValueError:
            return jsonify({"error": "Invalid date format. Use YYYY-MM-DD"}), 400
        
        meals = Nutrition.get_meals_by_date(current_user.id, date_obj)
        
        return jsonify({
            "success": True,
            "meals": json.loads(json_util.dumps(meals))
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Error getting meals: {str(e)}")
        return jsonify({"error": "Failed to retrieve meals"}), 500

@nutrition_bp.route('/meals/<meal_id>', methods=['GET', 'PUT', 'DELETE'])
@login_required
def manage_meal(meal_id):
    """Get, update or delete a specific meal"""
    try:
        # Get meal
        meal = Nutrition.get_meal(meal_id)
        
        if not meal:
            return jsonify({"error": "Meal not found"}), 404
        
        # Check if meal belongs to current user
        if str(meal['user_id']) != current_user.id:
            return jsonify({"error": "Unauthorized access"}), 403
        
        # GET request - Return meal details
        if request.method == 'GET':
            return jsonify({
                "success": True,
                "meal": json.loads(json_util.dumps(meal))
            }), 200
        
        # PUT request - Update meal
        elif request.method == 'PUT':
            data = request.get_json()
            
            # Parse time if needed
            if 'time' in data and isinstance(data['time'], str):
                try:
                    data['time'] = datetime.fromisoformat(data['time'].replace('Z', '+00:00'))
                except ValueError:
                    return jsonify({"error": "Invalid time format"}), 400
            
            success = Nutrition.update_meal(meal_id, data)
            
            if success:
                return jsonify({
                    "success": True,
                    "message": "Meal updated successfully"
                }), 200
            else:
                return jsonify({"error": "Failed to update meal"}), 500
        
        # DELETE request - Delete meal
        elif request.method == 'DELETE':
            success = Nutrition.delete_meal(meal_id)
            
            if success:
                return jsonify({
                    "success": True,
                    "message": "Meal deleted successfully"
                }), 200
            else:
                return jsonify({"error": "Failed to delete meal"}), 500
                
    except Exception as e:
        current_app.logger.error(f"Error managing meal: {str(e)}")
        return jsonify({"error": f"Operation failed: {str(e)}"}), 500

@nutrition_bp.route('/water', methods=['POST'])
@login_required
def log_water():
    """Log water intake"""
    try:
        data = request.get_json()
        
        # Validate amount
        if 'amount' not in data or not isinstance(data['amount'], (int, float)) or data['amount'] <= 0:
            return jsonify({"error": "Valid amount required"}), 400
        
        # Parse time if needed
        if 'time' in data and isinstance(data['time'], str):
            try:
                data['time'] = datetime.fromisoformat(data['time'].replace('Z', '+00:00'))
            except ValueError:
                return jsonify({"error": "Invalid time format"}), 400
        
        intake_id = Nutrition.log_water_intake(current_user.id, data)
        
        return jsonify({
            "success": True,
            "message": "Water intake logged successfully",
            "intake_id": intake_id
        }), 201
        
    except Exception as e:
        current_app.logger.error(f"Error logging water intake: {str(e)}")
        return jsonify({"error": "Failed to log water intake"}), 500

@nutrition_bp.route('/water/<date>', methods=['GET'])
@login_required
def get_water(date):
    """Get water intake for a specific date"""
    try:
        # Parse date
        try:
            date_obj = datetime.strptime(date, '%Y-%m-%d').date()
        except ValueError:
            return jsonify({"error": "Invalid date format. Use YYYY-MM-DD"}), 400
        
        total_water = Nutrition.get_daily_water_intake(current_user.id, date_obj)
        
        return jsonify({
            "success": True,
            "date": date,
            "total_water": total_water
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Error getting water intake: {str(e)}")
        return jsonify({"error": "Failed to retrieve water intake"}), 500

@nutrition_bp.route('/goals', methods=['GET', 'POST'])
@login_required
def manage_goals():
    """Get or set nutrition goals"""
    try:
        # GET request - Return current goals
        if request.method == 'GET':
            goals = Nutrition.get_nutrition_goal(current_user.id)
            
            return jsonify({
                "success": True,
                "goals": json.loads(json_util.dumps(goals))
            }), 200
        
        # POST request - Set goals
        elif request.method == 'POST':
            data = request.get_json()
            
            # Validate inputs
            for key in ['calories', 'protein', 'carbs', 'fats', 'water']:
                if key in data and (not isinstance(data[key], (int, float)) or data[key] < 0):
                    return jsonify({"error": f"Invalid value for {key}"}), 400
            
            success = Nutrition.set_nutrition_goal(current_user.id, data)
            
            if success:
                return jsonify({
                    "success": True,
                    "message": "Nutrition goals updated successfully"
                }), 200
            else:
                return jsonify({"error": "Failed to update nutrition goals"}), 500
                
    except Exception as e:
        current_app.logger.error(f"Error managing nutrition goals: {str(e)}")
        return jsonify({"error": f"Operation failed: {str(e)}"}), 500

@nutrition_bp.route('/summary/<date>', methods=['GET'])
@login_required
def get_summary(date):
    """Get nutrition summary for a specific date"""
    try:
        # Parse date
        try:
            date_obj = datetime.strptime(date, '%Y-%m-%d').date()
        except ValueError:
            return jsonify({"error": "Invalid date format. Use YYYY-MM-DD"}), 400
        
        # Get data
        summary = Nutrition.get_daily_nutrition_summary(current_user.id, date_obj)
        water = Nutrition.get_daily_water_intake(current_user.id, date_obj)
        goals = Nutrition.get_nutrition_goal(current_user.id)
        
        # Calculate progress percentages
        progress = {
            "calories": round((summary['total_calories'] / goals['calories']) * 100) if goals['calories'] > 0 else 0,
            "protein": round((summary['total_protein'] / goals['protein']) * 100) if goals['protein'] > 0 else 0,
            "carbs": round((summary['total_carbs'] / goals['carbs']) * 100) if goals['carbs'] > 0 else 0,
            "fats": round((summary['total_fats'] / goals['fats']) * 100) if goals['fats'] > 0 else 0,
            "water": round((water / goals['water']) * 100) if goals['water'] > 0 else 0
        }
        
        return jsonify({
            "success": True,
            "date": date,
            "summary": json.loads(json_util.dumps(summary)),
            "water_intake": water,
            "goals": json.loads(json_util.dumps(goals)),
            "progress": progress
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Error getting nutrition summary: {str(e)}")
        return jsonify({"error": "Failed to retrieve nutrition summary"}), 500