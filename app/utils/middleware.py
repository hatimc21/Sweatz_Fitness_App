from flask import request, redirect, url_for, flash
from flask_login import current_user

def register_middleware(app, mongo):
    """Register middleware functions with the Flask app"""
    
    @app.before_request
    def check_maintenance_mode():
        """Check if the application is in maintenance mode"""
        # Skip for admin routes and static files
        if request.path.startswith('/admin') or request.path.startswith('/static'):
            return None
        
        # Check if maintenance mode is enabled
        settings = mongo.db.settings.find_one({'_id': 'app_settings'})
        if settings and settings.get('maintenance_mode', False):
            # Allow access for admins
            if current_user.is_authenticated and hasattr(current_user, 'is_admin') and current_user.is_admin:
                return None
            
            # Redirect non-admins to maintenance page
            if request.endpoint != 'maintenance':  # Prevent redirect loop
                flash('The site is currently in maintenance mode. Please try again later.', 'warning')
                return redirect(url_for('maintenance'))
        
        return None