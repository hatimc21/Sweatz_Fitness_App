# app/api/auth.py
from flask import Blueprint, request, jsonify, render_template, redirect, url_for, flash, current_app
from flask_login import login_user, logout_user, login_required, current_user
from app.models.user import User
from app import mongo
import jwt
import datetime

# Define the blueprint
auth_bp = Blueprint('auth', __name__)

# Generate JWT token
def generate_jwt_token(user_id, expires_delta=None):
    """Generate a JWT token for API access"""
    if expires_delta is None:
        expires_delta = datetime.timedelta(days=30)  # Default to 30 days for mobile
    
    payload = {
        'exp': datetime.datetime.utcnow() + expires_delta,
        'iat': datetime.datetime.utcnow(),
        'sub': user_id
    }
    
    return jwt.encode(
        payload,
        current_app.config['JWT_SECRET_KEY'],
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
            token = generate_jwt_token(user.id)
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

# Mobile API endpoints
@auth_bp.route('/api/login', methods=['POST'])
def api_login():
    """Login for mobile clients"""
    try:
        data = request.get_json()
        
        # Validate input
        if not data or 'email' not in data or 'password' not in data:
            return jsonify({"error": "Email and password required"}), 400
        
        # Check if user exists
        user = User.get_by_email(data.get('email'))
        if not user or not user.verify_password(data.get('password')):
            return jsonify({"error": "Invalid credentials"}), 401
        
        # Update last login time
        user.update_last_login()
        
        # Generate JWT token
        token = generate_jwt_token(user.id)
        
        return jsonify({
            "success": True,
            "token": token,
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "subscription_tier": user.subscription_tier,
                "is_admin": user.is_admin
            }
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Error during API login: {str(e)}")
        return jsonify({"error": "Login failed due to server error"}), 500

@auth_bp.route('/api/refresh-token', methods=['POST'])
def refresh_token():
    """Refresh JWT token"""
    try:
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return jsonify({"error": "Authorization header is missing"}), 401
            
        if auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
        else:
            token = auth_header
            
        try:
            # Decode the token
            payload = jwt.decode(
                token,
                current_app.config['JWT_SECRET_KEY'],
                algorithms=['HS256']
            )
            
            user_id = payload['sub']
            
            # Check if user exists
            user = User.get_by_id(user_id)
            if not user:
                return jsonify({"error": "User not found"}), 401
                
            # Generate new token
            new_token = generate_jwt_token(user.id)
            
            return jsonify({
                "success": True,
                "token": new_token
            }), 200
            
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token has expired"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"error": "Invalid token"}), 401
            
    except Exception as e:
        current_app.logger.error(f"Error refreshing token: {str(e)}")
        return jsonify({"error": "Token refresh failed due to server error"}), 500

@auth_bp.route('/api/register', methods=['POST'])
def api_register():
    """Register a new user through API"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['username', 'email', 'password']
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing required field: {field}"}), 400
        
        # Check if user already exists
        if User.get_by_email(data.get('email')):
            return jsonify({"error": "Email already registered"}), 409
            
        if User.get_by_username(data.get('username')):
            return jsonify({"error": "Username already taken"}), 409
        
        # Create new user
        new_user = User.create(
            username=data.get('username'),
            email=data.get('email'),
            password=data.get('password'),
            first_name=data.get('first_name', ''),
            last_name=data.get('last_name', '')
        )
        
        # Generate JWT token
        token = generate_jwt_token(new_user.id)
        
        return jsonify({
            "success": True,
            "message": "Registration successful",
            "token": token,
            "user": {
                "id": new_user.id,
                "username": new_user.username,
                "email": new_user.email,
                "first_name": new_user.first_name,
                "last_name": new_user.last_name,
                "subscription_tier": new_user.subscription_tier
            }
        }), 201
        
    except Exception as e:
        current_app.logger.error(f"Error during API registration: {str(e)}")
        return jsonify({"error": "Registration failed due to server error"}), 500