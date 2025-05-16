from flask import Blueprint, request, jsonify, render_template, redirect, url_for, flash, current_app
from flask_login import login_user, logout_user, login_required, current_user
from app.models.user import User
from app import mongo
import jwt
import datetime

auth_bp = Blueprint('auth', __name__)

# Generate JWT token
def generate_token(user):
    payload = {
        'exp': datetime.datetime.utcnow() + datetime.timedelta(days=1),
        'iat': datetime.datetime.utcnow(),
        'sub': user.id
    }
    return jwt.encode(
        payload,
        current_app.config.get('JWT_SECRET_KEY'),
        algorithm='HS256'
    )

# Web routes for templates (for testing the API)
@auth_bp.route('/register', methods=['GET'])
def register_page():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return render_template('auth/register.html')

@auth_bp.route('/login', methods=['GET'])
def login_page():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return render_template('auth/login.html')

# API Routes for authentication
@auth_bp.route('/register', methods=['POST'])
def register():
    # Get data from request
    data = request.get_json() if request.is_json else request.form
    
    # Check if user already exists
    if User.get_by_email(data.get('email')):
        if request.is_json:
            return jsonify({'error': 'Email already registered'}), 400
        flash('Email already registered', 'danger')
        return redirect(url_for('auth.register_page'))
    
    if User.get_by_username(data.get('username')):
        if request.is_json:
            return jsonify({'error': 'Username already taken'}), 400
        flash('Username already taken', 'danger')
        return redirect(url_for('auth.register_page'))
    
    # Create new user
    try:
        new_user = User.create(
            username=data.get('username'),
            email=data.get('email'),
            password=data.get('password'),
            first_name=data.get('first_name', ''),
            last_name=data.get('last_name', '')
        )
        
        if request.is_json:
            return jsonify({
                'message': 'Registration successful',
                'user': {
                    'id': new_user.id,
                    'username': new_user.username,
                    'email': new_user.email
                }
            }), 201
        
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('auth.login_page'))
    except Exception as e:
        current_app.logger.error(f"Error registering user: {str(e)}")
        if request.is_json:
            return jsonify({'error': 'Registration failed'}), 500
        flash('Registration failed. Please try again.', 'danger')
        return redirect(url_for('auth.register_page'))

@auth_bp.route('/login', methods=['POST'])
def login():
    try:
        # Get data from request
        data = request.get_json() if request.is_json else request.form
        
        # Check if user exists
        user = User.get_by_email(data.get('email'))
        if not user or not user.verify_password(data.get('password')):
            if request.is_json:
                return jsonify({'error': 'Invalid credentials'}), 401
            flash('Invalid email or password', 'danger')
            return redirect(url_for('auth.login_page'))
        
        # Update last login time
        user.update_last_login()
        
        # Log in the user for session-based auth
        login_user(user)
        
        if request.is_json:
            # Generate JWT token for API access
            token = generate_token(user)
            return jsonify({
                'message': 'Login successful',
                'token': token,
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'subscription_tier': user.subscription_tier
                }
            })
        
        # For form submission, redirect to dashboard
        next_page = request.args.get('next')
        if next_page and next_page.startswith('/'):  # Only allow relative URLs
            return redirect(next_page)
        return redirect(url_for('dashboard'))
        
    except Exception as e:
        current_app.logger.error(f"Error during login: {str(e)}")
        if request.is_json:
            return jsonify({'error': 'Login failed due to server error'}), 500
        flash('Login failed due to server error. Please try again.', 'danger')
        return redirect(url_for('auth.login_page'))

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    
    if request.is_json:
        return jsonify({'message': 'Logged out successfully'})
    
    flash('You have been logged out', 'info')
    return redirect(url_for('auth.login_page'))