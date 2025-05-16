import os
from datetime import timedelta
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Base config."""
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-key-change-in-production')
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'jwt-secret-key')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(days=1)
    
    # MongoDB settings - we'll set MONGO_URI in the app factory now
    # We just need placeholders here
    MONGO_URI = None
    MONGO_USERNAME = os.environ.get('MONGO_USERNAME')
    MONGO_PASSWORD = os.environ.get('MONGO_PASSWORD')
    MONGO_CLUSTER = os.environ.get('MONGO_CLUSTER')
    MONGO_DATABASE = os.environ.get('MONGO_DATABASE', 'sweatz_dev')

class DevelopmentConfig(Config):
    """Development config."""
    DEBUG = True
    MONGO_DATABASE = os.environ.get('MONGO_DATABASE', 'sweatz_dev')

class TestingConfig(Config):
    """Testing config."""
    TESTING = True
    MONGO_DATABASE = 'sweatz_test'

class ProductionConfig(Config):
    """Production config."""
    DEBUG = False
    MONGO_DATABASE = 'sweatz_prod'
    
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}