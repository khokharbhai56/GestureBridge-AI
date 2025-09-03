import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # MongoDB Configuration
    MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017/gesturebridge')
    
    # JWT Configuration
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'your-secret-key-change-in-production')
    JWT_ACCESS_TOKEN_EXPIRES = int(os.getenv('JWT_ACCESS_TOKEN_EXPIRES', 3600))
    
    # Server Configuration
    PORT = int(os.getenv('PORT', 5000))
    HOST = os.getenv('HOST', '0.0.0.0')
    
    # ML Model Configuration
    MODEL_PATH = os.getenv('MODEL_PATH', 'backend/model/saved_model')
    MODEL_VERSION = os.getenv('MODEL_VERSION', '2.0')
    CONFIDENCE_THRESHOLD = float(os.getenv('CONFIDENCE_THRESHOLD', 0.85))
    
    # Video Processing
    MAX_FRAME_SIZE = os.getenv('MAX_FRAME_SIZE', '640x480')
    MAX_FPS = int(os.getenv('MAX_FPS', 30))
    VIDEO_QUALITY = os.getenv('VIDEO_QUALITY', 'medium')
    
    # Security
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', 'http://localhost:8000,http://127.0.0.1:5500').split(',')
    RATE_LIMIT = int(os.getenv('RATE_LIMIT', 100))
    MAX_CONTENT_LENGTH = int(os.getenv('MAX_CONTENT_LENGTH', 16777216))
