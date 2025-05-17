# app/__init__.py
from flask import Flask, render_template, flash
from flask_pymongo import PyMongo
from flask_login import LoginManager, login_required, current_user
from flask_cors import CORS
import os
import urllib.parse
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize extensions
mongo = PyMongo()
login_manager = LoginManager()
cors = CORS()

def create_app(config_name='default'):
    app = Flask(__name__)
    
    # Load config
    from app.config import config
    app.config.from_object(config[config_name])
    
    # Construct MongoDB URI with properly encoded credentials
    username = os.environ.get('MONGO_USERNAME')
    password = urllib.parse.quote_plus(os.environ.get('MONGO_PASSWORD', ''))
    cluster = os.environ.get('MONGO_CLUSTER')
    database = app.config.get('MONGO_DATABASE', 'sweatz_dev')
    
    # Add parameters to try fixing SSL issue
    app.config['MONGO_URI'] = f"mongodb+srv://{username}:{password}@{cluster}/{database}?retryWrites=true&w=majority&appName=Cluster0&ssl=true&tlsAllowInvalidCertificates=true"
    print(f"MongoDB URI constructed: mongodb+srv://{username}:****@{cluster}/{database}?retryWrites=true&w=majority&appName=Cluster0&ssl=true&tlsAllowInvalidCertificates=true")
    
    # Initialize extensions with app
    try:
        mongo.init_app(app)
        print("MongoDB connection successful!")
    except Exception as e:
        print(f"MongoDB connection error: {e}")
        print("App will run with limited functionality.")
    
    login_manager.init_app(app)
    cors.init_app(app)
    
    # Set up login view
    login_manager.login_view = 'auth.login_page'
    
    try:
        # Import user model for login manager
        from app.models.user import load_user
        
        # Register blueprints
        from app.api.auth import auth_bp
        app.register_blueprint(auth_bp)
        
        # Register admin blueprint
        from app.api.admin import admin_bp
        app.register_blueprint(admin_bp)
        
        # Register API blueprints
        from app.api.nutrition import nutrition_bp
        app.register_blueprint(nutrition_bp)
        
    except ImportError as e:
        print(f"Warning: Could not import modules: {e}")
    
    # A simple route to confirm the app is working
    @app.route('/')
    def index():
        return render_template('index.html')
    
    # Dashboard route (requires login)
    @app.route('/dashboard')
    @login_required
    def dashboard():
        context = {}
        
        # Add admin-specific data if user is admin
        if hasattr(current_user, 'is_admin') and current_user.is_admin:
            try:
                # Get user count for admin dashboard
                user_count = mongo.db.users.count_documents({})
                context['user_count'] = user_count
            except Exception as e:
                app.logger.error(f"Error fetching admin data: {e}")
        
        return render_template('dashboard.html', **context)
    
    # Add maintenance route
    @app.route('/maintenance')
    def maintenance():
        return render_template('maintenance.html')
    
    # Register middleware
    from app.utils.middleware import register_middleware
    register_middleware(app, mongo)
    
    # Error handler for 404
    @app.errorhandler(404)
    def page_not_found(e):
        flash('Page not found', 'warning')
        return render_template('404.html'), 404
    
    # Error handler for 500
    @app.errorhandler(500)
    def server_error(e):
        app.logger.error(f"Server error: {str(e)}")
        flash('An internal server error occurred', 'danger')
        return render_template('500.html'), 500
    

    # In the create_app function in app/__init__.py
    # Inside the try block where you register blueprints:

    from app.api.body import body_bp
    app.register_blueprint(body_bp)

    # In the create_app function in app/__init__.py
    # Inside the try block where you register blueprints:

    from app.api.workouts import workouts_bp
    app.register_blueprint(workouts_bp)
        
    return app