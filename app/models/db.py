from pymongo import MongoClient, ASCENDING, DESCENDING, TEXT
from pymongo.errors import OperationFailure, BulkWriteError
from config import Config
from datetime import datetime, timedelta
import hashlib
from bson.objectid import ObjectId
import json

class Database:
    """Advanced MongoDB database connection and operations"""
    
    def __init__(self):
        self.client = MongoClient(Config.MONGODB_URI)
        self.db = self.client[Config.DB_NAME]
        self._init_collections()
        self._setup_indexes()
        self._setup_validation()
    
    def _init_collections(self):
        """Initialize database collections"""
        collections = {
            'users': False,
            'activity_logs': False,
            'fatigue_results': False,
            'analytics': False,
            'audit_logs': True  # TTL collection
        }
        
        for collection_name, has_ttl in collections.items():
            if collection_name not in self.db.list_collection_names():
                if has_ttl:
                    self.db.create_collection(collection_name)
                else:
                    self.db.create_collection(collection_name)
    
    def _setup_indexes(self):
        """Setup advanced indexes including compound and TTL indexes"""
        # Users collection indexes
        try:
            self.db.users.create_index('email', unique=True)
            self.db.users.create_index('created_at')
            self.db.users.create_index([('email', TEXT)])  # Text search index
        except OperationFailure:
            pass
        
        # Activity logs collection indexes (compound indexes for performance)
        try:
            self.db.activity_logs.create_index([('user_id', ASCENDING), ('timestamp', DESCENDING)])
            self.db.activity_logs.create_index('user_id')
            self.db.activity_logs.create_index('timestamp')
            # TTL index - auto-delete after 90 days
            self.db.activity_logs.create_index('timestamp', expireAfterSeconds=7776000)
        except OperationFailure:
            pass
        
        # Fatigue results collection indexes
        try:
            self.db.fatigue_results.create_index([('user_id', ASCENDING), ('timestamp', DESCENDING)])
            self.db.fatigue_results.create_index('user_id')
            self.db.fatigue_results.create_index('fatigue_level')
            # TTL index - auto-delete after 180 days
            self.db.fatigue_results.create_index('timestamp', expireAfterSeconds=15552000)
        except OperationFailure:
            pass
        
        # Audit logs collection indexes (TTL index)
        try:
            self.db.audit_logs.create_index([('user_id', ASCENDING), ('timestamp', DESCENDING)])
            # Auto-delete audit logs after 30 days
            self.db.audit_logs.create_index('timestamp', expireAfterSeconds=2592000)
        except OperationFailure:
            pass
    
    def _setup_validation(self):
        """Setup MongoDB schema validation"""
        try:
            # User schema validation
            self.db.command('collMod', 'users', validator={
                '$jsonSchema': {
                    'bsonType': 'object',
                    'required': ['email', 'password', 'full_name'],
                    'properties': {
                        '_id': {'bsonType': 'objectId'},
                        'email': {'bsonType': 'string', 'pattern': '^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$'},
                        'password': {'bsonType': 'string'},
                        'full_name': {'bsonType': 'string'},
                        'created_at': {'bsonType': 'date'},
                        'is_active': {'bsonType': 'bool'}
                    }
                }
            }, validationLevel='moderate')
        except OperationFailure:
            pass
    
    def register_user(self, email, password, full_name):
        """Register a new user"""
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        user = {
            'email': email,
            'password': hashed_password,
            'full_name': full_name,
            'created_at': datetime.now(),
            'is_active': True
        }
        result = self.db.users.insert_one(user)
        
        # Audit log
        self._audit_log('create_user', str(result.inserted_id), 'User registration')
        
        return str(result.inserted_id)
    
    def find_user_by_email(self, email):
        """Find user by email"""
        return self.db.users.find_one({'email': email})
    
    def find_user_by_id(self, user_id):
        """Find user by ID"""
        return self.db.users.find_one({'_id': ObjectId(user_id)})
    
    def save_activity_log(self, user_id, typing_speed, inactivity_duration, key_presses, error_rate=0, keypress_interval=0, session_time=0, session_id=None):
        """Save user activity log"""
        log = {
            'user_id': user_id,
            'typing_speed': typing_speed,
            'inactivity_duration': inactivity_duration,
            'key_presses': key_presses,
            'error_rate': error_rate,
            'keypress_interval': keypress_interval,
            'session_time': session_time,
            'timestamp': datetime.now()
        }
        if session_id:
            log['session_id'] = session_id
            self.db.activity_logs.update_one(
                {'user_id': user_id, 'session_id': session_id},
                {'$set': log},
                upsert=True
            )
            doc = self.db.activity_logs.find_one({'user_id': user_id, 'session_id': session_id})
            return str(doc['_id']) if doc else None
        else:
            result = self.db.activity_logs.insert_one(log)
            return str(result.inserted_id)
    
    def get_user_activity(self, user_id, limit=50):
        """Get recent activity logs for user"""
        logs = list(self.db.activity_logs.find(
            {'user_id': user_id}
        ).sort('timestamp', -1).limit(limit))
        return logs
    
    def save_fatigue_result(self, user_id, fatigue_level, confidence, metrics, session_id=None):
        """Save fatigue detection result"""
        result = {
            'user_id': user_id,
            'fatigue_level': fatigue_level,
            'confidence': confidence,
            'metrics': metrics,
            'timestamp': datetime.now()
        }
        if session_id:
            result['session_id'] = session_id
            self.db.fatigue_results.update_one(
                {'user_id': user_id, 'session_id': session_id},
                {'$set': result},
                upsert=True
            )
            self._audit_log('save_fatigue', user_id, f'Fatigue level: {fatigue_level}')
            doc = self.db.fatigue_results.find_one({'user_id': user_id, 'session_id': session_id})
            return str(doc['_id']) if doc else None
        else:
            insert_result = self.db.fatigue_results.insert_one(result)
            self._audit_log('save_fatigue', user_id, f'Fatigue level: {fatigue_level}')
            return str(insert_result.inserted_id)
    
    def get_latest_fatigue_result(self, user_id):
        """Get latest fatigue result for user"""
        result = self.db.fatigue_results.find_one(
            {'user_id': user_id},
            sort=[('timestamp', -1)]
        )
        return result
    
    def get_fatigue_history(self, user_id, limit=30):
        """Get fatigue history for user"""
        results = list(self.db.fatigue_results.find(
            {'user_id': user_id}
        ).sort('timestamp', -1).limit(limit))
        return results
    
    def delete_activity_log(self, user_id, log_id):
        """Delete a specific activity log"""
        result = self.db.activity_logs.delete_one({
            '_id': log_id,
            'user_id': user_id
        })
        return result
    
    def delete_all_user_activity_logs(self, user_id):
        """Delete all activity logs for a user"""
        result = self.db.activity_logs.delete_many({
            'user_id': user_id
        })
        return result
    
    # ================ ADVANCED MONGODB FEATURES ================
    
    def _audit_log(self, action, user_id, details):
        """Create audit log entry"""
        audit_entry = {
            'action': action,
            'user_id': user_id,
            'details': details,
            'timestamp': datetime.now()
        }
        self.db.audit_logs.insert_one(audit_entry)
    
    def bulk_insert_activity_logs(self, user_id, activities):
        """Bulk insert multiple activity logs using Bulk API"""
        from pymongo import InsertOne
        
        requests = []
        for activity in activities:
            activity['user_id'] = user_id
            activity['timestamp'] = datetime.now()
            requests.append(InsertOne(activity))
        
        try:
            if requests:
                result = self.db.activity_logs.bulk_write(requests, ordered=False)
                return {
                    'inserted_count': result.inserted_count,
                    'success': True
                }
        except BulkWriteError as e:
            return {
                'inserted_count': e.details.get('nInserted', 0) if e.details else 0,
                'success': False,
                'error': str(e)
            }
        
        return {'inserted_count': 0, 'success': True}
    
    def get_user_fatigue_analytics(self, user_id):
        """Get comprehensive fatigue analytics using Aggregation Pipeline"""
        pipeline = [
            # Stage 1: Match user's fatigue results
            {'$match': {'user_id': user_id}},
            
            # Stage 2: Group by fatigue level and calculate stats
            {
                '$facet': {
                    'fatigue_distribution': [
                        {
                            '$group': {
                                '_id': '$fatigue_level',
                                'count': {'$sum': 1},
                                'avg_confidence': {'$avg': '$confidence'}
                            }
                        }
                    ],
                    'timeline_stats': [
                        {
                            '$group': {
                                '_id': {
                                    '$dateToString': {
                                        'format': '%Y-%m-%d',
                                        'date': '$timestamp'
                                    }
                                },
                                'daily_count': {'$sum': 1},
                                'avg_fatigue_confidence': {'$avg': '$confidence'}
                            }
                        },
                        {'$sort': {'_id': -1}},
                        {'$limit': 7}  # Last 7 days
                    ],
                    'overall_stats': [
                        {
                            '$group': {
                                '_id': None,
                                'total_assessments': {'$sum': 1},
                                'avg_confidence': {'$avg': '$confidence'},
                                'max_confidence': {'$max': '$confidence'},
                                'min_confidence': {'$min': '$confidence'}
                            }
                        }
                    ]
                }
            }
        ]
        
        results = list(self.db.fatigue_results.aggregate(pipeline))
        return results[0] if results else {}
    
    def get_user_activity_analytics(self, user_id):
        """Get activity analytics using Aggregation Pipeline"""
        pipeline = [
            {'$match': {'user_id': user_id}},
            {
                '$facet': {
                    'typing_stats': [
                        {
                            '$group': {
                                '_id': None,
                                'avg_typing_speed': {'$avg': '$typing_speed'},
                                'max_typing_speed': {'$max': '$typing_speed'},
                                'min_typing_speed': {'$min': '$typing_speed'}
                            }
                        }
                    ],
                    'inactivity_stats': [
                        {
                            '$group': {
                                '_id': None,
                                'avg_inactivity': {'$avg': '$inactivity_duration'},
                                'max_inactivity': {'$max': '$inactivity_duration'}
                            }
                        }
                    ],
                    'key_press_stats': [
                        {
                            '$group': {
                                '_id': None,
                                'avg_key_presses': {'$avg': '$key_presses'},
                                'total_key_presses': {'$sum': '$key_presses'}
                            }
                        }
                    ]
                }
            }
        ]
        
        results = list(self.db.activity_logs.aggregate(pipeline))
        return results[0] if results else {}
    
    def get_top_fatigued_users(self, limit=10):
        """Get users with highest fatigue levels using Aggregation"""
        pipeline = [
            {
                '$group': {
                    '_id': '$user_id',
                    'avg_fatigue_confidence': {'$avg': '$confidence'},
                    'total_assessments': {'$sum': 1},
                    'latest_assessment': {'$max': '$timestamp'}
                }
            },
            {'$sort': {'avg_fatigue_confidence': -1}},
            {'$limit': limit}
        ]
        
        results = list(self.db.fatigue_results.aggregate(pipeline))
        return results
    
    def bulk_update_fatigue_levels(self, updates):
        """Bulk update fatigue levels using Bulk API"""
        from pymongo import UpdateOne
        
        requests = []
        for user_id, new_level in updates:
            requests.append(
                UpdateOne(
                    {'user_id': user_id},
                    {'$set': {'fatigue_level': new_level, 'updated_at': datetime.now()}},
                    upsert=False
                )
            )
        
        try:
            if requests:
                result = self.db.fatigue_results.bulk_write(requests, ordered=False)
                return {
                    'modified_count': result.modified_count,
                    'success': True
                }
        except BulkWriteError as e:
            return {
                'modified_count': e.details.get('nModified', 0) if e.details else 0,
                'success': False,
                'error': str(e)
            }
        
        return {'modified_count': 0, 'success': True}
    
    def transaction_create_user_and_log(self, email, password, full_name, initial_activity):
        """Create user and initial activity log in a transaction"""
        session = self.client.start_session()
        try:
            with session.start_transaction():
                # Register user
                hashed_password = hashlib.sha256(password.encode()).hexdigest()
                user = {
                    'email': email,
                    'password': hashed_password,
                    'full_name': full_name,
                    'created_at': datetime.now(),
                    'is_active': True
                }
                user_result = self.db.users.insert_one(user, session=session)
                user_id = str(user_result.inserted_id)
                
                # Create initial activity log
                activity = {
                    'user_id': user_id,
                    **initial_activity,
                    'timestamp': datetime.now()
                }
                activity_result = self.db.activity_logs.insert_one(activity, session=session)
                
                return {
                    'success': True,
                    'user_id': user_id,
                    'activity_id': str(activity_result.inserted_id)
                }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
        finally:
            session.end_session()
    
    def search_users_by_name(self, search_text):
        """Search users by name using text search"""
        try:
            results = list(self.db.users.find(
                {'$text': {'$search': search_text}},
                {'score': {'$meta': 'textScore'}}
            ).sort([('score', {'$meta': 'textScore'})])
            )
            return results
        except OperationFailure:
            return []
    
    def get_database_stats(self):
        """Get comprehensive database statistics"""
        stats = {
            'users_count': self.db.users.count_documents({}),
            'activity_logs_count': self.db.activity_logs.count_documents({}),
            'fatigue_results_count': self.db.fatigue_results.count_documents({}),
            'audit_logs_count': self.db.audit_logs.count_documents({}),
            'collections': self.db.list_collection_names(),
            'indexes': {}
        }
        
        for collection_name in stats['collections']:
            stats['indexes'][collection_name] = list(
                self.db[collection_name].list_indexes()
            )
        
        return stats

# Global database instance
db = None

def get_db():
    """Get database instance"""
    global db
    if db is None:
        db = Database()
    return db
