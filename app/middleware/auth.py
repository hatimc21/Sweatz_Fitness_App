# app/middleware/auth.py
from functools import wraps
from flask import request, jsonify, current_app
import jwt
from app.models.user import User

def token_required(f):
    """Decorator for JWT protected API routes"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        # Check if token is in headers
        auth_header = request.headers.get('Authorization')
        if auth_header:
            if auth_header.startswith('Bearer '):
                token = auth_header.split(' ')[1]
            else:
                token = auth_header
        
        # Check if token is in query parameters (not recommended for production)
        if not token:
            token = request.args.get('token')
        
        if not token:
            return jsonify({"error": "Token is missing"}), 401
        
        try:
            # Decode token
            payload = jwt.decode(
                token,
                current_app.config['JWT_SECRET_KEY'],
                algorithms=['HS256']
            )
            
            user_id = payload['sub']
            
            # Get user from database
            user = User.get_by_id(user_id)
            if not user:
                return jsonify({"error": "User not found"}), 401
            
            # Check if user is active
            if not user.is_active:
                return jsonify({"error": "User account is disabled"}), 403
            
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token has expired"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"error": "Invalid token"}), 401
        
        # Pass the current user to the route function
        return f(user, *args, **kwargs)
    
    return decorated

def admin_token_required(f):
    """Decorator for admin-only API routes"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        # Check if token is in headers
        auth_header = request.headers.get('Authorization')
        if auth_header:
            if auth_header.startswith('Bearer '):
                token = auth_header.split(' ')[1]
            else:
                token = auth_header
        
        if not token:
            return jsonify({"error": "Token is missing"}), 401
        
        try:
            # Decode token
            payload = jwt.decode(
                token,
                current_app.config['JWT_SECRET_KEY'],
                algorithms=['HS256']
            )
            
            user_id = payload['sub']
            
            # Get user from database
            user = User.get_by_id(user_id)
            if not user:
                return jsonify({"error": "User not found"}), 401
            
            # Check if user is active and admin
            if not user.is_active:
                return jsonify({"error": "User account is disabled"}), 403
            
            if not user.is_admin:
                return jsonify({"error": "Admin privileges required"}), 403
            
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token has expired"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"error": "Invalid token"}), 401
        
        # Pass the current user to the route function
        return f(user, *args, **kwargs)
    
    return decorated