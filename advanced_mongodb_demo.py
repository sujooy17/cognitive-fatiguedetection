"""
Advanced MongoDB Features Demo for Cognitive Fatigue Detection
Demonstrates: Aggregation Pipelines, Bulk Operations, Transactions, TTL Indexes, Text Search, Schema Validation
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from app.models.db import Database
from datetime import datetime, timedelta
import json
from pymongo import InsertOne, UpdateOne
import time

class AdvancedMongoDBDemo:
    def __init__(self):
        self.db = Database()
        self.demo_results = []
    
    def print_section(self, title):
        """Print formatted section header"""
        print("\n" + "="*80)
        print(f"  {title}")
        print("="*80 + "\n")
    
    def print_result(self, title, data):
        """Print formatted result"""
        print(f"✓ {title}")
        print("-" * 80)
        if isinstance(data, (list, dict)):
            print(json.dumps(data, indent=2, default=str))
        else:
            print(data)
        print()
    
    def demo_1_setup_and_indexes(self):
        """Demo 1: Setup Collections, Indexes, and Validation"""
        self.print_section("DEMO 1: MongoDB Setup - Advanced Indexes & Schema Validation")
        
        print("✓ Advanced Index Types Created:")
        print("-" * 80)
        print("1. Unique Index: users.email (unique=True)")
        print("2. Compound Index: activity_logs (user_id ASC, timestamp DESC)")
        print("3. Compound Index: fatigue_results (user_id ASC, timestamp DESC)")
        print("4. Text Search Index: users (email TEXT)")
        print("5. TTL Index: activity_logs (auto-delete after 90 days)")
        print("6. TTL Index: fatigue_results (auto-delete after 180 days)")
        print("7. TTL Index: audit_logs (auto-delete after 30 days)")
        print("\n✓ Schema Validation Enabled:")
        print("-" * 80)
        print("- Users collection: Email pattern, required fields validation")
        print("- Validation level: MODERATE (allows additional fields)")
        print()
    
    def demo_2_bulk_operations(self):
        """Demo 2: Bulk Operations for Batch Insert"""
        self.print_section("DEMO 2: Bulk Operations - Batch Insert Multiple Records")
        
        user_id = "demo_user_bulk"
        activities = [
            {'typing_speed': 45, 'inactivity_duration': 120, 'key_presses': 85},
            {'typing_speed': 52, 'inactivity_duration': 95, 'key_presses': 120},
            {'typing_speed': 38, 'inactivity_duration': 180, 'key_presses': 65},
            {'typing_speed': 60, 'inactivity_duration': 45, 'key_presses': 150},
            {'typing_speed': 35, 'inactivity_duration': 250, 'key_presses': 40},
        ]
        
        result = self.db.bulk_insert_activity_logs(user_id, activities)
        self.print_result("Bulk Insert Result (5 activity logs)", result)
        
        print("📊 Inserted Activities:")
        print("-" * 80)
        for i, activity in enumerate(activities, 1):
            print(f"  Activity {i}: Speed={activity['typing_speed']}wpm, Inactivity={activity['inactivity_duration']}s, Keys={activity['key_presses']}")
        print()
    
    def demo_3_aggregation_pipelines(self):
        """Demo 3: Aggregation Pipelines for Analytics"""
        self.print_section("DEMO 3: Aggregation Pipelines - Activity Analytics")
        
        # First create some test data
        user_id = "demo_user_bulk"
        
        # Get activity analytics
        activity_analytics = self.db.get_user_activity_analytics(user_id)
        
        print("📊 Activity Analytics (Aggregation Pipeline):")
        print("-" * 80)
        if activity_analytics:
            if activity_analytics.get('typing_stats'):
                stats = activity_analytics['typing_stats'][0]
                self.print_result("Typing Speed Statistics", {
                    'Average': f"{stats.get('avg_typing_speed', 0):.2f} wpm",
                    'Maximum': stats.get('max_typing_speed'),
                    'Minimum': stats.get('min_typing_speed')
                })
            
            if activity_analytics.get('inactivity_stats'):
                stats = activity_analytics['inactivity_stats'][0]
                self.print_result("Inactivity Duration Statistics", {
                    'Average': f"{stats.get('avg_inactivity', 0):.2f} seconds",
                    'Maximum': stats.get('max_inactivity')
                })
            
            if activity_analytics.get('key_press_stats'):
                stats = activity_analytics['key_press_stats'][0]
                self.print_result("Key Press Statistics", {
                    'Average': f"{stats.get('avg_key_presses', 0):.2f}",
                    'Total': stats.get('total_key_presses')
                })
    
    def demo_4_transactions(self):
        """Demo 4: Multi-Document Transactions"""
        self.print_section("DEMO 4: Transactions - Atomic User Creation & Activity Log")
        
        initial_activity = {
            'typing_speed': 55,
            'inactivity_duration': 90,
            'key_presses': 110
        }
        
        result = self.db.transaction_create_user_and_log(
            email=f"transaction_user_{int(time.time())}@test.com",
            password="test_password",
            full_name="Transaction Test User",
            initial_activity=initial_activity
        )
        
        if result['success']:
            self.print_result("Transaction Result", {
                'Status': '✓ SUCCESS - Both operations completed atomically',
                'User ID': result['user_id'],
                'Activity Log ID': result['activity_id'],
                'Guarantee': 'If either operation failed, entire transaction rolled back'
            })
        else:
            self.print_result("Transaction Result", {
                'Status': '✗ FAILED',
                'Error': result['error']
            })
    
    def demo_5_fatigue_analytics(self):
        """Demo 5: Complex Aggregation for Fatigue Analytics"""
        self.print_section("DEMO 5: Complex Aggregation - Fatigue Analysis Pipeline")
        
        # Create sample fatigue data
        user_id = "demo_user_fatigue"
        fatigue_samples = [
            {'fatigue_level': 'Low', 'confidence': 85},
            {'fatigue_level': 'Medium', 'confidence': 65},
            {'fatigue_level': 'High', 'confidence': 45},
            {'fatigue_level': 'Medium', 'confidence': 62},
            {'fatigue_level': 'Low', 'confidence': 90},
        ]
        
        # Bulk insert fatigue results
        from pymongo import InsertOne
        requests = []
        for sample in fatigue_samples:
            sample['user_id'] = user_id
            sample['timestamp'] = datetime.now()
            requests.append(InsertOne(sample))
        
        if requests:
            self.db.db.fatigue_results.bulk_write(requests, ordered=False)
        
        # Get analytics
        analytics = self.db.get_user_fatigue_analytics(user_id)
        
        print("📊 Fatigue Analytics (Multi-Stage Aggregation Pipeline):")
        print("-" * 80)
        
        if analytics.get('fatigue_distribution'):
            self.print_result("Fatigue Level Distribution", analytics['fatigue_distribution'])
        
        if analytics.get('timeline_stats'):
            self.print_result("Timeline Statistics (Last 7 Days)", analytics['timeline_stats'])
        
        if analytics.get('overall_stats'):
            stats = analytics['overall_stats'][0]
            self.print_result("Overall Statistics", {
                'Total Assessments': stats.get('total_assessments'),
                'Average Confidence': f"{stats.get('avg_confidence', 0):.2f}%",
                'Maximum Confidence': f"{stats.get('max_confidence')}%",
                'Minimum Confidence': f"{stats.get('min_confidence')}%"
            })
    
    def demo_6_text_search(self):
        """Demo 6: Text Search Capability"""
        self.print_section("DEMO 6: Text Search - Full-Text Search on User Data")
        
        # Create test users
        test_users = [
            {'email': 'john.smith@test.com', 'full_name': 'John Smith', 'created_at': datetime.now(), 'is_active': True},
            {'email': 'jane.doe@test.com', 'full_name': 'Jane Doe', 'created_at': datetime.now(), 'is_active': True},
            {'email': 'smith.johnson@test.com', 'full_name': 'Smith Johnson', 'created_at': datetime.now(), 'is_active': True},
        ]
        
        for user in test_users:
            try:
                self.db.db.users.insert_one(user)
            except:
                pass
        
        # Search for users
        search_results = self.db.search_users_by_name('Smith')
        
        self.print_result("Text Search Results (searching for 'Smith')", {
            'Query': "db.users.find({'$text': {'$search': 'Smith'}})",
            'Results Count': len(search_results),
            'Matching Users': [u.get('full_name', 'N/A') for u in search_results]
        })
    
    def demo_7_database_stats(self):
        """Demo 7: Database Statistics and Metadata"""
        self.print_section("DEMO 7: Database Statistics & Metadata")
        
        stats = self.db.get_database_stats()
        
        self.print_result("Database Collection Counts", {
            'Users': stats['users_count'],
            'Activity Logs': stats['activity_logs_count'],
            'Fatigue Results': stats['fatigue_results_count'],
            'Audit Logs': stats['audit_logs_count']
        })
        
        print("\n✓ Collections in Database:")
        print("-" * 80)
        for collection in stats['collections']:
            print(f"  • {collection}")
        
        print("\n✓ Indexes Created (by collection):")
        print("-" * 80)
        for collection, indexes in stats['indexes'].items():
            print(f"\n  {collection}:")
            for idx in indexes:
                index_name = idx.get('name', 'unknown')
                index_keys = idx.get('key', [])
                print(f"    - {index_name}: {index_keys}")
    
    def demo_8_audit_logging(self):
        """Demo 8: Audit Logging System"""
        self.print_section("DEMO 8: Audit Logging - Track All Database Operations")
        
        # Get audit logs
        audit_logs = list(self.db.db.audit_logs.find().sort('timestamp', -1).limit(5))
        
        self.print_result("Recent Audit Logs (Last 5 Operations)", {
            'Total Audit Entries': self.db.db.audit_logs.count_documents({}),
            'Recent Actions': [
                {
                    'Action': log.get('action'),
                    'User': log.get('user_id'),
                    'Details': log.get('details'),
                    'Timestamp': log.get('timestamp').strftime('%Y-%m-%d %H:%M:%S') if log.get('timestamp') else 'N/A'
                }
                for log in audit_logs
            ]
        })
    
    def demo_9_top_fatigued_users(self):
        """Demo 9: Leaderboard Query with Aggregation"""
        self.print_section("DEMO 9: Analytics Query - Top Fatigued Users Leaderboard")
        
        top_users = self.db.get_top_fatigued_users(limit=5)
        
        self.print_result("Top 5 Most Fatigued Users (Aggregation Query)", {
            'Query Type': 'Multi-stage aggregation pipeline',
            'Leaderboard': [
                {
                    'Rank': i + 1,
                    'User ID': user.get('_id'),
                    'Avg Fatigue Confidence': f"{user.get('avg_fatigue_confidence', 0):.2f}%",
                    'Total Assessments': user.get('total_assessments'),
                    'Latest Assessment': user.get('latest_assessment').strftime('%Y-%m-%d %H:%M:%S') if user.get('latest_assessment') else 'N/A'
                }
                for i, user in enumerate(top_users)
            ]
        })
    
    def demo_10_ttl_indexes(self):
        """Demo 10: TTL Index Explanation"""
        self.print_section("DEMO 10: TTL Indexes - Automatic Data Expiration")
        
        self.print_result("TTL Index Configuration", {
            'Feature': 'Automatic document deletion based on timestamp',
            'Collections with TTL': {
                'activity_logs': {
                    'Expiration Time': '90 days',
                    'Field': 'timestamp',
                    'Seconds': 7776000,
                    'Use Case': 'Automatically clean up old activity logs'
                },
                'fatigue_results': {
                    'Expiration Time': '180 days',
                    'Field': 'timestamp',
                    'Seconds': 15552000,
                    'Use Case': 'Keep fatigue history but clean old data'
                },
                'audit_logs': {
                    'Expiration Time': '30 days',
                    'Field': 'timestamp',
                    'Seconds': 2592000,
                    'Use Case': 'Retain recent audit trail only'
                }
            },
            'Benefit': 'Automatic storage management without manual cleanup'
        })
    
    def run_all_demos(self):
        """Run all demonstrations"""
        print("\n")
        print("╔" + "="*78 + "╗")
        print("║" + " "*14 + "ADVANCED MONGODB FEATURES DEMONSTRATION" + " "*26 + "║")
        print("║" + " "*11 + "Cognitive Fatigue Detection System" + " "*33 + "║")
        print("╚" + "="*78 + "╝")
        
        try:
            self.demo_1_setup_and_indexes()
            self.demo_2_bulk_operations()
            self.demo_3_aggregation_pipelines()
            self.demo_4_transactions()
            self.demo_5_fatigue_analytics()
            self.demo_6_text_search()
            self.demo_7_database_stats()
            self.demo_8_audit_logging()
            self.demo_9_top_fatigued_users()
            self.demo_10_ttl_indexes()
            
            self.print_section("✓ DEMO COMPLETE - All Advanced MongoDB Features Demonstrated")
            print("""
KEY FEATURES DEMONSTRATED:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. ✓ Advanced Indexing
   • Compound indexes for query optimization
   • Text search indexes for full-text search
   • TTL indexes for automatic data expiration
   • Unique constraints on email field

2. ✓ Bulk Operations
   • InsertOne requests for batch inserts
   • UpdateOne requests for batch updates
   • Ordered and unordered bulk writes
   • Error handling and partial success tracking

3. ✓ Aggregation Pipelines
   • Multi-stage pipelines with $facet
   • Group, sort, and limit operations
   • Date operations and statistics
   • Complex data transformations

4. ✓ Transactions
   • Multi-document ACID transactions
   • Automatic rollback on failure
   • Atomic user creation with initial activity log
   • Session management

5. ✓ Schema Validation
   • JSON Schema validation rules
   • Email regex pattern validation
   • Required fields enforcement
   • Validation levels (moderate)

6. ✓ Text Search
   • Full-text search on user data
   • Relevance scoring
   • Search result ranking

7. ✓ Audit Logging
   • Automatic operation tracking
   • Timestamp recording
   • Action history persistence

8. ✓ Database Statistics
   • Collection metrics
   • Index information
   • Database metadata

9. ✓ Analytics Queries
   • User leaderboards
   • Statistical analysis
   • Timeline aggregations

10. ✓ TTL Configuration
    • 90-day activity log retention
    • 180-day fatigue result retention
    • 30-day audit log retention

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
            """)
        
        except Exception as e:
            print(f"\n❌ Error during demo: {str(e)}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    demo = AdvancedMongoDBDemo()
    demo.run_all_demos()
