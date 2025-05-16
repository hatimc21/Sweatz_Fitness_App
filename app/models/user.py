from flask_login import UserMixin
from bson import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
from app import mongo, login_manager
from datetime import datetime

class User(UserMixin):
    def __init__(self, user_data):
        self.id = str(user_data.get('_id'))
        self.username = user_data.get('username')
        self.email = user_data.get('email')
        self.password_hash = user_data.get('password_hash')
        self.first_name = user_data.get('first_name')
        self.last_name = user_data.get('last_name')
        self.created_at = user_data.get('created_at')
        self.last_login = user_data.get('last_login')
        self._is_active = user_data.get('is_active', True)
        self._is_superuser = user_data.get('is_superuser', False)
        self._role = user_data.get('role', 'user')
        self._subscription_tier = user_data.get('subscription_tier', 'free')
    
    def get_id(self):
        return self.id
    
    # Override is_active property from UserMixin
    @property
    def is_active(self):
        return self._is_active
    
    @property
    def is_superuser(self):
        return self._is_superuser
    
    @property
    def role(self):
        return self._role
    
    @property
    def subscription_tier(self):
        return self._subscription_tier
    
    @property
    def is_admin(self):
        """Check if the user has admin privileges"""
        return self.is_superuser or self.role == 'admin'
    
    @staticmethod
    def create(username, email, password, first_name="", last_name="", is_superuser=False, role="user"):
        user_data = {
            'username': username,
            'email': email,
            'password_hash': generate_password_hash(password),
            'first_name': first_name,
            'last_name': last_name,
            'created_at': datetime.utcnow(),
            'is_active': True,
            'is_superuser': is_superuser,
            'role': role,
            'subscription_tier': 'admin' if is_superuser else 'free'
        }
        
        # Insert user into MongoDB
        result = mongo.db.users.insert_one(user_data)
        user_data['_id'] = result.inserted_id
        
        return User(user_data)
    
    @staticmethod
    def get_by_email(email):
        user_data = mongo.db.users.find_one({'email': email})
        if user_data:
            return User(user_data)
        return None
    
    @staticmethod
    def get_by_username(username):
        user_data = mongo.db.users.find_one({'username': username})
        if user_data:
            return User(user_data)
        return None
    
    @staticmethod
    def get_by_id(user_id):
        try:
            user_data = mongo.db.users.find_one({'_id': ObjectId(user_id)})
            if user_data:
                return User(user_data)
        except:
            pass
        return None
    
    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def update_last_login(self):
        mongo.db.users.update_one(
            {'_id': ObjectId(self.id)},
            {'$set': {'last_login': datetime.utcnow()}}
        )

@login_manager.user_loader
def load_user(user_id):
    return User.get_by_id(user_id)