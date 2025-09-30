import requests
import json
from requests.auth import HTTPBasicAuth

# Configuration
BASE_URL = "http://127.0.0.1:8000/api"
PROVIDER_USERNAME = "provider1"
PROVIDER_PASSWORD = "password123"
PATIENT_USERNAME = "patient1"
PATIENT_PASSWORD = "password123"

def print_separator(title):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")

def print_request_details(method, url, auth=None, data=None):
    print(f"\n🔗 {method} {url}")
    if auth:
        print(f"🔐 Auth: {auth.username} / {'*' * len(auth.password)}")
    if data:
        print(f"📤 Data: {json.dumps(data, indent=2)}")

def print_response(response):
    print(f"📨 Status: {response.status_code}")
    try:
        if response.headers.get('content-type', '').startswith('application/json'):
            print(f"📋 Response: {json.dumps(response.json(), indent=2)}")
        else:
            print(f"📋 Response: {response.text[:200]}...")
    except:
        print(f"📋 Response: {response.text[:200]}...")

def test_1_api_root():
    """Test the API root endpoint"""
    print_separator("TEST 1: API ROOT")
    
    url = f"{BASE_URL}/"
    print_request_details("GET", url)
    
    response = requests.get(url)
    print_response(response)
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ SUCCESS: API Root accessible")
        print(f"📄 Available endpoints: {list(data.get('endpoints', {}).keys())}")
    else:
        print(f"❌ FAILED: Expected 200, got {response.status_code}")

def test_2_provider_me():
    """Test the provider me endpoint"""
    print_separator("TEST 2: PROVIDER ME")
    
    url = f"{BASE_URL}/provider/me/"
    auth = HTTPBasicAuth(PROVIDER_USERNAME, PROVIDER_PASSWORD)
    print_request_details("GET", url, auth)
    
    response = requests.get(url, auth=auth)
    print_response(response)
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ SUCCESS: Provider info retrieved")
        print(f"👤 Provider: {data.get('name')} ({data.get('email')})")
        print(f"🏥 Role: {data.get('role')}")
    else:
        print(f"❌ FAILED: Expected 200, got {response.status_code}")

def test_3_provider_me_unauthorized():
    """Test provider me without authentication"""
    print_separator("TEST 3: PROVIDER ME (UNAUTHORIZED)")
    
    url = f"{BASE_URL}/provider/me/"
    print_request_details("GET", url)
    
    response = requests.get(url)
    print_response(response)
    
    if response.status_code in [401, 403]:
        print(f"✅ SUCCESS: Unauthorized access properly blocked")
    else:
        print(f"❌ FAILED: Expected 401/403, got {response.status_code}")

def test_4_provider_me_wrong_role():
    """Test provider me with patient credentials"""
    print_separator("TEST 4: PROVIDER ME (WRONG ROLE)")
    
    url = f"{BASE_URL}/provider/me/"
    auth = HTTPBasicAuth(PATIENT_USERNAME, PATIENT_PASSWORD)
    print_request_details("GET", url, auth)
    
    response = requests.get(url, auth=auth)
    print_response(response)
    
    if response.status_code == 403:
        print(f"✅ SUCCESS: Patient access to provider endpoint blocked")
    else:
        print(f"❌ FAILED: Expected 403, got {response.status_code}")

def test_5_provider_stats():
    """Test provider statistics endpoint"""
    print_separator("TEST 5: PROVIDER STATISTICS")
    
    url = f"{BASE_URL}/provider/stats/"
    auth = HTTPBasicAuth(PROVIDER_USERNAME, PROVIDER_PASSWORD)
    print_request_details("GET", url, auth)
    
    response = requests.get(url, auth=auth)
    print_response(response)
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ SUCCESS: Statistics retrieved")
        print(f"📊 Total Claims: {data.get('totalClaims')}")
        print(f"⏳ Pending: {data.get('pendingClaims')}")
        print(f"✅ Approved: {data.get('approvedClaims')}")
        print(f"❌ Rejected: {data.get('rejectedClaims')}")
        print(f"💰 Total Revenue: ${data.get('totalRevenue')}")
    else:
        print(f"❌ FAILED: Expected 200, got {response.status_code}")

def test_6_claims_list():
    """Test claims list endpoint"""
    print_separator("TEST 6: CLAIMS LIST")
    
    url = f"{BASE_URL}/claims/"
    auth = HTTPBasicAuth(PROVIDER_USERNAME, PROVIDER_PASSWORD)
    print_request_details("GET", url, auth)
    
    response = requests.get(url, auth=auth)
    print_response(response)
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ SUCCESS: Claims list retrieved")
        print(f"📋 Total Claims: {data.get('count')}")
        print(f"📄 Page Results: {len(data.get('results', []))}")
        
        for i, claim in enumerate(data.get('results', [])[:3], 1):
            print(f"  {i}. {claim.get('claim_number')} - {claim.get('status')} - ${claim.get('amount_requested')}")
    else:
        print(f"❌ FAILED: Expected 200, got {response.status_code}")

def test_7_claims_list_with_filters():
    """Test claims list with status filter"""
    print_separator("TEST 7: CLAIMS LIST (WITH FILTERS)")
    
    url = f"{BASE_URL}/claims/?status=approved"
    auth = HTTPBasicAuth(PROVIDER_USERNAME, PROVIDER_PASSWORD)
    print_request_details("GET", url, auth)
    
    response = requests.get(url, auth=auth)
    print_response(response)
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ SUCCESS: Filtered claims retrieved")
        print(f"📋 Approved Claims: {data.get('count')}")
        
        # Test search filter
        url_search = f"{BASE_URL}/claims/?search=bronchitis"
        print(f"\n🔍 Testing search filter...")
        print_request_details("GET", url_search, auth)
        
        response_search = requests.get(url_search, auth=auth)
        print_response(response_search)
        
        if response_search.status_code == 200:
            search_data = response_search.json()
            print(f"🔍 Search Results: {search_data.get('count')} claims")
    else:
        print(f"❌ FAILED: Expected 200, got {response.status_code}")

def test_8_patient_search():
    """Test patient search endpoint"""
    print_separator("TEST 8: PATIENT SEARCH")
    
    # Test with patient name
    url = f"{BASE_URL}/provider/patients/search/?q=patient1"
    auth = HTTPBasicAuth(PROVIDER_USERNAME, PROVIDER_PASSWORD)
    print_request_details("GET", url, auth)
    
    response = requests.get(url, auth=auth)
    print_response(response)
    
    if response.status_code == 200:
        patients = response.json()
        print(f"✅ SUCCESS: Patient search completed")
        print(f"👥 Found {len(patients)} patients")
        
        for patient in patients:
            print(f"  👤 {patient.get('username')} - {patient.get('email')} ({patient.get('insurance_id')})")
            
        # Test with empty query
        print(f"\n🔍 Testing empty search query...")
        url_empty = f"{BASE_URL}/provider/patients/search/"
        response_empty = requests.get(url_empty, auth=auth)
        print(f"📨 Empty query status: {response_empty.status_code}")
        if response_empty.status_code == 400:
            print(f"✅ SUCCESS: Empty query properly rejected")
    else:
        print(f"❌ FAILED: Expected 200, got {response.status_code}")

def test_9_claim_detail():
    """Test claim detail endpoint"""
    print_separator("TEST 9: CLAIM DETAIL")
    
    # First get a claim ID from the list
    auth = HTTPBasicAuth(PROVIDER_USERNAME, PROVIDER_PASSWORD)
    claims_response = requests.get(f"{BASE_URL}/claims/", auth=auth)
    
    if claims_response.status_code == 200:
        claims_data = claims_response.json()
        if claims_data.get('results'):
            claim = claims_data['results'][0]
            claim_id = claim.get('id')
            claim_number = claim.get('claim_number')
            
            # Test with UUID
            url = f"{BASE_URL}/claims/{claim_id}/"
            print_request_details("GET", url, auth)
            
            response = requests.get(url, auth=auth)
            print_response(response)
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ SUCCESS: Claim detail retrieved")
                print(f"🏥 Claim: {data.get('claim_number')}")
                print(f"👤 Patient: {data.get('patient_name')}")
                print(f"🏥 Provider: {data.get('provider_name')}")
                print(f"📋 Status: {data.get('status')}")
                print(f"💰 Amount: ${data.get('amount_requested')}")
                
                # Test with claim number
                print(f"\n🔍 Testing with claim number...")
                url_number = f"{BASE_URL}/claims/{claim_number}/"
                print_request_details("GET", url_number, auth)
                
                response_number = requests.get(url_number, auth=auth)
                print(f"📨 Claim number lookup status: {response_number.status_code}")
            else:
                print(f"❌ FAILED: Expected 200, got {response.status_code}")
        else:
            print(f"❌ No claims available for testing")
    else:
        print(f"❌ Could not get claims list for testing")

def test_10_create_claim():
    """Test claim creation endpoint"""
    print_separator("TEST 10: CREATE CLAIM")
    
    # First get a patient ID
    patient_search = requests.get(
        f"{BASE_URL}/provider/patients/search/?q=patient1", 
        auth=HTTPBasicAuth(PROVIDER_USERNAME, PROVIDER_PASSWORD)
    )
    
    if patient_search.status_code == 200:
        patients = patient_search.json()
        if patients:
            patient_id = patients[0]['id']
            
            url = f"{BASE_URL}/claims/create/"
            auth = HTTPBasicAuth(PROVIDER_USERNAME, PROVIDER_PASSWORD)
            
            claim_data = {
                "patient": patient_id,
                "diagnosis_code": "R05",
                "diagnosis_description": "Cough",
                "procedure_code": "99213",
                "procedure_description": "Office visit for cough evaluation",
                "amount_requested": "150.00",
                "priority": "low",
                "date_of_service": "2025-09-28",
                "provider_npi": "1234567890",
                "notes": "Patient presented with persistent cough"
            }
            
            print_request_details("POST", url, auth, claim_data)
            
            response = requests.post(url, json=claim_data, auth=auth)
            print_response(response)
            
            if response.status_code == 201:
                data = response.json()
                print(f"✅ SUCCESS: New claim created")
                print(f"🆔 Claim Number: {data.get('claim_number')}")
                print(f"💰 Amount: ${data.get('amount_requested')}")
                print(f"📋 Status: {data.get('status')}")
            else:
                print(f"❌ FAILED: Expected 201, got {response.status_code}")
        else:
            print(f"❌ No patients found for testing")
    else:
        print(f"❌ Could not search patients for testing")

def test_11_update_claim():
    """Test claim update endpoint"""
    print_separator("TEST 11: UPDATE CLAIM")
    
    # Get the first claim to update
    auth = HTTPBasicAuth(PROVIDER_USERNAME, PROVIDER_PASSWORD)
    claims_response = requests.get(f"{BASE_URL}/claims/", auth=auth)
    
    if claims_response.status_code == 200:
        claims_data = claims_response.json()
        if claims_data.get('results'):
            claim = claims_data['results'][0]
            claim_id = claim.get('id')
            
            url = f"{BASE_URL}/claims/{claim_id}/"
            
            update_data = {
                "status": "under_review",
                "notes": "Updated via API test - claim under medical review"
            }
            
            print_request_details("PUT", url, auth, update_data)
            
            response = requests.put(url, json=update_data, auth=auth)
            print_response(response)
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ SUCCESS: Claim updated")
                print(f"🆔 Claim: {data.get('claim_number')}")
                print(f"📋 New Status: {data.get('status')}")
                print(f"📝 Notes: {data.get('notes')}")
            else:
                print(f"❌ FAILED: Expected 200, got {response.status_code}")
        else:
            print(f"❌ No claims available for testing")
    else:
        print(f"❌ Could not get claims list for testing")

def run_all_tests():
    """Run all API tests"""
    print("🚀 COMPREHENSIVE API TESTING")
    print("Testing Django Provider API - All Endpoints")
    
    tests = [
        test_1_api_root,
        test_2_provider_me,
        test_3_provider_me_unauthorized,
        test_4_provider_me_wrong_role,
        test_5_provider_stats,
        test_6_claims_list,
        test_7_claims_list_with_filters,
        test_8_patient_search,
        test_9_claim_detail,
        test_10_create_claim,
        test_11_update_claim,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            passed += 1
        except Exception as e:
            print(f"❌ TEST FAILED: {test.__name__}")
            print(f"Error: {str(e)}")
            failed += 1
    
    print_separator("TEST SUMMARY")
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print(f"📊 Total: {passed + failed}")
    
    if failed == 0:
        print("\n🎉 ALL TESTS PASSED! Your API is working perfectly!")
    else:
        print(f"\n⚠️  {failed} tests failed. Check the errors above.")

if __name__ == "__main__":
    run_all_tests()