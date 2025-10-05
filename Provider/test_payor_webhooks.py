#!/usr/bin/env python3
"""
Test script to verify payor-to-provider webhook connectivity
Run this from your payor system to test webhook delivery
"""

import requests
import json
from datetime import datetime

def test_provider_webhook_endpoints():
    """Test all provider webhook endpoints"""
    
    # Provider system URL - UPDATE THIS
    PROVIDER_URL = "http://127.0.0.1:8000"
    
    print("=" * 60)
    print("TESTING PAYOR-TO-PROVIDER WEBHOOK CONNECTIVITY")
    print("=" * 60)
    
    # Test 1: Health Check
    print("\n1. Testing Provider Health Endpoint...")
    try:
        response = requests.get(f"{PROVIDER_URL}/api/webhooks/health/", timeout=10)
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.text}")
        if response.status_code == 200:
            print("   ✅ Health check PASSED")
        else:
            print("   ❌ Health check FAILED")
    except Exception as e:
        print(f"   ❌ Health check ERROR: {str(e)}")
    
    # Test 2: Claim Approval Webhook
    print("\n2. Testing Claim Approval Webhook...")
    approval_payload = {
        "claim_id": "TEST-CLAIM-001",
        "provider_id": "PROV-001",
        "provider_name": "City Medical Center",
        "patient_name": "John Doe",
        "insurance_id": "BC-789-456",
        "amount": 400.0,
        "status": "approved",
        "approval_date": datetime.now().isoformat(),
        "approved_amount": 400.0,
        "patient_responsibility": 0.0,
        "reason_code": "STANDARD_APPROVAL",
        "notes": "Test webhook from payor system",
        "reviewer_id": "test_user",
        "payor_reference": "PAYOR-REF-123",
        "event_type": "claim_approved",
        "timestamp": datetime.now().isoformat()
    }
    
    try:
        response = requests.post(
            f"{PROVIDER_URL}/api/webhooks/payor/claim-approved/",
            json=approval_payload,
            headers={
                "Content-Type": "application/json",
                "User-Agent": "PayorSystem/1.0 WebhookBot"
            },
            timeout=10
        )
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.text}")
        if response.status_code in [200, 201]:
            print("   ✅ Claim approval webhook PASSED")
        else:
            print("   ❌ Claim approval webhook FAILED")
    except Exception as e:
        print(f"   ❌ Claim approval webhook ERROR: {str(e)}")
    
    # Test 3: Claim Denial Webhook
    print("\n3. Testing Claim Denial Webhook...")
    denial_payload = {
        "claim_id": "TEST-CLAIM-002",
        "provider_id": "PROV-001",
        "provider_name": "City Medical Center", 
        "patient_name": "Jane Smith",
        "insurance_id": "BC-789-457",
        "amount": 300.0,
        "status": "denied",
        "denial_date": datetime.now().isoformat(),
        "denial_reason": "INSUFFICIENT_DOCUMENTATION",
        "notes": "Missing required medical records",
        "reviewer_id": "test_user",
        "payor_reference": "PAYOR-REF-124",
        "event_type": "claim_denied",
        "timestamp": datetime.now().isoformat()
    }
    
    try:
        response = requests.post(
            f"{PROVIDER_URL}/api/webhooks/payor/claim-denied/",
            json=denial_payload,
            headers={
                "Content-Type": "application/json",
                "User-Agent": "PayorSystem/1.0 WebhookBot"
            },
            timeout=10
        )
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.text}")
        if response.status_code in [200, 201]:
            print("   ✅ Claim denial webhook PASSED")
        else:
            print("   ❌ Claim denial webhook FAILED")
    except Exception as e:
        print(f"   ❌ Claim denial webhook ERROR: {str(e)}")
    
    # Test 4: Claim Under Review Webhook
    print("\n4. Testing Claim Under Review Webhook...")
    review_payload = {
        "claim_id": "TEST-CLAIM-003",
        "provider_id": "PROV-001",
        "provider_name": "City Medical Center",
        "patient_name": "Bob Johnson",
        "insurance_id": "BC-789-458",
        "amount": 500.0,
        "status": "under_review",
        "review_reason": "MANUAL_REVIEW_REQUIRED",
        "estimated_review_time": "24-48 hours",
        "notes": "Claim requires additional medical review",
        "reviewer_contact": "claims@payor.com",
        "reviewer_id": "test_user",
        "payor_reference": "PAYOR-REF-125",
        "event_type": "claim_under_review",
        "timestamp": datetime.now().isoformat()
    }
    
    try:
        response = requests.post(
            f"{PROVIDER_URL}/api/webhooks/payor/claim-under-review/",
            json=review_payload,
            headers={
                "Content-Type": "application/json",
                "User-Agent": "PayorSystem/1.0 WebhookBot"
            },
            timeout=10
        )
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.text}")
        if response.status_code in [200, 201]:
            print("   ✅ Claim under review webhook PASSED")
        else:
            print("   ❌ Claim under review webhook FAILED")
    except Exception as e:
        print(f"   ❌ Claim under review webhook ERROR: {str(e)}")
    
    print("\n" + "=" * 60)
    print("WEBHOOK TESTING COMPLETE")
    print("=" * 60)
    
    print("\nIf any tests failed:")
    print("1. Ensure provider system is running on http://127.0.0.1:8000")
    print("2. Check provider webhook endpoint URLs")
    print("3. Verify network connectivity")
    print("4. Check provider system logs for errors")

def test_webhook_with_real_claim():
    """Test webhook with a claim that actually exists in the provider system"""
    
    PROVIDER_URL = "http://127.0.0.1:8000"
    
    print("\n" + "=" * 60)
    print("TESTING WITH REALISTIC CLAIM DATA")
    print("=" * 60)
    
    # Use the claim data from your error log
    real_claim_payload = {
        "claim_id": "CLM-20251003-001",  # Use a realistic claim ID
        "provider_id": "PROV-001",
        "provider_name": "City Medical Center",
        "patient_name": "John Doe",
        "insurance_id": "BC-789-456",
        "amount": 400.0,
        "status": "approved",
        "approval_date": datetime.now().isoformat(),
        "approved_amount": 400.0,
        "patient_responsibility": 0.0,
        "reason_code": "STANDARD_APPROVAL",
        "notes": "Approved after payor review - Type 2 diabetes mellitus visit",
        "reviewer_id": "payor_reviewer_001",
        "payor_reference": "PAYOR-CLM-12345",
        "event_type": "claim_approved",
        "timestamp": datetime.now().isoformat(),
        # Additional fields that might help matching
        "diagnosis_code": "E11.9",
        "procedure_code": "99213",
        "date_of_service": "2025-10-01"
    }
    
    try:
        response = requests.post(
            f"{PROVIDER_URL}/api/webhooks/payor/claim-approved/",
            json=real_claim_payload,
            headers={
                "Content-Type": "application/json",
                "User-Agent": "PayorSystem/1.0 WebhookBot"
            },
            timeout=10
        )
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code in [200, 201]:
            print("✅ Realistic claim webhook SUCCESSFUL!")
            print("The provider should now show the claim as approved.")
        else:
            print("❌ Realistic claim webhook FAILED")
            print("Check if the claim exists in the provider system.")
            
    except Exception as e:
        print(f"❌ Realistic claim webhook ERROR: {str(e)}")

if __name__ == "__main__":
    test_provider_webhook_endpoints()
    test_webhook_with_real_claim()