# app/utils/mock_db.py
from datetime import datetime
from bson import ObjectId
import json
import os
import random

# In-memory storage
_mock_data = {
    'users': [],
    'meals': [],
    'water_intake': [],
    'nutrition_goals': [],
    'weight_logs': [],
    'body_measurements': [],
    'body_composition': [],
    'progress_photos': [],
    'body_goals': [],
    'exercises': [],
    'workout_routines': [],
    'scheduled_workouts': [],
    'completed_workouts': [],
    'reminders': [],
    'settings': [
        {
            '_id': 'app_settings',
            'maintenance_mode': False,
            'allow_registrations': True,
            'default_subscription': 'free',
            'app_version': '1.0.0',
            'last_updated': datetime.now()
        }
    ]
}

# Add some default admin user
_mock_data['users'].append({
    '_id': ObjectId('6123456789abcdef01234567'),
    'username': 'admin',
    'email': 'admin@example.com',
    'password_hash': 'pbkdf2:sha256:150000$x7QZ9cNT$5b2491202c8a61cc38aa43db4d9c0d602dedb42cd8969ba4422c040f46d59303',  # password is 'admin123'
    'first_name': 'Admin',
    'last_name': 'User',
    'created_at': datetime(2024, 1, 1),
    'last_login': datetime(2025, 5, 1),
    'is_active': True,
    'is_superuser': True,
    'role': 'admin',
    'subscription_tier': 'admin'
})

# Add some regular user
_mock_data['users'].append({
    '_id': ObjectId('7123456789abcdef01234567'),
    'username': 'user',
    'email': 'user@example.com',
    'password_hash': 'pbkdf2:sha256:150000$x7QZ9cNT$5b2491202c8a61cc38aa43db4d9c0d602dedb42cd8969ba4422c040f46d59303',  # password is 'admin123' (same for simplicity)
    'first_name': 'Regular',
    'last_name': 'User',
    'created_at': datetime(2024, 2, 1),
    'last_login': datetime(2025, 5, 1),
    'is_active': True,
    'is_superuser': False,
    'role': 'user',
    'subscription_tier': 'free'
})

# Add sample exercises
exercise_categories = ["Chest", "Back", "Shoulders", "Arms", "Legs", "Core", "Full Body", "Cardio"]
difficulties = ["beginner", "intermediate", "advanced"]

for i in range(1, 20):
    _mock_data['exercises'].append({
        '_id': ObjectId(),
        'name': f"Sample Exercise {i}",
        'description': f"This is a sample exercise description for exercise {i}.",
        'muscle_group': random.choice(exercise_categories),
        'difficulty': random.choice(difficulties),
        'instruction': f"Step 1. Do this.\nStep 2. Do that.\nStep 3. Complete set for exercise {i}.",
        'video_url': f"https://www.youtube.com/watch?v=sample{i}",
        'equipment': ["barbell", "dumbbell"] if i % 2 == 0 else ["bodyweight"],
        'created_at': datetime.now(),
        'created_by': '6123456789abcdef01234567'  # admin user ID
    })

class MockCollection:
    def __init__(self, collection_name):
        self.collection_name = collection_name
        self.data = _mock_data.get(collection_name, [])
    
    def find_one(self, query=None, *args, **kwargs):
        """Find a single document matching the query"""
        if not query:
            return self.data[0] if self.data else None
        
        for doc in self.data:
            matches = True
            for key, value in query.items():
                if key == '_id' and isinstance(value, str):
                    value = ObjectId(value)
                
                if key not in doc:
                    matches = False
                    break
                
                if isinstance(value, dict):
                    # Handle comparison operators like $gte, $lte
                    if '$gte' in value and doc[key] < value['$gte']:
                        matches = False
                        break
                    if '$lte' in value and doc[key] > value['$lte']:
                        matches = False
                        break
                elif doc[key] != value:
                    matches = False
                    break
            
            if matches:
                return doc
        
        return None
    
    def count_documents(self, query=None):
        """Count documents matching the query"""
        if not query:
            return len(self.data)
        
        count = 0
        for doc in self.data:
            matches = True
            for key, value in query.items():
                if key == '_id' and isinstance(value, str):
                    value = ObjectId(value)
                
                if key not in doc:
                    matches = False
                    break
                
                if isinstance(value, dict):
                    # Handle comparison operators like $gte, $lte
                    if '$gte' in value and doc[key] < value['$gte']:
                        matches = False
                        break
                    if '$lte' in value and doc[key] > value['$lte']:
                        matches = False
                        break
                elif doc[key] != value:
                    matches = False
                    break
            
            if matches:
                count += 1
        
        return count
    
    def find(self, query=None, *args, **kwargs):
        """Find documents matching the query"""
        if not query:
            return MockCursor(self.data)
        
        results = []
        for doc in self.data:
            matches = True
            for key, value in query.items():
                if key == '_id' and isinstance(value, str):
                    value = ObjectId(value)
                
                if key not in doc:
                    matches = False
                    break
                
                if isinstance(value, dict):
                    # Handle comparison operators like $gte, $lte
                    if '$gte' in value and doc[key] < value['$gte']:
                        matches = False
                        break
                    if '$lte' in value and doc[key] > value['$lte']:
                        matches = False
                        break
                elif doc[key] != value:
                    matches = False
                    break
            
            if matches:
                results.append(doc)
        
        return MockCursor(results)
    
    def distinct(self, field):
        """Get distinct values for a field"""
        values = set()
        for doc in self.data:
            if field in doc:
                if isinstance(doc[field], list):
                    for val in doc[field]:
                        values.add(val)
                else:
                    values.add(doc[field])
        return list(values)
    
    def insert_one(self, document):
        """Insert a document"""
        if '_id' not in document:
            document['_id'] = ObjectId()
        
        self.data.append(document)
        _mock_data[self.collection_name] = self.data
        
        return MockResult(document['_id'])
    
    def update_one(self, query, update, upsert=False):
        """Update a document"""
        if '$set' in update:
            update_data = update['$set']
        else:
            update_data = update
        
        for i, doc in enumerate(self.data):
            matches = True
            for key, value in query.items():
                if key == '_id' and isinstance(value, str):
                    value = ObjectId(value)
                
                if key not in doc:
                    matches = False
                    break
                
                if doc[key] != value:
                    matches = False
                    break
            
            if matches:
                for key, value in update_data.items():
                    doc[key] = value
                
                _mock_data[self.collection_name][i] = doc
                return MockResult(None, 1)
        
        # If no document matches and upsert is True, insert
        if upsert:
            new_doc = {**query, **update_data}
            if '_id' not in new_doc:
                new_doc['_id'] = ObjectId()
            
            self.data.append(new_doc)
            _mock_data[self.collection_name] = self.data
            
            return MockResult(None, 0, 0, new_doc['_id'])
        
        return MockResult(None, 0)
    
    def delete_one(self, query):
        """Delete a document"""
        for i, doc in enumerate(self.data):
            matches = True
            for key, value in query.items():
                if key == '_id' and isinstance(value, str):
                    value = ObjectId(value)
                
                if key not in doc:
                    matches = False
                    break
                
                if doc[key] != value:
                    matches = False
                    break
            
            if matches:
                del self.data[i]
                _mock_data[self.collection_name] = self.data
                return MockResult(None, 0, 1)
        
        return MockResult(None, 0, 0)
    
    def aggregate(self, pipeline):
        """Simple mock for aggregation"""
        if self.collection_name == 'users' and len(pipeline) > 0 and '$group' in pipeline[0]:
            # Mock for user subscription distribution
            return [
                {"_id": "free", "count": 5},
                {"_id": "premium", "count": 2},
                {"_id": "admin", "count": 1}
            ]
        
        return []

class MockCursor:
    def __init__(self, documents):
        self.documents = documents
        self.current_sort = None
        self.current_limit = None
        self.current_skip = 0
    
    def sort(self, field, direction):
        """Sort the documents"""
        self.current_sort = (field, direction)
        return self
    
    def limit(self, n):
        """Limit the documents"""
        self.current_limit = n
        return self
    
    def skip(self, n):
        """Skip the documents"""
        self.current_skip = n
        return self
    
    def __iter__(self):
        """Return iterator for documents"""
        documents = self.documents
        
        # Apply sort if specified
        if self.current_sort:
            field, direction = self.current_sort
            documents = sorted(documents, key=lambda x: x.get(field, None), reverse=(direction < 0))
        
        # Apply skip
        if self.current_skip > 0:
            documents = documents[self.current_skip:]
        
        # Apply limit
        if self.current_limit is not None:
            documents = documents[:self.current_limit]
        
        return iter(documents)

class MockResult:
    def __init__(self, inserted_id=None, modified_count=0, deleted_count=0, upserted_id=None):
        self.inserted_id = inserted_id
        self.modified_count = modified_count
        self.deleted_count = deleted_count
        self.upserted_id = upserted_id

class MockMongoDB:
    def __init__(self):
        self.collections = {}
    
    def __getattr__(self, name):
        if name not in self.collections:
            self.collections[name] = MockCollection(name)
        return self.collections[name]

    def command(self, cmd):
        """Mock for database commands"""
        if cmd == "serverStatus":
            return {"version": "5.0.0-mock"}
        return {}
    
    def list_collection_names(self):
        """Return list of collection names"""
        return list(_mock_data.keys())