from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
import sys
import os
import logging

# Fix import error by adding backend directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from config import Config

logger = logging.getLogger(__name__)

class Database:
    def __init__(self):
        self.client = None
        self.db = None
        self.models = {}
        self._initialize_logging()

    def _initialize_logging(self):
        """Initialize logging configuration"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )

    def connect(self):
        """Establish connection to MongoDB"""
        try:
            self.client = MongoClient(Config.MONGO_URI, serverSelectionTimeoutMS=5000)
            # Test the connection
            self.client.server_info()
            self.db = self.client.get_database()
            
            # Initialize models
            self._initialize_models()
            
            logger.info("Successfully connected to MongoDB!")
            return True
        except ConnectionError as e:
            logger.error(f"Failed to connect to MongoDB: {str(e)}")
            raise
        except ServerSelectionTimeoutError as e:
            logger.error(f"MongoDB server selection timeout: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error while connecting to MongoDB: {str(e)}")
            raise

    def _initialize_models(self):
        """Initialize database models"""
        try:
            # Import models from the same directory
            from models import (
                UserModel, TranslationModel, FeedbackModel,
                StreamingSessionModel, AnalyticsModel, LanguageModel
            )
            
            self.models['users'] = UserModel(self)
            self.models['translations'] = TranslationModel(self)
            self.models['feedback'] = FeedbackModel(self)
            self.models['streaming_sessions'] = StreamingSessionModel(self)
            self.models['analytics'] = AnalyticsModel(self)
            self.models['languages'] = LanguageModel(self)
            
            logger.info("Database models initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing database models: {str(e)}")
            raise

    def get_model(self, model_name):
        """Get a database model"""
        if model_name not in self.models:
            raise ValueError(f"Model '{model_name}' not found")
        return self.models[model_name]

    def close(self):
        """Close the MongoDB connection"""
        if self.client:
            try:
                self.client.close()
                logger.info("MongoDB connection closed successfully")
            except Exception as e:
                logger.error(f"Error closing MongoDB connection: {str(e)}")

    def get_collection(self, collection_name):
        """Get a MongoDB collection"""
        if self.db is None:
            raise ConnectionError("Database connection not established")
        return self.db[collection_name]

    def create_indexes(self):
        """Create necessary indexes for collections"""
        try:
            from models import create_database_indexes
            create_database_indexes(self)
            logger.info("All database indexes created successfully")
        except Exception as e:
            logger.error(f"Error creating database indexes: {str(e)}")
            raise

    def initialize_default_data(self):
        """Initialize default data in the database"""
        try:
            # Initialize supported languages
            languages_model = self.get_model('languages')
            
            # Check if languages already exist
            existing_languages = languages_model.get_supported_languages()
            if not existing_languages:
                default_languages = [
                    {
                        'code': 'ASL',
                        'name': 'American Sign Language',
                        'native_name': 'ASL',
                        'country': 'United States',
                        'region': 'North America',
                        'is_active': True,
                        'model_version': '2.0',
                        'accuracy': 0.992
                    },
                    {
                        'code': 'BSL',
                        'name': 'British Sign Language',
                        'native_name': 'BSL',
                        'country': 'United Kingdom',
                        'region': 'Europe',
                        'is_active': True,
                        'model_version': '2.0',
                        'accuracy': 0.988
                    },
                    {
                        'code': 'JSL',
                        'name': 'Japanese Sign Language',
                        'native_name': '日本手話',
                        'country': 'Japan',
                        'region': 'Asia',
                        'is_active': True,
                        'model_version': '1.8',
                        'accuracy': 0.985
                    },
                    {
                        'code': 'LSF',
                        'name': 'French Sign Language',
                        'native_name': 'Langue des signes française',
                        'country': 'France',
                        'region': 'Europe',
                        'is_active': True,
                        'model_version': '1.9',
                        'accuracy': 0.983
                    },
                    {
                        'code': 'DGS',
                        'name': 'German Sign Language',
                        'native_name': 'Deutsche Gebärdensprache',
                        'country': 'Germany',
                        'region': 'Europe',
                        'is_active': True,
                        'model_version': '1.7',
                        'accuracy': 0.981
                    }
                ]
                
                for lang_data in default_languages:
                    languages_model.create_language(lang_data)
                
                logger.info("Default languages initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing default data: {str(e)}")
            raise

    def get_database_stats(self):
        """Get database statistics"""
        try:
            stats = {}
            
            # Get collection stats
            collections = ['users', 'translations', 'feedback', 'streaming_sessions', 'analytics', 'languages']
            for collection_name in collections:
                collection = self.get_collection(collection_name)
                stats[collection_name] = {
                    'count': collection.count_documents({}),
                    'size': collection.estimated_document_count()
                }
            
            # Get database info
            db_stats = self.db.command("dbStats")
            stats['database'] = {
                'name': self.db.name,
                'collections': db_stats.get('collections', 0),
                'data_size': db_stats.get('dataSize', 0),
                'storage_size': db_stats.get('storageSize', 0),
                'indexes': db_stats.get('indexes', 0)
            }
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting database stats: {str(e)}")
            return {}

# Create a global database instance
db = Database()
