"""
Test script for Provider API endpoints
"""
import requests
import json
from requests.auth import HTTPBasicAuth

# Base URL for the API
BASE_URL = "http://127.0.0.1:8000/api"

# Test credentials
PROVIDER_USERNAME = "provider1"
PROVIDER_PASSWORD = "password123"

def test_api_root():
    """Test the API root endpoint"""
    print("Testing API root...")
    response = requests.get(f"{BASE_URL}/")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    print()

def test_provider_me():
    """Test the provider me endpoint"""
    print("Testing Provider Me endpoint...")
    auth = HTTPBasicAuth(PROVIDER_USERNAME, PROVIDER_PASSWORD)
    response = requests.get(f"{BASE_URL}/provider/me/", auth=auth)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    else:
        print(f"Error: {response.text}")
    print()

def test_claims_list():
    """Test the claims list endpoint"""
    print("Testing Claims List endpoint...")
    auth = HTTPBasicAuth(PROVIDER_USERNAME, PROVIDER_PASSWORD)
    response = requests.get(f"{BASE_URL}/claims/", auth=auth)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        # Handle paginated response
        if 'results' in data:
            claims = data['results']
            print(f"Found {data['count']} total claims, showing {len(claims)}")
        else:
            claims = data
            print(f"Found {len(claims)} claims")
        
        for claim in claims:
            print(f"- {claim['claim_number']}: {claim['diagnosis_description'][:50]}... ({claim['status']})")
    else:
        print(f"Error: {response.text}")
    print()

def test_provider_stats():
    """Test the provider stats endpoint"""
    print("Testing Provider Stats endpoint...")
    auth = HTTPBasicAuth(PROVIDER_USERNAME, PROVIDER_PASSWORD)
    response = requests.get(f"{BASE_URL}/provider/stats/", auth=auth)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    else:
        print(f"Error: {response.text}")
    print()

def test_patient_search():
    """Test the patient search endpoint"""
    print("Testing Patient Search endpoint...")
    auth = HTTPBasicAuth(PROVIDER_USERNAME, PROVIDER_PASSWORD)
    response = requests.get(f"{BASE_URL}/provider/patients/search/?q=patient1", auth=auth)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        patients = response.json()
        print(f"Found {len(patients)} patients")
        for patient in patients:
            print(f"- {patient['username']}: {patient['email']} (Role: {patient['role']})")
    else:
        print(f"Error: {response.text}")
    print()

if __name__ == "__main__":
    print("Starting Provider API Tests...")
    print("=" * 50)
    
    test_api_root()
    test_provider_me()
    test_claims_list()
    test_provider_stats()
    test_patient_search()
    
    print("Tests completed!")