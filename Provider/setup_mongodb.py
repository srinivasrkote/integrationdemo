#!/usr/bin/env python3
"""
MongoDB Atlas Setup and Configuration Script for Provider Django App
"""

import os
import sys
import subprocess
from pathlib import Path

def install_requirements():
    """Install required Python packages"""
    print("Installing required packages...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ All packages installed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error installing packages: {e}")
        return False

def check_env_file():
    """Check if .env file exists and has required MongoDB settings"""
    env_path = Path('.env')
    if not env_path.exists():
        print("❌ .env file not found!")
        print("Please create a .env file with your MongoDB Atlas credentials.")
        return False
    
    # Read and check required variables
    required_vars = ['MONGO_DB_NAME', 'MONGO_HOST', 'MONGO_USER', 'MONGO_PASSWORD']
    missing_vars = []
    
    with open(env_path, 'r') as f:
        content = f.read()
        for var in required_vars:
            if f"{var}=" not in content:
                missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ Missing required environment variables: {', '.join(missing_vars)}")
        return False
    
    print("✅ .env file configured correctly!")
    return True

def test_mongodb_connection():
    """Test MongoDB Atlas connection"""
    try:
        import pymongo
        from decouple import config
        
        # Get MongoDB settings from .env file
        mongo_user = config('MONGO_USER')
        mongo_password = config('MONGO_PASSWORD')
        mongo_host = config('MONGO_HOST')
        mongo_db_name = config('MONGO_DB_NAME')
        
        # Create connection string
        connection_string = f"mongodb+srv://{mongo_user}:{mongo_password}@{mongo_host}/{mongo_db_name}?retryWrites=true&w=majority"
        
        # Test connection
        client = pymongo.MongoClient(connection_string, serverSelectionTimeoutMS=10000)
        client.server_info()  # Force connection test
        
        print("✅ MongoDB Atlas connection successful!")
        client.close()
        return True
        
    except Exception as e:
        print(f"❌ MongoDB Atlas connection failed: {e}")
        print("\nPlease check your MongoDB Atlas credentials in the .env file:")
        print("1. MONGO_HOST should be your cluster address (without mongodb+srv://)")
        print("2. MONGO_USER should be your database username")
        print("3. MONGO_PASSWORD should be your database password")
        print("4. MONGO_DB_NAME should be your database name")
        return False

def run_migrations():
    """Run Django migrations"""
    print("Running Django migrations...")
    try:
        subprocess.check_call([sys.executable, "manage.py", "migrate", "--run-syncdb"])
        print("✅ Migrations completed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Migration failed: {e}")
        return False

def create_sample_data():
    """Create sample data"""
    print("Creating sample data in MongoDB...")
    try:
        subprocess.check_call([sys.executable, "manage.py", "create_mongo_sample_data"])
        print("✅ Sample data created successfully in MongoDB!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Sample data creation failed: {e}")
        return False

def main():
    """Main setup function"""
    print("🚀 Setting up Provider Django App with MongoDB Atlas")
    print("=" * 50)
    
    # Step 1: Install requirements
    if not install_requirements():
        return False
    
    # Step 2: Check .env file
    if not check_env_file():
        return False
    
    # Step 3: Test MongoDB connection
    if not test_mongodb_connection():
        return False
    
    # Step 4: Run migrations
    if not run_migrations():
        return False
    
    # Step 5: Create sample data
    if not create_sample_data():
        return False
    
    print("\n🎉 Setup completed successfully!")
    print("You can now run the Django development server with:")
    print("python manage.py runserver")
    
    return True

if __name__ == "__main__":
    main()