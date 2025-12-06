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
        "machine_id": "68889e4d171eff841cba171a"
    }
    
    print(f"Machine ID: {alert_data['machine_id']}")
    
    success = email_service.send_alert_email(alert_data, inference_count=1)
    
    if success:
        print("\n✅ Normal status email sent successfully!")
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
        "machine_id": "68889e4d171eff841cba171a"
    }
    
    print(f"Machine ID: {alert_data['machine_id']}")
    
    success = email_service.send_alert_email(alert_data, inference_count=2)
    
    if success:
        print("\n✅ Critical status email sent successfully!")
    else:
        print("\n❌ Failed to send critical status email")
    
    return success

if __name__ == "__main__":
    print("\n🔧 Email Notification Service Test Suite")
    print("="*80)
    print("Recipient: adheeshagunathilake23@gmail.com")
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
    else:
        print("\n⚠️ Some email tests failed. Check SendGrid API key and configuration.")
