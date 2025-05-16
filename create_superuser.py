import os
import sys
import urllib.parse
from pymongo import MongoClient
from werkzeug.security import generate_password_hash
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def create_superuser(username, email, password, first_name="Admin", last_name="User"):
    """
    Create a superuser in the MongoDB database with admin privileges
    """
    # Connect to MongoDB
    mongo_username = os.environ.get('MONGO_USERNAME')
    mongo_password = urllib.parse.quote_plus(os.environ.get('MONGO_PASSWORD', ''))
    mongo_cluster = os.environ.get('MONGO_CLUSTER')
    mongo_database = os.environ.get('MONGO_DATABASE', 'sweatz_dev')
    
    uri = f"mongodb+srv://{mongo_username}:{mongo_password}@{mongo_cluster}/{mongo_database}?retryWrites=true&w=majority&appName=Cluster0"
    
    try:
        client = MongoClient(uri)
        db = client[mongo_database]
        
        # Check if user already exists
        existing_user = db.users.find_one({'$or': [{'username': username}, {'email': email}]})
        if existing_user:
            print(f"Error: User already exists with username '{username}' or email '{email}'")
            return False
        
        # Create superuser document
        superuser = {
            'username': username,
            'email': email,
            'password_hash': generate_password_hash(password),
            'first_name': first_name,
            'last_name': last_name,
            'created_at': datetime.utcnow(),
            'last_login': None,
            'is_active': True,
            'is_superuser': True,  # Special flag for admin privileges
            'subscription_tier': 'admin',  # Special tier for admins
            'role': 'admin'  # Explicit role for authorization checks
        }
        
        # Insert the superuser into the database
        result = db.users.insert_one(superuser)
        
        if result.inserted_id:
            print(f"Superuser '{username}' created successfully with ID: {result.inserted_id}")
            return True
        else:
            print("Error: Failed to create superuser")
            return False
            
    except Exception as e:
        print(f"Error connecting to MongoDB: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage: python create_superuser.py <username> <email> <password> [first_name] [last_name]")
        sys.exit(1)
    
    username = sys.argv[1]
    email = sys.argv[2]
    password = sys.argv[3]
    
    first_name = sys.argv[4] if len(sys.argv) > 4 else "Admin"
    last_name = sys.argv[5] if len(sys.argv) > 5 else "User"
    
    success = create_superuser(username, email, password, first_name, last_name)
    sys.exit(0 if success else 1)