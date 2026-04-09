import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Application configuration"""
    SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key-here-change-in-production')
    
    # MongoDB Configuration
    MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/')
    DB_NAME = 'cognitive_fatigue_db'
    
    # Session Configuration
    SESSION_TIMEOUT = 3600  # 1 hour
    
    # CORS Configuration
    CORS_ORIGINS = ['http://localhost:5000', 'http://127.0.0.1:5000']
