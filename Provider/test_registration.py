import requests
import json

# Test the MongoDB registration endpoint
def test_registration():
    url = "http://127.0.0.1:8000/api/mongo/register-test/"
    
    test_user = {
        "username": "testuser123",
        "email": "testuser123@example.com",
        "password": "password123",
        "first_name": "Test",
        "last_name": "User",
        "role": "patient",
        "phone": "(555) 123-4567"
    }
    
    try:
        print("Testing registration endpoint...")
        print(f"URL: {url}")
        print(f"Data: {json.dumps(test_user, indent=2)}")
        
        response = requests.post(url, json=test_user, headers={
            'Content-Type': 'application/json'
        })
        
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        print(f"Response Text: {response.text}")
        
        if response.status_code == 201:
            print("✅ Registration successful!")
            data = response.json()
            print(f"User created: {data.get('user', {}).get('username')}")
        else:
            print(f"❌ Registration failed with status {response.status_code}")
            try:
                error_data = response.json()
                print(f"Error: {error_data.get('error')}")
            except:
                print(f"Raw response: {response.text}")
                
    except Exception as e:
        print(f"❌ Request failed: {str(e)}")

if __name__ == "__main__":
    test_registration()