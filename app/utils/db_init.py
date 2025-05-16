from app import mongo
from pymongo.errors import CollectionInvalid, OperationFailure

def init_db():
    """Initialize MongoDB with required collections and indexes"""
    print("Starting database initialization...")
    
    try:
        # Check connection
        db_info = mongo.db.command("serverStatus")
        print(f"Connected to MongoDB. Server version: {db_info.get('version', 'unknown')}")
        
        # List existing collections
        existing_collections = mongo.db.list_collection_names()
        print(f"Existing collections: {existing_collections}")
        
        # Collections to create
        collections = ['users', 'nutrition_logs', 'body_logs', 'workouts', 'exercises']
        
        # Create collections if they don't exist
        for collection in collections:
            if collection not in existing_collections:
                print(f"Creating collection '{collection}'...")
                mongo.db.create_collection(collection)
                print(f"Collection '{collection}' created successfully.")
            else:
                print(f"Collection '{collection}' already exists.")
        
        # Create indexes (will be created or updated if they already exist)
        print("Creating indexes...")
        
        # Users collection
        mongo.db.users.create_index('email', unique=True)
        print("Created index on users.email")
        
        mongo.db.users.create_index('username', unique=True)
        print("Created index on users.username")
        
        # Nutrition logs
        mongo.db.nutrition_logs.create_index([('user_id', 1), ('date', 1)])
        print("Created index on nutrition_logs.user_id and nutrition_logs.date")
        
        # Body logs
        mongo.db.body_logs.create_index([('user_id', 1), ('date', 1)])
        print("Created index on body_logs.user_id and body_logs.date")
        
        # Workouts
        mongo.db.workouts.create_index('user_id')
        print("Created index on workouts.user_id")
        
        print("Database initialization completed successfully.")
        
    except Exception as e:
        print(f"Error during database initialization: {str(e)}")
        print("Database initialization failed.")