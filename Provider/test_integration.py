#!/usr/bin/env python3
"""
Test script to check the Provider-Payor integration status
"""
import requests
import json

def test_payor_integration():
    """Test the payor integration endpoint"""
    print("🧪 Testing Provider-Payor Integration...\n")
    
    base_url = "http://127.0.0.1:8001"
    
    # Test 1: Health Check
    print("1️⃣ Testing Health Check...")
    try:
        response = requests.get(f"{base_url}/api/health/", timeout=10)
        if response.status_code == 200:
            print("✅ Health check passed")
            print(f"   Response: {response.json()}\n")
        else:
            print(f"❌ Health check failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Health check error: {e}\n")
    
    # Test 2: API Root
    print("2️⃣ Testing API Root...")
    try:
        response = requests.get(f"{base_url}/api/", timeout=10)
        if response.status_code == 200:
            print("✅ API root accessible")
            data = response.json()
            print(f"   Available endpoints: {list(data.get('endpoints', {}).keys())}\n")
        else:
            print(f"❌ API root failed: {response.status_code}")
    except Exception as e:
        print(f"❌ API root error: {e}\n")
    
    # Test 3: Payor Integration Status
    print("3️⃣ Testing Payor Integration Status...")
    try:
        response = requests.get(f"{base_url}/api/payor/integration/", timeout=10)
        if response.status_code == 200:
            print("✅ Payor integration endpoint accessible")
            data = response.json()
            print(f"   Connection Status: {data.get('connection_status', {}).get('success', 'Unknown')}")
            print(f"   Payor URL: {data.get('payor_config', {}).get('base_url', 'Not configured')}")
            print(f"   Insurance Mappings: {len(data.get('insurance_mappings', {}))}")
            print(f"   Insurance Policies: {len(data.get('insurance_policies', []))}\n")
        else:
            print(f"❌ Payor integration failed: {response.status_code}")
            if response.text:
                print(f"   Error: {response.text}")
    except Exception as e:
        print(f"❌ Payor integration error: {e}\n")
    
    # Test 4: Test Connection to Payor
    print("4️⃣ Testing Connection to Payor...")
    try:
        response = requests.post(f"{base_url}/api/provider/test-connection/", 
                               json={}, timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Connection test completed")
            print(f"   Success: {data.get('success', False)}")
            print(f"   Message: {data.get('message', 'No message')}\n")
        else:
            print(f"❌ Connection test failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Connection test error: {e}\n")

if __name__ == "__main__":
    test_payor_integration()