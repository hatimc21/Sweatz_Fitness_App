from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify, current_app
from flask_login import login_required, current_user
from bson import ObjectId
from functools import wraps
from app import mongo
from datetime import datetime, timedelta
from app.models.user import User
import pymongo

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
    
    return render_template('admin/exercises.html', 
                           exercises=exercises_data,
                           muscle_groups=muscle_groups,
                           page=page,
                           total_pages=total_pages,
                           total_exercises=total_exercises,
                           active_tab='exercises')

# Add exercise
@admin_bp.route('/exercises/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_exercise():
    if request.method == 'POST':
        try:
            # Get form data
            data = request.form
            
            # Prepare exercise data
            exercise_data = {
                'name': data.get('name'),
                'description': data.get('description'),
                'muscle_group': data.get('muscle_group'),
                'difficulty': data.get('difficulty'),
                'instruction': data.get('instruction'),
                'video_url': data.get('video_url'),
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
            flash('Error adding exercise', 'danger')
        
        return redirect(url_for('admin.add_exercise'))
    
    # GET request - show form
    return render_template('admin/exercise_form.html', 
                           exercise=None,
                           active_tab='exercises')

# System settings
@admin_bp.route('/settings')
@login_required
@admin_required
def settings():
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
    
# Add these routes to the existing admin_bp

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
            
            # Prepare exercise data
            update_data = {
                'name': data.get('name'),
                'description': data.get('description'),
                'muscle_group': data.get('muscle_group'),
                'difficulty': data.get('difficulty'),
                'instruction': data.get('instruction'),
                'video_url': data.get('video_url'),
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
        flash('Error editing exercise', 'danger')
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
        flash('Error deleting exercise', 'danger')
        return redirect(url_for('admin.exercises'))