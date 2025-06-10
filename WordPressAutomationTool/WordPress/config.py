
import os

class Config:
    DEBUG = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///wordpress.db')
    SECRET_KEY = os.getenv('FLASK_SECRET_KEY', 'default-secret-key-change-in-production')
    
class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False
    # Ensure we're using 0.0.0.0 for production
    HOST = '0.0.0.0'
    PORT = int(os.getenv('PORT', 5000))
