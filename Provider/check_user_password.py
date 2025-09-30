#!/usr/bin/env python
"""
Simple script to check user password in MongoDB
"""
import os
import sys
import django

# Add the provider directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'provider.settings')
django.setup()

from claims.mongo_models import User

def check_user_password():
    print("🔍 Checking user passwords in MongoDB...")
    
    # Find manju user
    user = User.objects(username='manju').first()
    if user:
        print(f"✅ Found user: {user.username}")
        print(f"📧 Email: {user.email}")
        print(f"🔑 Stored password: '{user.password}'")
        print(f"🎭 Role: {user.role}")
        print(f"🟢 Active: {user.is_active}")
    else:
        print("❌ User 'manju' not found in MongoDB")
        
    # List all users and their passwords
    print("\n📋 All users in MongoDB:")
    users = User.objects()
    for u in users:
        print(f"  {u.username}: password='{u.password}', role={u.role}, active={u.is_active}")

if __name__ == '__main__':
    check_user_password()