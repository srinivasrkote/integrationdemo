#!/usr/bin/env python3
"""
Quick Test Script for Provider System (Local Development)
Tests the complete workflow without ngrok
"""

import requests
import json
import time
from datetime import datetime

def test_system_status():
    """Test if both backend and frontend are running"""
    print("🔍 Testing System Status...")
    
    # Test Django Backend
    try:
        response = requests.get("http://127.0.0.1:8000/api/webhooks/health/", timeout=5)
        if response.status_code == 200:
            print("✅ Django Backend: Running on http://127.0.0.1:8000")
        else:
            print(f"❌ Django Backend: Error {response.status_code}")
    except requests.RequestException as e:
        print(f"❌ Django Backend: Not running - {str(e)}")
    
    # Test React Frontend (try common ports)
    frontend_ports = [3001, 3002, 5173]
    frontend_running = False
    
    for port in frontend_ports:
        try:
            response = requests.get(f"http://localhost:{port}", timeout=3)
            if response.status_code == 200:
                print(f"✅ React Frontend: Running on http://localhost:{port}")
                frontend_running = True
                break
        except requests.RequestException:
            continue
    
    if not frontend_running:
        print("❌ React Frontend: Not running")
    
    print()

def test_complete_workflow():
    """Test the complete claim submission and webhook workflow"""
    print("🧪 Testing Complete Workflow...")
    
    # Step 1: Submit a test claim
    print("\n1. Submitting test claim...")
    
    claim_data = {
        "patient_name": "John Doe Test",
        "insurance_id": "TEST-12345",
        "diagnosis_codes": [
            {"code": "E11.9", "description": "Type 2 diabetes mellitus without complications"}
        ],
        "procedure_codes": [
            {"code": "99213", "description": "Office visit, established patient"}
        ],
        "amount_requested": 150.00,
        "date_of_service": "2025-10-03",
        "notes": "Test claim submission",
        "priority": "medium"
    }
    
    try:
        response = requests.post(
            "http://127.0.0.1:8000/api/provider/submit-claim/",
            json=claim_data,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        if response.status_code in [200, 201]:
            result = response.json()
            claim_id = result.get('claim_id', 'UNKNOWN')
            print(f"✅ Claim submitted successfully: {claim_id}")
            
            # Step 2: Simulate payor approval
            print(f"\n2. Simulating payor approval for claim {claim_id}...")
            
            approval_payload = {
                "claim_id": claim_id,
                "provider_id": "PROV-001",
                "patient_name": "John Doe Test",
                "insurance_id": "TEST-12345",
                "amount": 150.00,
                "status": "approved",
                "approval_date": datetime.now().isoformat(),
                "approved_amount": 150.00,
                "patient_responsibility": 0.00,
                "reason_code": "STANDARD_APPROVAL",
                "notes": "Test approval via webhook",
                "reviewer_id": "test_system",
                "event_type": "claim_approved",
                "timestamp": datetime.now().isoformat()
            }
            
            webhook_response = requests.post(
                "http://127.0.0.1:8000/api/webhooks/payor/claim-approved/",
                json=approval_payload,
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            if webhook_response.status_code in [200, 201]:
                print("✅ Webhook delivered successfully")
                print("✅ Claim should now show as 'approved' in provider dashboard")
                
                # Step 3: Verify claim status
                print(f"\n3. Verifying claim status...")
                
                claims_response = requests.get(
                    "http://127.0.0.1:8000/api/mongo/claims/",
                    timeout=10
                )
                
                if claims_response.status_code == 200:
                    claims = claims_response.json()
                    recent_claims = claims.get('results', claims) if isinstance(claims, dict) else claims
                    
                    # Find our test claim
                    test_claim = None
                    for claim in recent_claims[:5]:  # Check last 5 claims
                        if claim.get('patient_name') == "John Doe Test":
                            test_claim = claim
                            break
                    
                    if test_claim:
                        status = test_claim.get('status', 'unknown')
                        amount = test_claim.get('approved_amount', test_claim.get('amount_requested', 0))
                        print(f"✅ Claim found: Status = {status}, Amount = ${amount}")
                        
                        if status == 'approved':
                            print("🎉 WORKFLOW TEST PASSED!")
                            print("   → Claim submitted")
                            print("   → Payor webhook received")
                            print("   → Status updated to approved")
                            print("   → Provider dashboard will show updated status")
                        else:
                            print(f"⚠️  Claim status is '{status}', expected 'approved'")
                    else:
                        print("❌ Test claim not found in recent claims")
                else:
                    print(f"❌ Failed to fetch claims: {claims_response.status_code}")
                    
            else:
                print(f"❌ Webhook delivery failed: {webhook_response.status_code}")
                print(f"   Response: {webhook_response.text}")
                
        else:
            print(f"❌ Claim submission failed: {response.status_code}")
            print(f"   Response: {response.text}")
            
    except requests.RequestException as e:
        print(f"❌ Workflow test failed: {str(e)}")

def main():
    print("=" * 60)
    print("PROVIDER SYSTEM LOCAL TEST")
    print("=" * 60)
    
    test_system_status()
    
    # Ask user if they want to run workflow test
    print("Do you want to run the complete workflow test?")
    print("This will:")
    print("  1. Submit a test claim")
    print("  2. Simulate payor approval")
    print("  3. Verify the status update")
    print()
    
    answer = input("Run workflow test? (y/N): ").lower().strip()
    
    if answer in ['y', 'yes']:
        test_complete_workflow()
    else:
        print("Skipping workflow test.")
    
    print("\n" + "=" * 60)
    print("TESTING COMPLETE")
    print("=" * 60)
    print("\nNext steps:")
    print("1. Open http://localhost:3001 or http://localhost:3002 (frontend)")
    print("2. Login with: username=testuser, password=testpass123")
    print("3. Submit claims and see them in 'Recent Claims'")
    print("4. Run this test script to simulate payor approvals")

if __name__ == "__main__":
    main()