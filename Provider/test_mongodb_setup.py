#!/usr/bin/env python3
"""
MongoDB Atlas Connection Test Script
Run this script to verify your MongoDB Atlas configuration
"""

import os
import sys
from pathlib import Path

# Add project directory to Python path
project_dir = Path(__file__).parent
sys.path.insert(0, str(project_dir))

# Set Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'provider.settings')

# Initialize Django
import django
django.setup()

def test_django_setup():
    """Test basic Django setup"""
    print("🔧 Testing Django setup...")
    try:
        from django.conf import settings
        print(f"✅ Django SECRET_KEY configured: {settings.SECRET_KEY[:10]}...")
        print(f"✅ Django DEBUG mode: {settings.DEBUG}")
        return True
    except Exception as e:
        print(f"❌ Django setup failed: {e}")
        return False

def test_mongodb_connection():
    """Test MongoDB Atlas connection"""
    print("\n🔗 Testing MongoDB Atlas connection...")
    try:
        import mongoengine
        from claims.mongo_models import User, Claim
        
        # Test connection by counting documents
        user_count = User.objects.count()
        claim_count = Claim.objects.count()
        
        print(f"✅ MongoDB connection successful!")
        print(f"✅ Users in database: {user_count}")
        print(f"✅ Claims in database: {claim_count}")
        return True
        
    except Exception as e:
        print(f"❌ MongoDB connection failed: {e}")
        print("💡 Please check your .env file with correct MongoDB Atlas credentials")
        return False

def test_sample_data():
    """Test sample data creation"""
    print("\n📊 Testing sample data...")
    try:
        from claims.mongo_models import User, Claim
        
        # Check for sample users
        provider = User.objects(username='provider1').first()
        patient = User.objects(username='patient1').first()
        
        if provider and patient:
            print(f"✅ Sample users found:")
            print(f"   - Provider: {provider.first_name} {provider.last_name}")
            print(f"   - Patient: {patient.first_name} {patient.last_name}")
        else:
            print("ℹ️  No sample data found. Run: python manage.py create_mongo_sample_data")
        
        # Check for sample claims
        claims = Claim.objects.limit(3)
        if claims:
            print(f"✅ Sample claims found:")
            for claim in claims:
                print(f"   - {claim.claim_number}: {claim.diagnosis_description[:30]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ Sample data test failed: {e}")
        return False

def test_api_imports():
    """Test API view imports"""
    print("\n🌐 Testing API components...")
    try:
        from claims.mongo_views import (
            MongoClaimListView, MongoClaimDetailView, 
            MongoUserListView, MongoAuthView
        )
        print("✅ MongoDB API views imported successfully")
        
        from claims.urls import urlpatterns
        mongo_endpoints = [url for url in urlpatterns if 'mongo' in str(url.pattern)]
        print(f"✅ MongoDB API endpoints registered: {len(mongo_endpoints)}")
        
        return True
        
    except Exception as e:
        print(f"❌ API components test failed: {e}")
        return False

def run_all_tests():
    """Run all tests"""
    print("🚀 MongoDB Atlas Setup Verification")
    print("=" * 50)
    
    tests = [
        ("Django Setup", test_django_setup),
        ("MongoDB Connection", test_mongodb_connection),
        ("Sample Data", test_sample_data),
        ("API Components", test_api_imports),
    ]
    
    results = []
    for test_name, test_func in tests:
        success = test_func()
        results.append((test_name, success))
    
    print("\n" + "=" * 50)
    print("📋 Test Results:")
    
    all_passed = True
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"   {status} - {test_name}")
        if not success:
            all_passed = False
    
    print("\n" + "=" * 50)
    if all_passed:
        print("🎉 All tests passed! Your MongoDB Atlas setup is working correctly!")
        print("\nNext steps:")
        print("1. Start the server: python manage.py runserver")
        print("2. Test the API: curl http://localhost:8000/api/mongo/claims/")
        print("3. Update your frontend to use the new MongoDB endpoints")
    else:
        print("⚠️  Some tests failed. Please check the error messages above.")
        print("\nTroubleshooting:")
        print("1. Verify your .env file has correct MongoDB Atlas credentials")
        print("2. Check your MongoDB Atlas cluster is running and accessible")
        print("3. Ensure all packages are installed: pip install -r requirements.txt")

if __name__ == "__main__":
    run_all_tests()