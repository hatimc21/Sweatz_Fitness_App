from app import create_app
from app.utils.db_init import init_db
import sys

app = create_app()

if __name__ == '__main__':
    with app.app_context():
        try:
            init_db()
            print("Database initialization complete, starting server...")
        except Exception as e:
            print(f"Error initializing database: {e}")
            print("Continuing with server startup anyway...")
    
    try:
        app.run(debug=True, host='0.0.0.0')
    except Exception as e:
        print(f"Error starting server: {e}")
        sys.exit(1)