"""
Test claim submission for BCBS member John Doe (MEM-BC-001)

This script creates and submits a claim for testing the provider-payor integration.
The claim uses real member data from the BCBS payor system.

Member Details:
- Member ID: MEM-BC-001
- Insurance ID: BC-789-456
- Policy: BC-789-456-123 (BlueCross Gold Plan)
- Medical Conditions: Type 2 Diabetes (E11.9), Hypertension (I10)
"""

import requests
import json
from datetime import datetime

# BCBS Member John Doe claim
claim_data = {
    "patient_name": "John Doe",
    "insurance_id": "BC-789-456",  # From member data
    "diagnosis_code": "E11.9",  # Type 2 Diabetes (primary condition)
    "diagnosis_description": "Type 2 diabetes mellitus without complications",
    "procedure_code": "99214",  # Office visit, established patient, moderate complexity
    "procedure_description": "Office visit for diabetes management with lab work",
    "amount": 450.00,  # Total charge: $250 (office visit) + $100 (HbA1c) + $100 (CMP)
    "date_of_service": "2025-10-01",
    "notes": "Routine diabetes follow-up. Secondary diagnosis: Hypertension (I10). Labs performed: HbA1c test (83036), Comprehensive metabolic panel (80053). Patient deductible met: $1200, OOP met: $2500"
}

def print_claim_summary(claim):
    """Print formatted claim summary"""
    print("=" * 80)
    print("CLAIM SUBMISSION TEST - JOHN DOE (BCBS MEMBER MEM-BC-001)")
    print("=" * 80)
    print(json.dumps(claim, indent=2))
    print("=" * 80)
    print(f"\nPatient: {claim['patient_name']}")
    print(f"Insurance ID: {claim['insurance_id']}")
    print(f"Policy: BC-789-456-123 (BlueCross Gold Plan)")
    print(f"Diagnosis: {claim['diagnosis_code']} - {claim['diagnosis_description']}")
    print(f"Procedure: {claim['procedure_code']} - {claim['procedure_description']}")
    print(f"Amount: ${claim['amount']}")
    print(f"Service Date: {claim['date_of_service']}")
    print("=" * 80)

def submit_claim(claim):
    """Submit claim to provider API"""
    url = "http://127.0.0.1:8001/api/provider/submit-claim/"
    
    print("\n[SUBMITTING CLAIM TO PROVIDER API]")
    print(f"URL: {url}")
    
    try:
        response = requests.post(url, json=claim, timeout=30)
        print(f"\nStatus Code: {response.status_code}")
        
        response_data = response.json()
        print(f"\nResponse Body:")
        print(json.dumps(response_data, indent=2))
        
        if response.status_code == 201:
            print("\n" + "=" * 80)
            print("[SUCCESS] Claim submitted successfully!")
            print("=" * 80)
            print(f"Provider Claim ID: {response_data.get('claim_id', 'N/A')}")
            print(f"Payor Claim ID: {response_data.get('payor_claim_id', 'N/A')}")
            print(f"Status: {response_data.get('status', 'N/A')}")
            print(f"Message: {response_data.get('message', 'N/A')}")
            print("=" * 80)
            return response_data
            
        elif response.status_code == 400:
            print("\n" + "=" * 80)
            print("[VALIDATION ERROR]")
            print("=" * 80)
            if 'validation_errors' in response_data:
                print("Required field errors:")
                for error in response_data['validation_errors']:
                    print(f"  - {error}")
            if 'validation_warnings' in response_data:
                print("\nWarnings:")
                for warning in response_data['validation_warnings']:
                    print(f"  - {warning}")
            if 'error' in response_data:
                print(f"\nError: {response_data['error']}")
            print("=" * 80)
            return None
            
        else:
            print(f"\n[UNEXPECTED STATUS] {response.status_code}")
            return None
            
    except requests.exceptions.ConnectionError:
        print("\n" + "=" * 80)
        print("[CONNECTION ERROR]")
        print("=" * 80)
        print("Cannot connect to Django server at port 8001")
        print("\nPlease ensure:")
        print("1. Django server is running: python manage.py runserver 0.0.0.0:8001")
        print("2. Server has been restarted to pick up .env changes")
        print("=" * 80)
        return None
        
    except Exception as e:
        print(f"\n[ERROR] {str(e)}")
        print(f"Error type: {type(e).__name__}")
        return None

def verify_claim_status(payor_claim_id):
    """Verify claim status in payor system"""
    if not payor_claim_id:
        return
    
    print("\n[VERIFYING CLAIM IN PAYOR SYSTEM]")
    status_url = f"http://127.0.0.1:8001/api/provider/claim-status/{payor_claim_id}/"
    print(f"URL: {status_url}")
    
    try:
        response = requests.get(status_url, timeout=10)
        print(f"Status Code: {response.status_code}")
        
        response_data = response.json()
        print(f"\nStatus Response:")
        print(json.dumps(response_data, indent=2))
        
        if response.status_code == 200 and response_data.get('success'):
            print("\n" + "=" * 80)
            print("[VERIFICATION SUCCESS]")
            print("=" * 80)
            claim_status = response_data.get('claim_status', {})
            print(f"Payor Claim ID: {claim_status.get('payor_claim_id', 'N/A')}")
            print(f"Status: {claim_status.get('status', 'N/A')}")
            print(f"Patient: {claim_status.get('patient_name', 'N/A')}")
            print(f"Amount: ${claim_status.get('amount', 'N/A')}")
            print("=" * 80)
        else:
            print("\n[VERIFICATION FAILED]")
            
    except Exception as e:
        print(f"\n[ERROR] Could not verify claim status: {str(e)}")

def main():
    """Main execution"""
    print_claim_summary(claim_data)
    
    result = submit_claim(claim_data)
    
    if result and result.get('success'):
        payor_claim_id = result.get('payor_claim_id')
        if payor_claim_id:
            verify_claim_status(payor_claim_id)
    
    print("\n" + "=" * 80)
    print("TEST COMPLETE")
    print("=" * 80)

if __name__ == "__main__":
    main()
