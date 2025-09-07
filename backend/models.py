from datetime import datetime
from bson import ObjectId
from pymongo import ASCENDING, DESCENDING
import logging

logger = logging.getLogger(__name__)

class BaseModel:
    """Base model class with common functionality"""
    
    def __init__(self, db):
        self.db = db
    
    def to_dict(self, document):
        """Convert MongoDB document to dictionary with string IDs"""
        if document:
            document['_id'] = str(document['_id'])
            if 'user_id' in document and isinstance(document['user_id'], ObjectId):
                document['user_id'] = str(document['user_id'])
            if 'created_at' in document:
                document['created_at'] = document['created_at'].isoformat()
            if 'updated_at' in document:
                document['updated_at'] = document['updated_at'].isoformat()
        return document

class UserModel(BaseModel):
    """User model for managing user data"""
    
    def __init__(self, db):
        super().__init__(db)
        self.collection = db.get_collection('users')
    
    def create_user(self, username, email, password_hash, additional_data=None):
        """Create a new user"""
        user_data = {
            'username': username,
            'email': email,
            'password': password_hash,
            'profile': {
                'first_name': additional_data.get('first_name', '') if additional_data else '',
                'last_name': additional_data.get('last_name', '') if additional_data else '',
                'preferred_language': additional_data.get('preferred_language', 'ASL') if additional_data else 'ASL',
                'country': additional_data.get('country', '') if additional_data else '',
                'bio': additional_data.get('bio', '') if additional_data else '',
                'avatar_url': additional_data.get('avatar_url', '') if additional_data else ''
            },
            'settings': {
                'notifications_enabled': True,
                'email_notifications': True,
                'privacy_level': 'public',
                'theme': 'light'
            },
            'statistics': {
                'total_translations': 0,
                'total_sessions': 0,
                'accuracy_rating': 0.0,
                'favorite_language': 'ASL'
            },
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow(),
            'last_login': None,
            'is_active': True,
            'email_verified': False
        }
        
        result = self.collection.insert_one(user_data)
        return result.inserted_id
    
    def get_user_by_id(self, user_id):
        """Get user by ID"""
        user = self.collection.find_one({'_id': ObjectId(user_id)})
        return self.to_dict(user)
    
    def get_user_by_email(self, email):
        """Get user by email"""
        user = self.collection.find_one({'email': email})
        return self.to_dict(user)
    
    def update_user(self, user_id, update_data):
        """Update user data"""
        update_data['updated_at'] = datetime.utcnow()
        result = self.collection.update_one(
            {'_id': ObjectId(user_id)},
            {'$set': update_data}
        )
        return result.modified_count > 0

class TranslationModel(BaseModel):
    """Translation model for managing translation history"""
    
    def __init__(self, db):
        super().__init__(db)
        self.collection = db.get_collection('translations')
    
    def create_translation(self, user_id, translation_data):
        """Create a new translation record"""
        translation = {
            'user_id': ObjectId(user_id),
            'type': translation_data.get('type', 'video'),  # video, text, image, stream
            'input_data': translation_data.get('input_data'),
            'output_data': translation_data.get('output_data'),
            'language': translation_data.get('language', 'ASL'),
            'confidence': translation_data.get('confidence', 0.0),
            'processing_time': translation_data.get('processing_time', 0.0),
            'model_version': translation_data.get('model_version', '1.0'),
            'metadata': {
                'device_type': translation_data.get('device_type', 'unknown'),
                'browser': translation_data.get('browser', 'unknown'),
                'resolution': translation_data.get('resolution', 'unknown'),
                'frame_rate': translation_data.get('frame_rate', 0)
            },
            'feedback': {
                'accuracy_rating': None,
                'user_correction': None,
                'is_helpful': None
            },
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        }
        
        result = self.collection.insert_one(translation)
        return result.inserted_id
    
    def get_user_translations(self, user_id, page=1, per_page=10):
        """Get paginated translations for a user"""
        skip = (page - 1) * per_page
        
        translations = list(self.collection.find(
            {'user_id': ObjectId(user_id)}
        ).sort('created_at', DESCENDING).skip(skip).limit(per_page))
        
        total_count = self.collection.count_documents({'user_id': ObjectId(user_id)})
        
        return {
            'translations': [self.to_dict(t) for t in translations],
            'total': total_count,
            'page': page,
            'per_page': per_page,
            'total_pages': (total_count + per_page - 1) // per_page
        }

class FeedbackModel(BaseModel):
    """Feedback model for managing user feedback"""
    
    def __init__(self, db):
        super().__init__(db)
        self.collection = db.get_collection('feedback')
    
    def create_feedback(self, user_id, feedback_data):
        """Create a new feedback record"""
        feedback = {
            'user_id': ObjectId(user_id),
            'type': feedback_data.get('type'),  # translation, accuracy, feature, bug, general
            'category': feedback_data.get('category', 'general'),
            'rating': feedback_data.get('rating'),
            'title': feedback_data.get('title', ''),
            'comment': feedback_data.get('comment', ''),
            'translation_id': ObjectId(feedback_data['translation_id']) if feedback_data.get('translation_id') else None,
            'suggested_correction': feedback_data.get('suggested_correction'),
            'language': feedback_data.get('language'),
            'severity': feedback_data.get('severity', 'medium'),
            'status': 'pending',
            'metadata': {
                'browser_info': feedback_data.get('browser_info'),
                'device_info': feedback_data.get('device_info'),
                'url': feedback_data.get('url'),
                'user_agent': feedback_data.get('user_agent')
            },
            'admin_response': {
                'response': None,
                'responded_by': None,
                'responded_at': None
            },
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        }
        
        result = self.collection.insert_one(feedback)
        return result.inserted_id
    
    def get_user_feedback(self, user_id, page=1, per_page=10):
        """Get paginated feedback for a user"""
        skip = (page - 1) * per_page
        
        feedback_list = list(self.collection.find(
            {'user_id': ObjectId(user_id)}
        ).sort('created_at', DESCENDING).skip(skip).limit(per_page))
        
        total_count = self.collection.count_documents({'user_id': ObjectId(user_id)})
        
        return {
            'feedback': [self.to_dict(f) for f in feedback_list],
            'total': total_count,
            'page': page,
            'per_page': per_page,
            'total_pages': (total_count + per_page - 1) // per_page
        }

class StreamingSessionModel(BaseModel):
    """Streaming session model for managing real-time sessions"""
    
    def __init__(self, db):
        super().__init__(db)
        self.collection = db.get_collection('streaming_sessions')
    
    def create_session(self, user_id, session_data):
        """Create a new streaming session"""
        session = {
            'user_id': ObjectId(user_id),
            'session_id': session_data.get('session_id'),
            'language': session_data.get('language', 'ASL'),
            'quality': session_data.get('quality', 'medium'),
            'status': 'active',
            'statistics': {
                'total_frames': 0,
                'total_translations': 0,
                'average_confidence': 0.0,
                'duration_seconds': 0
            },
            'translations': [],
            'metadata': {
                'device_type': session_data.get('device_type'),
                'browser': session_data.get('browser'),
                'ip_address': session_data.get('ip_address')
            },
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow(),
            'ended_at': None
        }
        
        result = self.collection.insert_one(session)
        return result.inserted_id
    
    def update_session(self, session_id, update_data):
        """Update streaming session"""
        update_data['updated_at'] = datetime.utcnow()
        result = self.collection.update_one(
            {'session_id': session_id},
            {'$set': update_data}
        )
        return result.modified_count > 0
    
    def end_session(self, session_id, final_stats):
        """End a streaming session"""
        update_data = {
            'status': 'completed',
            'ended_at': datetime.utcnow(),
            'updated_at': datetime.utcnow(),
            'statistics': final_stats
        }
        
        result = self.collection.update_one(
            {'session_id': session_id},
            {'$set': update_data}
        )
        return result.modified_count > 0

class AnalyticsModel(BaseModel):
    """Analytics model for tracking usage and performance"""
    
    def __init__(self, db):
        super().__init__(db)
        self.collection = db.get_collection('analytics')
    
    def log_event(self, user_id, event_data):
        """Log an analytics event"""
        event = {
            'user_id': ObjectId(user_id) if user_id else None,
            'event_type': event_data.get('event_type'),
            'event_name': event_data.get('event_name'),
            'properties': event_data.get('properties', {}),
            'session_id': event_data.get('session_id'),
            'timestamp': datetime.utcnow(),
            'metadata': {
                'user_agent': event_data.get('user_agent'),
                'ip_address': event_data.get('ip_address'),
                'referrer': event_data.get('referrer'),
                'page_url': event_data.get('page_url')
            }
        }
        
        result = self.collection.insert_one(event)
        return result.inserted_id

class LanguageModel(BaseModel):
    """Language model for managing supported languages"""
    
    def __init__(self, db):
        super().__init__(db)
        self.collection = db.get_collection('languages')
    
    def get_supported_languages(self):
        """Get all supported languages"""
        languages = list(self.collection.find({'is_active': True}))
        return [self.to_dict(lang) for lang in languages]
    
    def create_language(self, language_data):
        """Create a new language entry"""
        language = {
            'code': language_data.get('code'),
            'name': language_data.get('name'),
            'native_name': language_data.get('native_name'),
            'country': language_data.get('country'),
            'region': language_data.get('region'),
            'is_active': language_data.get('is_active', True),
            'model_version': language_data.get('model_version', '1.0'),
            'accuracy': language_data.get('accuracy', 0.0),
            'total_users': 0,
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        }
        
        result = self.collection.insert_one(language)
        return result.inserted_id

def create_database_indexes(db):
    """Create all necessary database indexes"""
    try:
        # Users collection indexes
        users = db.get_collection('users')
        users.create_index('email', unique=True)
        users.create_index('username', unique=True)
        users.create_index('created_at')
        users.create_index('last_login')
        
        # Translations collection indexes
        translations = db.get_collection('translations')
        translations.create_index('user_id')
        translations.create_index('created_at')
        translations.create_index('language')
        translations.create_index('type')
        translations.create_index([('user_id', ASCENDING), ('created_at', DESCENDING)])
        
        # Feedback collection indexes
        feedback = db.get_collection('feedback')
        feedback.create_index('user_id')
        feedback.create_index('type')
        feedback.create_index('status')
        feedback.create_index('created_at')
        feedback.create_index('translation_id')
        
        # Streaming sessions collection indexes
        streaming_sessions = db.get_collection('streaming_sessions')
        streaming_sessions.create_index('user_id')
        streaming_sessions.create_index('session_id', unique=True)
        streaming_sessions.create_index('status')
        streaming_sessions.create_index('created_at')
        
        # Analytics collection indexes
        analytics = db.get_collection('analytics')
        analytics.create_index('user_id')
        analytics.create_index('event_type')
        analytics.create_index('timestamp')
        analytics.create_index('session_id')
        
        # Languages collection indexes
        languages = db.get_collection('languages')
        languages.create_index('code', unique=True)
        languages.create_index('is_active')
        
        logger.info("All database indexes created successfully")
        
    except Exception as e:
        logger.error(f"Error creating database indexes: {str(e)}")
        raise
