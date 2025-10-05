#!/usr/bin/env python3
"""
Test script for provider webhook endpoints
This script tests all the webhook endpoints to ensure they're working correctly
"""

import requests
import json
import sys
from datetime import datetime

# Configuration
PROVIDER_BASE_URL = "http://127.0.0.1:8001"
WEBHOOK_ENDPOINTS = {
    'health': '/api/webhooks/health/',
    'test': '/api/webhooks/test/',
    'claim_approved': '/api/webhooks/payor/claim-approved/',
    'claim_denied': '/api/webhooks/payor/claim-denied/',
    'claim_under_review': '/api/webhooks/payor/claim-under-review/',
    'generic': '/api/webhooks/payor/'
}

def test_health_endpoint():
    """Test the webhook health endpoint"""
    print("🔍 Testing webhook health endpoint...")
    
    try:
        url = f"{PROVIDER_BASE_URL}{WEBHOOK_ENDPOINTS['health']}"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Health check passed")
            print(f"   Status: {data.get('status')}")
            print(f"   Service: {data.get('service')}")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Health check error: {str(e)}")
        return False

def test_webhook_endpoint():
    """Test the test webhook endpoint"""
    print("\\n🧪 Testing webhook test endpoint...")
    
    test_payload = {
        "test": True,
        "message": "Test webhook from test script",
        "timestamp": datetime.now().isoformat()
    }
    
    try:
        url = f"{PROVIDER_BASE_URL}{WEBHOOK_ENDPOINTS['test']}"
        response = requests.post(
            url,
            json=test_payload,
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Test webhook passed")
            print(f"   Success: {data.get('success')}")
            print(f"   Message: {data.get('message')}")
            return True
        else:
            print(f"❌ Test webhook failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Test webhook error: {str(e)}")
        return False

def test_claim_approval_webhook():
    """Test claim approval webhook"""
    print("\\n✅ Testing claim approval webhook...")
    
    approval_payload = {
        "claim_id": "CLM-TEST-001",
        "provider_id": "PROV-001",
        "provider_name": "Test Medical Center",
        "patient_name": "Test Patient",
        "insurance_id": "TEST-123-456",
        "amount": 1250.00,
        "status": "approved",
        "approval_date": datetime.now().isoformat(),
        "approved_amount": 1000.00,
        "patient_responsibility": 250.00,
        "reason_code": "STANDARD_APPROVAL",
        "notes": "Test claim approval from webhook test",
        "reviewer_id": "test_system",
        "payor_reference": "CLM-TEST-001"
    }
    
    try:
        url = f"{PROVIDER_BASE_URL}{WEBHOOK_ENDPOINTS['claim_approved']}"
        response = requests.post(
            url,
            json=approval_payload,
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Claim approval webhook passed")
            print(f"   Success: {data.get('success')}")
            print(f"   Message: {data.get('message')}")
            return True
        else:
            data = response.json() if response.headers.get('content-type') == 'application/json' else response.text
            print(f"❌ Claim approval webhook failed: {response.status_code}")
            print(f"   Response: {data}")
            return False
            
    except Exception as e:
        print(f"❌ Claim approval webhook error: {str(e)}")
        return False

def test_claim_denial_webhook():
    """Test claim denial webhook"""
    print("\\n❌ Testing claim denial webhook...")
    
    denial_payload = {
        "claim_id": "CLM-TEST-002",
        "provider_id": "PROV-001",
        "provider_name": "Test Medical Center",
        "patient_name": "Test Patient 2",
        "insurance_id": "TEST-789-012",
        "amount": 2500.00,
        "status": "denied",
        "denial_date": datetime.now().isoformat(),
        "denial_reason": "INSUFFICIENT_DOCUMENTATION",
        "notes": "Test claim denial from webhook test - missing required docs",
        "reviewer_id": "test_system",
        "payor_reference": "CLM-TEST-002"
    }
    
    try:
        url = f"{PROVIDER_BASE_URL}{WEBHOOK_ENDPOINTS['claim_denied']}"
        response = requests.post(
            url,
            json=denial_payload,
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Claim denial webhook passed")
            print(f"   Success: {data.get('success')}")
            print(f"   Message: {data.get('message')}")
            return True
        else:
            data = response.json() if response.headers.get('content-type') == 'application/json' else response.text
            print(f"❌ Claim denial webhook failed: {response.status_code}")
            print(f"   Response: {data}")
            return False
            
    except Exception as e:
        print(f"❌ Claim denial webhook error: {str(e)}")
        return False

def test_claim_under_review_webhook():
    """Test claim under review webhook"""
    print("\\n🔍 Testing claim under review webhook...")
    
    review_payload = {
        "claim_id": "CLM-TEST-003",
        "provider_id": "PROV-001",
        "provider_name": "Test Medical Center",
        "patient_name": "Test Patient 3",
        "insurance_id": "TEST-345-678",
        "amount": 3500.00,
        "status": "under_review",
        "review_reason": "MANUAL_REVIEW_REQUIRED",
        "estimated_review_time": "24-48 hours",
        "notes": "Test claim under review from webhook test",
        "reviewer_contact": "test@payor.com",
        "reviewer_id": "test_system",
        "payor_reference": "CLM-TEST-003"
    }
    
    try:
        url = f"{PROVIDER_BASE_URL}{WEBHOOK_ENDPOINTS['claim_under_review']}"
        response = requests.post(
            url,
            json=review_payload,
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Claim under review webhook passed")
            print(f"   Success: {data.get('success')}")
            print(f"   Message: {data.get('message')}")
            return True
        else:
            data = response.json() if response.headers.get('content-type') == 'application/json' else response.text
            print(f"❌ Claim under review webhook failed: {response.status_code}")
            print(f"   Response: {data}")
            return False
            
    except Exception as e:
        print(f"❌ Claim under review webhook error: {str(e)}")
        return False

def test_generic_webhook():
    """Test generic webhook endpoint"""
    print("\\n🔄 Testing generic webhook endpoint...")
    
    generic_payload = {
        "event_type": "claim_status_update",
        "claim_id": "CLM-TEST-004",
        "new_status": "processing",
        "timestamp": datetime.now().isoformat(),
        "message": "Test generic webhook"
    }
    
    try:
        url = f"{PROVIDER_BASE_URL}{WEBHOOK_ENDPOINTS['generic']}"
        response = requests.post(
            url,
            json=generic_payload,
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Generic webhook passed")
            print(f"   Success: {data.get('success')}")
            print(f"   Message: {data.get('message')}")
            return True
        else:
            data = response.json() if response.headers.get('content-type') == 'application/json' else response.text
            print(f"❌ Generic webhook failed: {response.status_code}")
            print(f"   Response: {data}")
            return False
            
    except Exception as e:
        print(f"❌ Generic webhook error: {str(e)}")
        return False

def main():
    """Run all webhook tests"""
    print("🚀 Provider Webhook Endpoint Test Suite")
    print("="*50)
    
    # Check if provider server is running
    try:
        response = requests.get(f"{PROVIDER_BASE_URL}/api/health/", timeout=5)
        if response.status_code != 200:
            print(f"❌ Provider server not responding at {PROVIDER_BASE_URL}")
            print("   Please ensure the provider server is running:")
            print("   cd d:\\Provider\\integrationdemo\\Provider")
            print("   python manage.py runserver 8001")
            sys.exit(1)
    except Exception as e:
        print(f"❌ Cannot connect to provider server: {str(e)}")
        print("   Please ensure the provider server is running:")
        print("   cd d:\\Provider\\integrationdemo\\Provider")
        print("   python manage.py runserver 8001")
        sys.exit(1)
    
    print(f"✅ Provider server is running at {PROVIDER_BASE_URL}")
    
    # Run all tests
    tests = [
        test_health_endpoint,
        test_webhook_endpoint,
        test_claim_approval_webhook,
        test_claim_denial_webhook,
        test_claim_under_review_webhook,
        test_generic_webhook
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print("\\n" + "="*50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All webhook endpoints are working correctly!")
        print("\\n📋 Next steps:")
        print("   1. Configure payor system with provider webhook URL")
        print("   2. Test end-to-end claim flow")
        print("   3. Set up ngrok for external access")
    else:
        print("⚠️  Some webhook endpoints need attention")
        print("   Check the provider server logs for more details")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)