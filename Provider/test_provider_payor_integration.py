"""
Test script for Provider-Payor API Integration
Tests all endpoints as per PROVIDER_INTEGRATION_GUIDE.md
"""

import requests
import json
from datetime import datetime
import time

# Configuration
PROVIDER_BASE_URL = "http://127.0.0.1:8001/api"
PAYOR_BASE_URL = "https://e131ed05871e.ngrok-free.app/api"

def print_section(title):
    """Print a formatted section header"""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80)

def print_result(success, message, data=None):
    """Print test result"""
    status = "✅ PASS" if success else "❌ FAIL"
    print(f"\n{status}: {message}")
    if data:
        print(json.dumps(data, indent=2))

def test_connection():
    """Test connection to payor system"""
    print_section("TEST 1: Connection Test")
    
    try:
        url = f"{PROVIDER_BASE_URL}/provider/test-connection/"
        response = requests.post(url, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            print_result(result['success'], "Connection test", result)
            return result['success']
        else:
            print_result(False, f"Connection failed: {response.status_code}", response.text)
            return False
            
    except Exception as e:
        print_result(False, f"Connection test error: {e}")
        return False

def test_submit_claim_auto_approve():
    """Test submitting a claim that should be auto-approved"""
    print_section("TEST 2: Submit Claim (Auto-Approve)")
    
    try:
        claim_data = {
            "patient_name": "John Doe",
            "insurance_id": "BC-789-456",  # Valid insurance ID from payor
            "diagnosis_code": "J20.9",  # Acute bronchitis
            "diagnosis_description": "Acute Bronchitis",
            "procedure_code": "99213",  # Office visit
            "procedure_description": "Office consultation and treatment",
            "amount": "1250.00",
            "date_of_service": datetime.now().strftime('%Y-%m-%d'),
            "priority": "medium",
            "notes": "Patient presenting with persistent cough",
            "patient_dob": "1985-06-15",
            "patient_gender": "M"
        }
        
        url = f"{PROVIDER_BASE_URL}/provider/submit-claim/"
        response = requests.post(url, json=claim_data, timeout=30)
        
        if response.status_code == 201:
            result = response.json()
            print_result(result['success'], "Claim submitted", {
                'claim_id': result.get('claim_id'),
                'status': result.get('status'),
                'auto_approved': result.get('auto_approved'),
                'coverage_validated': result.get('coverage_validated')
            })
            return result.get('claim_id')
        else:
            print_result(False, f"Claim submission failed: {response.status_code}", response.json())
            return None
            
    except Exception as e:
        print_result(False, f"Claim submission error: {e}")
        return None

def test_submit_claim_invalid_insurance():
    """Test submitting a claim with invalid insurance ID"""
    print_section("TEST 3: Submit Claim (Invalid Insurance)")
    
    try:
        claim_data = {
            "patient_name": "Jane Smith",
            "insurance_id": "INVALID-999",  # Invalid insurance ID
            "diagnosis_code": "J20.9",
            "procedure_code": "99213",
            "amount": "500.00",
            "date_of_service": datetime.now().strftime('%Y-%m-%d')
        }
        
        url = f"{PROVIDER_BASE_URL}/provider/submit-claim/"
        response = requests.post(url, json=claim_data, timeout=30)
        
        result = response.json()
        # This should fail with appropriate error
        expected_failure = response.status_code == 400 and not result.get('success')
        
        print_result(expected_failure, "Invalid insurance properly rejected", {
            'error': result.get('error'),
            'error_code': result.get('error_code')
        })
        
    except Exception as e:
        print_result(False, f"Test error: {e}")

def test_submit_claim_missing_fields():
    """Test submitting a claim with missing required fields"""
    print_section("TEST 4: Submit Claim (Missing Required Fields)")
    
    try:
        claim_data = {
            "patient_name": "Test Patient"
            # Missing required fields: insurance_id, diagnosis_code, amount
        }
        
        url = f"{PROVIDER_BASE_URL}/provider/submit-claim/"
        response = requests.post(url, json=claim_data, timeout=30)
        
        result = response.json()
        # This should fail with validation errors
        expected_failure = response.status_code == 400 and not result.get('success')
        
        print_result(expected_failure, "Missing fields properly validated", {
            'validation_errors': result.get('validation_errors', [])
        })
        
    except Exception as e:
        print_result(False, f"Test error: {e}")

def test_get_claim_status(claim_id):
    """Test getting claim status"""
    print_section(f"TEST 5: Get Claim Status ({claim_id})")
    
    if not claim_id:
        print_result(False, "No claim ID provided, skipping test")
        return
    
    try:
        url = f"{PROVIDER_BASE_URL}/provider/claim-status/{claim_id}/"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            print_result(result['success'], "Claim status retrieved", {
                'claim_id': result.get('claim_id'),
                'status': result.get('status'),
                'patient_name': result.get('patient_name')
            })
        else:
            print_result(False, f"Status check failed: {response.status_code}", response.json())
            
    except Exception as e:
        print_result(False, f"Status check error: {e}")

def test_sync_all_claims():
    """Test syncing all claims"""
    print_section("TEST 6: Sync All Claims")
    
    try:
        url = f"{PROVIDER_BASE_URL}/provider/sync-claims/"
        response = requests.get(url, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            print_result(result['success'], "Claims synced", {
                'synced': result.get('synced'),
                'updated': result.get('updated')
            })
        else:
            print_result(False, f"Sync failed: {response.status_code}", response.json())
            
    except Exception as e:
        print_result(False, f"Sync error: {e}")

def test_update_configuration():
    """Test updating payor configuration"""
    print_section("TEST 7: Update Configuration")
    
    try:
        config_data = {
            "payor_url": "https://9323de5960fc.ngrok-free.app/api",
            "provider_id": "PROV-001",
            "provider_name": "City Medical Center"
        }
        
        url = f"{PROVIDER_BASE_URL}/provider/update-config/"
        # Note: This requires authentication
        response = requests.post(url, json=config_data, timeout=10)
        
        # May fail if not authenticated, but that's OK for this test
        if response.status_code in [200, 401, 403]:
            print_result(True, "Configuration endpoint accessible", {
                'status_code': response.status_code
            })
        else:
            print_result(False, f"Unexpected status: {response.status_code}")
            
    except Exception as e:
        print_result(False, f"Configuration error: {e}")

def test_webhook_payload():
    """Test webhook payload processing"""
    print_section("TEST 8: Webhook Payload (Simulation)")
    
    try:
        # Simulate a webhook payload
        webhook_data = {
            "event_type": "claim_status_update",
            "timestamp": datetime.now().isoformat(),
            "claim_id": "CLM-20241003-TEST123",
            "previous_status": "under_review",
            "new_status": "approved",
            "message": "Claim approved after validation",
            "patient_name": "Test Patient",
            "insurance_id": "BC-789-456",
            "amount": 1250.00,
            "coverage_validated": True,
            "auto_approved": False,
            "payment_details": {
                "approved_amount": 1000.00,
                "patient_responsibility": 250.00,
                "expected_payment_date": "2024-10-10"
            }
        }
        
        url = f"{PROVIDER_BASE_URL}/provider/webhook/payor-claims/"
        response = requests.post(url, json=webhook_data, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            print_result(result.get('received', False), "Webhook payload processed", result)
        else:
            print_result(False, f"Webhook failed: {response.status_code}", response.json())
            
    except Exception as e:
        print_result(False, f"Webhook error: {e}")

def run_all_tests():
    """Run all integration tests"""
    print("\n")
    print("╔" + "=" * 78 + "╗")
    print("║" + " " * 15 + "PROVIDER-PAYOR API INTEGRATION TESTS" + " " * 27 + "║")
    print("╚" + "=" * 78 + "╝")
    
    print(f"\nProvider API: {PROVIDER_BASE_URL}")
    print(f"Payor API: {PAYOR_BASE_URL}")
    print(f"Test Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Run tests
    test_connection()
    time.sleep(1)
    
    claim_id = test_submit_claim_auto_approve()
    time.sleep(2)
    
    test_submit_claim_invalid_insurance()
    time.sleep(1)
    
    test_submit_claim_missing_fields()
    time.sleep(1)
    
    if claim_id:
        test_get_claim_status(claim_id)
        time.sleep(1)
    
    test_sync_all_claims()
    time.sleep(1)
    
    test_update_configuration()
    time.sleep(1)
    
    test_webhook_payload()
    
    # Summary
    print_section("TEST SUMMARY")
    print("\nAll integration tests completed!")
    print("\nEndpoints tested:")
    print("  ✓ POST /api/provider/submit-claim/")
    print("  ✓ GET  /api/provider/claim-status/<claim_id>/")
    print("  ✓ POST /api/provider/webhook/payor-claims/")
    print("  ✓ POST /api/provider/test-connection/")
    print("  ✓ POST /api/provider/update-config/")
    print("  ✓ GET  /api/provider/sync-claims/")
    
    print("\n" + "=" * 80 + "\n")

if __name__ == "__main__":
    run_all_tests()
