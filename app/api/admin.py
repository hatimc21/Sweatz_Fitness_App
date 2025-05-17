from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify, current_app, Response
from flask_login import login_required, current_user
from bson import ObjectId, json_util
from functools import wraps
from app import mongo
from datetime import datetime, timedelta
from app.models.user import User
import pymongo
import json
import csv
from io import StringIO

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

# Admin access decorator
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash('You need administrative privileges to access this page.', 'danger')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

# Dashboard
@admin_bp.route('/')
@login_required
@admin_required
def dashboard():
    # Overview statistics
    stats = {
        'total_users': mongo.db.users.count_documents({}),
        'active_users': mongo.db.users.count_documents({'is_active': True}),
        'total_workouts': mongo.db.workouts.count_documents({}),
        'total_exercises': mongo.db.exercises.count_documents({})
    }
    
    # New users in the last 7 days
    week_ago = datetime.utcnow() - timedelta(days=7)
    stats['new_users_week'] = mongo.db.users.count_documents({'created_at': {'$gte': week_ago}})
    
    # Get subscription distribution
    subscription_pipeline = [
        {'$group': {'_id': '$subscription_tier', 'count': {'$sum': 1}}},
        {'$sort': {'count': -1}}
    ]
    subscription_stats = list(mongo.db.users.aggregate(subscription_pipeline))
    
    # Recent user registrations
    recent_users = list(mongo.db.users.find().sort('created_at', pymongo.DESCENDING).limit(5))
    
    # Convert ObjectId to string for serialization
    for user in recent_users:
        user['_id'] = str(user['_id'])
    
    return render_template('admin/dashboard.html', 
                           stats=stats, 
                           subscription_stats=subscription_stats,
                           recent_users=recent_users,
                           active_tab='dashboard')

# User Management
@admin_bp.route('/users')
@login_required
@admin_required
def users():
    page = int(request.args.get('page', 1))
    per_page = 20
    skip = (page - 1) * per_page
    
    # Apply filters if provided
    filters = {}
    if request.args.get('subscription'):
        filters['subscription_tier'] = request.args.get('subscription')
    if request.args.get('status'):
        filters['is_active'] = (request.args.get('status') == 'active')
    
    # Get total count for pagination
    total_users = mongo.db.users.count_documents(filters)
    total_pages = (total_users + per_page - 1) // per_page
    
    # Get users with pagination
    users_data = list(mongo.db.users.find(filters).sort('created_at', pymongo.DESCENDING)
                     .skip(skip).limit(per_page))
    
    # Convert ObjectId to string for serialization
    for user in users_data:
        user['_id'] = str(user['_id'])
    
    return render_template('admin/users.html', 
                           users=users_data,
                           page=page,
                           total_pages=total_pages,
                           total_users=total_users,
                           active_tab='users')

# User Detail
@admin_bp.route('/users/<user_id>')
@login_required
@admin_required
def user_detail(user_id):
    try:
        user_data = mongo.db.users.find_one({'_id': ObjectId(user_id)})
        if not user_data:
            flash('User not found', 'warning')
            return redirect(url_for('admin.users'))
        
        user_data['_id'] = str(user_data['_id'])
        
        # Get user's workouts
        workouts = list(mongo.db.workouts.find({'user_id': user_id}).sort('date', pymongo.DESCENDING).limit(10))
        for workout in workouts:
            workout['_id'] = str(workout['_id'])
        
        # Get user's body logs
        body_logs = list(mongo.db.body_logs.find({'user_id': user_id}).sort('date', pymongo.DESCENDING).limit(10))
        for log in body_logs:
            log['_id'] = str(log['_id'])
        
        return render_template('admin/user_detail.html', 
                               user=user_data,
                               workouts=workouts,
                               body_logs=body_logs,
                               active_tab='users')
    except Exception as e:
        current_app.logger.error(f"Error fetching user details: {str(e)}")
        flash('Error fetching user details', 'danger')
        return redirect(url_for('admin.users'))

# Update user
@admin_bp.route('/users/<user_id>/update', methods=['POST'])
@login_required
@admin_required
def update_user(user_id):
    try:
        # Get form data
        data = request.form
        
        # Prepare update data
        update_data = {
            'first_name': data.get('first_name'),
            'last_name': data.get('last_name'),
            'is_active': data.get('is_active') == 'true',
            'subscription_tier': data.get('subscription_tier'),
            'role': data.get('role')
        }
        
        # Update user
        result = mongo.db.users.update_one(
            {'_id': ObjectId(user_id)},
            {'$set': update_data}
        )
        
        if result.modified_count > 0:
            flash('User updated successfully', 'success')
        else:
            flash('No changes were made', 'info')
        
        return redirect(url_for('admin.user_detail', user_id=user_id))
    except Exception as e:
        current_app.logger.error(f"Error updating user: {str(e)}")
        flash('Error updating user', 'danger')
        return redirect(url_for('admin.user_detail', user_id=user_id))

# Exercise Management
@admin_bp.route('/exercises')
@login_required
@admin_required
def exercises():
    page = int(request.args.get('page', 1))
    per_page = 20
    skip = (page - 1) * per_page
    
    # Apply filters if provided
    filters = {}
    
    if request.args.get('muscle_group'):
        filters['muscle_group'] = request.args.get('muscle_group')
    
    if request.args.get('difficulty'):
        filters['difficulty'] = request.args.get('difficulty')
    
    if request.args.get('equipment'):
        filters['equipment'] = request.args.get('equipment')
    
    if request.args.get('search'):
        filters['name'] = {'$regex': request.args.get('search'), '$options': 'i'}
    
    # Get total count for pagination
    total_exercises = mongo.db.exercises.count_documents(filters)
    total_pages = (total_exercises + per_page - 1) // per_page
    
    # Get exercises with pagination
    exercises_data = list(mongo.db.exercises.find(filters).sort('name', pymongo.ASCENDING)
                         .skip(skip).limit(per_page))
    
    # Convert ObjectId to string for serialization
    for exercise in exercises_data:
        exercise['_id'] = str(exercise['_id'])
    
    # Get all unique muscle groups for filtering
    muscle_groups = mongo.db.exercises.distinct('muscle_group')
    
    # Get all unique equipment types for filtering
    equipment_pipeline = [
        {"$unwind": "$equipment"},
        {"$group": {"_id": "$equipment"}},
        {"$sort": {"_id": 1}}
    ]
    equipment_list = [item['_id'] for item in mongo.db.exercises.aggregate(equipment_pipeline)]
    
    return render_template('admin/exercises.html', 
                           exercises=exercises_data,
                           muscle_groups=muscle_groups,
                           equipment_list=equipment_list,
                           page=page,
                           total_pages=total_pages,
                           total_exercises=total_exercises,
                           active_tab='exercises')

# Add exercise
@admin_bp.route('/exercises/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_exercise_route():
    if request.method == 'POST':
        try:
            # Get form data
            data = request.form
            
            # Process equipment - combine checkboxes and other equipment field
            equipment = []
            if 'equipment_json' in data and data['equipment_json']:
                try:
                    equipment = json.loads(data['equipment_json'])
                except:
                    # Fallback to processing checkboxes directly
                    equipment = request.form.getlist('equipment')
            
            # Prepare exercise data
            exercise_data = {
                'name': data.get('name'),
                'description': data.get('description'),
                'muscle_group': data.get('muscle_group'),
                'difficulty': data.get('difficulty'),
                'instruction': data.get('instruction'),
                'video_url': data.get('video_url'),
                'equipment': equipment,
                'tips': data.get('tips', ''),
                'created_at': datetime.utcnow(),
                'created_by': str(current_user.id)
            }
            
            # Insert exercise
            result = mongo.db.exercises.insert_one(exercise_data)
            
            if result.inserted_id:
                flash('Exercise added successfully', 'success')
                return redirect(url_for('admin.exercises'))
            else:
                flash('Error adding exercise', 'danger')
        except Exception as e:
            current_app.logger.error(f"Error adding exercise: {str(e)}")
            flash(f'Error adding exercise: {str(e)}', 'danger')
        
        return redirect(url_for('admin.add_exercise_route'))
    
    # GET request - show form
    return render_template('admin/exercise_form.html', 
                           exercise=None,
                           active_tab='exercises')

# Edit exercise
@admin_bp.route('/exercises/edit/<exercise_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_exercise(exercise_id):
    try:
        exercise = mongo.db.exercises.find_one({'_id': ObjectId(exercise_id)})
        if not exercise:
            flash('Exercise not found', 'warning')
            return redirect(url_for('admin.exercises'))
        
        if request.method == 'POST':
            # Get form data
            data = request.form
            
            # Process equipment - combine checkboxes and other equipment field
            equipment = []
            if 'equipment_json' in data and data['equipment_json']:
                try:
                    equipment = json.loads(data['equipment_json'])
                except:
                    # Fallback to processing checkboxes directly
                    equipment = request.form.getlist('equipment')
            
            # Prepare exercise data
            update_data = {
                'name': data.get('name'),
                'description': data.get('description'),
                'muscle_group': data.get('muscle_group'),
                'difficulty': data.get('difficulty'),
                'instruction': data.get('instruction'),
                'video_url': data.get('video_url'),
                'equipment': equipment,
                'tips': data.get('tips', ''),
                'updated_at': datetime.utcnow(),
                'updated_by': str(current_user.id)
            }
            
            # Update exercise
            result = mongo.db.exercises.update_one(
                {'_id': ObjectId(exercise_id)},
                {'$set': update_data}
            )
            
            if result.modified_count > 0:
                flash('Exercise updated successfully', 'success')
            else:
                flash('No changes were made', 'info')
            
            return redirect(url_for('admin.exercises'))
        
        # Convert ObjectId to string for template
        exercise['_id'] = str(exercise['_id'])
        
        # GET request - show form
        return render_template('admin/exercise_form.html', 
                              exercise=exercise,
                              active_tab='exercises')
    except Exception as e:
        current_app.logger.error(f"Error editing exercise: {str(e)}")
        flash(f'Error editing exercise: {str(e)}', 'danger')
        return redirect(url_for('admin.exercises'))

# Delete exercise
@admin_bp.route('/exercises/delete/<exercise_id>')
@login_required
@admin_required
def delete_exercise(exercise_id):
    try:
        result = mongo.db.exercises.delete_one({'_id': ObjectId(exercise_id)})
        
        if result.deleted_count > 0:
            flash('Exercise deleted successfully', 'success')
        else:
            flash('Exercise not found', 'warning')
        
        return redirect(url_for('admin.exercises'))
    except Exception as e:
        current_app.logger.error(f"Error deleting exercise: {str(e)}")
        flash(f'Error deleting exercise: {str(e)}', 'danger')
        return redirect(url_for('admin.exercises'))

# Export exercises
@admin_bp.route('/exercises/export')
@login_required
@admin_required
def export_exercises():
    """Export exercises to CSV"""
    try:
        # Apply filters if provided
        filters = {}
        
        if request.args.get('muscle_group'):
            filters['muscle_group'] = request.args.get('muscle_group')
        
        if request.args.get('difficulty'):
            filters['difficulty'] = request.args.get('difficulty')
        
        if request.args.get('equipment'):
            filters['equipment'] = request.args.get('equipment')
        
        if request.args.get('search'):
            filters['name'] = {'$regex': request.args.get('search'), '$options': 'i'}
        
        # Get all exercises matching the filters
        exercises = list(mongo.db.exercises.find(filters).sort('name', pymongo.ASCENDING))
        
        # Create CSV
        output = StringIO()
        writer = csv.writer(output)
        
        # Write header row
        writer.writerow(['ID', 'Name', 'Muscle Group', 'Difficulty', 'Equipment', 'Description', 'Instructions', 'Video URL', 'Created At'])
        
        # Write data rows
        for exercise in exercises:
            equipment_str = ', '.join(exercise.get('equipment', [])) if exercise.get('equipment') else ''
            
            writer.writerow([
                str(exercise['_id']),
                exercise.get('name', ''),
                exercise.get('muscle_group', ''),
                exercise.get('difficulty', ''),
                equipment_str,
                exercise.get('description', ''),
                exercise.get('instruction', '').replace('\n', ' ') if exercise.get('instruction') else '',
                exercise.get('video_url', ''),
                exercise.get('created_at', '').strftime('%Y-%m-%d %H:%M:%S') if exercise.get('created_at') else ''
            ])
        
        # Prepare response
        output.seek(0)
        return Response(
            output.getvalue(),
            mimetype="text/csv",
            headers={"Content-disposition": "attachment; filename=sweatz_exercises.csv"}
        )
        
    except Exception as e:
        current_app.logger.error(f"Error exporting exercises: {str(e)}")
        flash(f"Error exporting exercises: {str(e)}", 'danger')
        return redirect(url_for('admin.exercises'))

# API endpoint to get exercise details
@admin_bp.route('/api/exercises/<exercise_id>', methods=['GET'])
@login_required
@admin_required
def get_exercise_api(exercise_id):
    """API endpoint to get exercise details"""
    try:
        exercise = mongo.db.exercises.find_one({'_id': ObjectId(exercise_id)})
        
        if not exercise:
            return jsonify({"error": "Exercise not found"}), 404
        
        # If the exercise has a created_by field, fetch the username
        if 'created_by' in exercise:
            try:
                creator = mongo.db.users.find_one({'_id': ObjectId(exercise['created_by'])})
                if creator:
                    exercise['created_by_username'] = creator.get('username', 'Unknown')
            except:
                exercise['created_by_username'] = 'Unknown'
        
        return jsonify({
            "success": True,
            "exercise": json.loads(json_util.dumps(exercise))
        })
        
    except Exception as e:
        current_app.logger.error(f"Error fetching exercise: {str(e)}")
        return jsonify({"error": f"Error: {str(e)}"}), 500

# API endpoint to delete an exercise
@admin_bp.route('/api/exercises/<exercise_id>', methods=['DELETE'])
@login_required
@admin_required
def delete_exercise_api(exercise_id):
    """API endpoint to delete an exercise"""
    try:
        result = mongo.db.exercises.delete_one({'_id': ObjectId(exercise_id)})
        
        if result.deleted_count == 0:
            return jsonify({"error": "Exercise not found"}), 404
        
        return jsonify({
            "success": True,
            "message": "Exercise deleted successfully"
        })
        
    except Exception as e:
        current_app.logger.error(f"Error deleting exercise: {str(e)}")
        return jsonify({"error": f"Error: {str(e)}"}), 500

# API endpoint to delete multiple exercises
@admin_bp.route('/api/exercises/bulk-delete', methods=['POST'])
@login_required
@admin_required
def bulk_delete_exercises():
    """API endpoint to delete multiple exercises"""
    try:
        data = request.get_json()
        
        if not data or 'exercise_ids' not in data or not isinstance(data['exercise_ids'], list):
            return jsonify({"error": "Invalid request data"}), 400
        
        # Convert string IDs to ObjectId
        object_ids = [ObjectId(id) for id in data['exercise_ids']]
        
        result = mongo.db.exercises.delete_many({'_id': {'$in': object_ids}})
        
        return jsonify({
            "success": True,
            "message": f"{result.deleted_count} exercises deleted successfully"
        })
        
    except Exception as e:
        current_app.logger.error(f"Error bulk deleting exercises: {str(e)}")
        return jsonify({"error": f"Error: {str(e)}"}), 500

# System settings
@admin_bp.route('/settings')
@login_required
@admin_required
def settings():
    """Render the system settings page"""
    # Get current settings
    settings_data = mongo.db.settings.find_one({'_id': 'app_settings'})
    if not settings_data:
        # Create default settings if they don't exist
        settings_data = {
            '_id': 'app_settings',
            'maintenance_mode': False,
            'allow_registrations': True,
            'default_subscription': 'free',
            'app_version': '1.0.0',
            'last_updated': datetime.utcnow()
        }
        mongo.db.settings.insert_one(settings_data)
    
    return render_template('admin/settings.html', 
                           settings=settings_data,
                           active_tab='settings')

# Update settings
@admin_bp.route('/settings/update', methods=['POST'])
@login_required
@admin_required
def update_settings():
    """Update system settings"""
    try:
        # Get form data
        data = request.form
        
        # Prepare settings data
        settings_data = {
            'maintenance_mode': data.get('maintenance_mode') == 'true',
            'allow_registrations': data.get('allow_registrations') == 'true',
            'default_subscription': data.get('default_subscription'),
            'app_version': data.get('app_version'),
            'last_updated': datetime.utcnow(),
            'updated_by': str(current_user.id)
        }
        
        # Update settings
        result = mongo.db.settings.update_one(
            {'_id': 'app_settings'},
            {'$set': settings_data},
            upsert=True
        )
        
        flash('Settings updated successfully', 'success')
        return redirect(url_for('admin.settings'))
    except Exception as e:
        current_app.logger.error(f"Error updating settings: {str(e)}")
        flash('Error updating settings', 'danger')
        return redirect(url_for('admin.settings'))

# API endpoint for chart data
@admin_bp.route('/api/stats/users')
@login_required
@admin_required
def user_stats_api():
    """API endpoint for user statistics chart data"""
    try:
        # Get user signups by date for the last 30 days
        days = 30
        start_date = datetime.utcnow() - timedelta(days=days)
        
        pipeline = [
            {'$match': {'created_at': {'$gte': start_date}}},
            {'$group': {
                '_id': {'$dateToString': {'format': '%Y-%m-%d', 'date': '$created_at'}},
                'count': {'$sum': 1}
            }},
            {'$sort': {'_id': 1}}
        ]
        
        results = list(mongo.db.users.aggregate(pipeline))
        
        # Fill in missing dates
        date_counts = {r['_id']: r['count'] for r in results}
        all_dates = []
        
        for i in range(days):
            date = (start_date + timedelta(days=i)).strftime('%Y-%m-%d')
            all_dates.append({
                'date': date,
                'count': date_counts.get(date, 0)
            })
        
        return jsonify(all_dates)
    except Exception as e:
        current_app.logger.error(f"Error fetching user stats: {str(e)}")
        return jsonify({'error': 'Error fetching user stats'}), 500