# """
# Test MongoDB connection and explore maintenancescheduler_db database
# """

# import sys
# import os

# # Add parent directory to path
# sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# from pymongo.mongo_client import MongoClient
# from pymongo.server_api import ServerApi
# from dotenv import load_dotenv
# from bson import ObjectId

# load_dotenv()

# def test_mongodb_connection():
#     """Test MongoDB connection and list specific collections"""
#     print("="*80)
#     print("MongoDB Connection Test - Specific Collections")
#     print("="*80)
    
#     # Get MongoDB URI from environment
#     mongo_uri = os.getenv("MONGO_URI")
    
#     if not mongo_uri:
#         print("❌ MONGO_URI not found in .env file")
#         return
    
#     print(f"✅ Found MONGO_URI in environment")
#     print(f"   Connecting to MongoDB cluster...")
    
#     try:
#         # Create MongoDB client
#         client = MongoClient(mongo_uri, server_api=ServerApi('1'))
        
#         # Test connection
#         client.admin.command('ping')
#         print("✅ Successfully connected to MongoDB!")
        
#         # Access the maintenancescheduler_db database
#         db = client["maintenancescheduler_db"]
#         print(f"\n✅ Accessed database: maintenancescheduler_db")
        
#         # The machine_id we're looking for (from InfluxDB/hourly_means collection)
#         target_machine_id = "68889e4d171eff841cba171a"
#         print(f"\n🔍 Searching for workspace with _id matching machine_id: {target_machine_id}")
        
#         # Define collections of interest
#         collections_of_interest = [
#             "users",
#             "workspaces"
#         ]
        
#         print(f"\n📊 Exploring {len(collections_of_interest)} collections:")
#         for idx, collection_name in enumerate(collections_of_interest, 1):
#             print(f"   {idx}. {collection_name}")
        
#         # Explore each collection
#         print("\n" + "="*80)
#         print("Collection Details")
#         print("="*80)
        
#         for collection_name in collections_of_interest:
#             collection = db[collection_name]
#             doc_count = collection.count_documents({})
            
#             print(f"\n📁 Collection: {collection_name}")
#             print(f"   Total Documents: {doc_count}")
            
#             if doc_count > 0:
#                 first_doc = collection.find_one()
                
#                 # Print Machine_ID if it exists in this collection
#                 if 'machine_id' in first_doc:
#                     print(f"\n   🏭 Machine_ID: {first_doc['machine_id']}")
                
#                 print(f"\n   First Document Fields:")
#                 print(f"   " + "-"*76)
                
#                 # List all fields and their types
#                 for field, value in first_doc.items():
#                     value_type = type(value).__name__
                    
#                     # Format value display
#                     if isinstance(value, (str, int, float, bool)):
#                         value_display = str(value)
#                         if len(value_display) > 50:
#                             value_display = value_display[:47] + "..."
#                     elif isinstance(value, list):
#                         value_display = f"[{len(value)} items]"
#                     elif isinstance(value, dict):
#                         value_display = f"{{dict with {len(value)} keys}}"
#                     else:
#                         value_display = str(value)[:50]
                    
#                     print(f"   • {field:30s} ({value_type:15s}): {value_display}")
                
#                 # Print full document in pretty format
#                 print(f"\n   Full First Document (JSON):")
#                 print(f"   " + "-"*76)
#                 import json
#                 from datetime import datetime
                
#                 # Convert ObjectId and datetime for JSON serialization
#                 def convert_for_json(obj):
#                     if isinstance(obj, ObjectId):
#                         return str(obj)
#                     elif isinstance(obj, datetime):
#                         return obj.isoformat()
#                     elif isinstance(obj, dict):
#                         return {k: convert_for_json(v) for k, v in obj.items()}
#                     elif isinstance(obj, list):
#                         return [convert_for_json(item) for item in obj]
#                     return obj
                
#                 json_doc = convert_for_json(first_doc)
#                 json_str = json.dumps(json_doc, indent=4)
                
#                 # Indent each line
#                 for line in json_str.split('\n'):
#                     print(f"   {line}")
#             else:
#                 print(f"   ⚠️ Collection is empty")
        
#         # Now search for workspace matching machine_id
#         print("\n" + "="*80)
#         print("Workspace Matching Machine ID")
#         print("="*80)
        
#         workspaces_collection = db["workspaces"]
#         users_collection = db["users"]
        
#         # Convert machine_id string to ObjectId for MongoDB query
#         try:
#             workspace_object_id = ObjectId(target_machine_id)
#             workspace = workspaces_collection.find_one({"_id": workspace_object_id})
            
#             if workspace:
#                 print(f"\n✅ Found workspace matching machine_id!")
#                 print(f"   Workspace Name: {workspace.get('name', 'N/A')}")
#                 print(f"   Workspace ID: {workspace['_id']}")
#                 print(f"   Description: {workspace.get('description', 'N/A')}")
#                 print(f"   Owner ID: {workspace.get('owner', 'N/A')}")
                
#                 # Get members from workspace
#                 members = workspace.get('members', [])
#                 print(f"\n👥 Associated Users ({len(members)} members):")
#                 print(f"   " + "-"*76)
                
#                 if members:
#                     for idx, member in enumerate(members, 1):
#                         user_id = member.get('user')
#                         role = member.get('role', 'Unknown')
#                         joined_at = member.get('joinedAt', 'N/A')
                        
#                         # Fetch user details from users collection
#                         user = users_collection.find_one({"_id": user_id})
                        
#                         if user:
#                             print(f"\n   {idx}. User Details:")
#                             print(f"      • User ID: {user_id}")
#                             print(f"      • Name: {user.get('name', 'N/A')}")
#                             print(f"      • Email: {user.get('email', 'N/A')}")
#                             print(f"      • Role in Workspace: {role}")
#                             print(f"      • Joined At: {joined_at}")
#                             print(f"      • Email Verified: {user.get('isEmailVerified', False)}")
#                             print(f"      • 2FA Enabled: {user.get('is2FAEnabled', False)}")
#                         else:
#                             print(f"\n   {idx}. ⚠️ User ID {user_id} not found in users collection")
#                             print(f"      • Role in Workspace: {role}")
#                             print(f"      • Joined At: {joined_at}")
#                 else:
#                     print(f"   ⚠️ No members found in this workspace")
                
#             else:
#                 print(f"\n❌ No workspace found with _id: {target_machine_id}")
#                 print(f"   Searched ObjectId: {workspace_object_id}")
                
#         except Exception as e:
#             print(f"\n❌ Error searching for workspace: {e}")
#             import traceback
#             traceback.print_exc()
        
#         # Close connection
#         client.close()
#         print("\n" + "="*80)
#         print("✅ MongoDB exploration completed successfully")
#         print("="*80)
        
#     except Exception as e:
#         print(f"❌ Error connecting to MongoDB: {e}")
#         import traceback
#         traceback.print_exc()

# if __name__ == "__main__":
#     test_mongodb_connection()

"""
Test email notification service independently
Run this to verify SendGrid configuration before full system test
"""

import sys
import os

# Add parent directory to path so we can import services module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from services.email_service import EmailNotificationService
from datetime import datetime

def test_normal_email():
    """Test sending a normal status email"""
    print("="*80)
    print("Testing NORMAL Status Email")
    print("="*80)
    
    email_service = EmailNotificationService()
    
    # Mock alert data for normal status
    alert_data = {
        "status": "normal",
        "message": "✅ Machine condition normal. All features within acceptable ranges.",
        "timestamp": datetime.now().isoformat(),
        "anomaly_scores": {
            "current": 5.23,
            "tempA": 8.15,
            "tempB": 6.77,
            "accX": 12.33,
            "accY": 9.45,
            "accZ": 15.67
        },
        "critical_features": [],
        "machine_id": "68889e4d171eff841cba171a"  # Real workspace ID from MongoDB
    }
    
    print(f"Machine ID: {alert_data['machine_id']}")
    print(f"Fetching workspace members...")
    
    success = email_service.send_alert_email(alert_data, inference_count=1)
    
    if success:
        print("\n✅ Normal status email sent successfully to all workspace members!")
    else:
        print("\n❌ Failed to send normal status email")
    
    return success

def test_critical_email():
    """Test sending a critical status email"""
    print("\n" + "="*80)
    print("Testing CRITICAL Status Email")
    print("="*80)
    
    email_service = EmailNotificationService()
    
    # Mock alert data for critical status
    alert_data = {
        "status": "critical",
        "message": "⚠️ Machine condition at risk. Critical features: tempA (45.23%), accZ (38.17%)",
        "timestamp": datetime.now().isoformat(),
        "anomaly_scores": {
            "current": 8.33,
            "tempA": 45.23,
            "tempB": 12.50,
            "accX": 15.00,
            "accY": 10.83,
            "accZ": 38.17
        },
        "critical_features": ["tempA", "accZ"],
        "machine_id": "68889e4d171eff841cba171a"  # Real workspace ID from MongoDB
    }
    
    print(f"Machine ID: {alert_data['machine_id']}")
    print(f"Fetching workspace members...")
    
    success = email_service.send_alert_email(alert_data, inference_count=2)
    
    if success:
        print("\n✅ Critical status email sent successfully to all workspace members!")
    else:
        print("\n❌ Failed to send critical status email")
    
    return success

if __name__ == "__main__":
    print("\n🔧 Email Notification Service Test Suite")
    print("="*80)
    print("Emails will be sent to all members of workspace: 68889e4d171eff841cba171a")
    print("="*80)
    
    # Test normal email
    normal_success = test_normal_email()
    
    # Wait a bit between emails
    import time
    time.sleep(2)
    
    # Test critical email
    critical_success = test_critical_email()
    
    # Summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    print(f"Normal Email:   {'✅ PASSED' if normal_success else '❌ FAILED'}")
    print(f"Critical Email: {'✅ PASSED' if critical_success else '❌ FAILED'}")
    
    if normal_success and critical_success:
        print("\n🎉 All email tests passed! Email service is working correctly.")
        print("Check inboxes of all workspace members for test emails.")
    else:
        print("\n⚠️ Some email tests failed. Check SendGrid API key and configuration.")