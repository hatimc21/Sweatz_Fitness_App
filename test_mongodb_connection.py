import pymongo
import urllib.parse
import os
from dotenv import load_dotenv

load_dotenv()

def test_connection():
    username = os.environ.get('MONGO_USERNAME')
    password = urllib.parse.quote_plus(os.environ.get('MONGO_PASSWORD', ''))
    cluster = os.environ.get('MONGO_CLUSTER')
    database = os.environ.get('MONGO_DATABASE')
    
    uri = f"mongodb+srv://{username}:{password}@{cluster}/{database}?retryWrites=true&w=majority&appName=Cluster0"
    
    print(f"Trying to connect with URI: mongodb+srv://{username}:****@{cluster}/{database}?retryWrites=true&w=majority&appName=Cluster0")
    
    try:
        client = pymongo.MongoClient(uri)
        
        # The ismaster command is cheap and does not require auth.
        client.admin.command('ismaster')
        
        print("Connection successful!")
        print("Available databases:")
        for db in client.list_database_names():
            print(f" - {db}")
        
        return True
    except Exception as e:
        print(f"Connection failed: {e}")
        return False

if __name__ == "__main__":
    test_connection()