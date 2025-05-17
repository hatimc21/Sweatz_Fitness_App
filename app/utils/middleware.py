# app/utils/middleware.py
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
        
        try:
            # Check if maintenance mode is enabled - with timeout
            settings = mongo.db.settings.find_one({'_id': 'app_settings'}, max_time_ms=1000)
            if settings and settings.get('maintenance_mode', False):
                # Allow access for admins
                if current_user.is_authenticated and hasattr(current_user, 'is_admin') and current_user.is_admin:
                    return None
                
                # Redirect non-admins to maintenance page
                if request.endpoint != 'maintenance':  # Prevent redirect loop
                    flash('The site is currently in maintenance mode. Please try again later.', 'warning')
                    return redirect(url_for('maintenance'))
        except Exception as e:
            # Log error but don't let it block the request
            app.logger.error(f"Error checking maintenance mode: {str(e)}")
            # Assume system is not in maintenance mode if there's an error
        
        return None