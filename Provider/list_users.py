#!/usr/bin/env python3
"""
List all users in the MongoDB database
"""
import os
import sys
import django

# Add the project directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'provider.settings')
django.setup()

from claims.mongo_models import User

def list_users():
    print("=== Users in MongoDB Database ===")
    print()
    
    users = User.objects().order_by('username')
    
    if not users:
        print("No users found in the database.")
        print("Please register new users through the registration form.")
        return
    
    print(f"Found {len(users)} users:")
    print("-" * 60)
    print(f"{'Username':<15} {'Email':<25} {'Role':<10} {'Active'}")
    print("-" * 60)
    
    for user in users:
        active_status = "✅ Yes" if user.is_active else "❌ No"
        print(f"{user.username:<15} {user.email:<25} {user.role:<10} {active_status}")
        
    print("-" * 60)
    print()
    print("💡 To login, use any of the above usernames with their corresponding passwords.")
    print("💡 If you don't know the password, use the 'Forgot Password' feature.")
    print("💡 To create new users, use the registration form on the website.")

if __name__ == '__main__':
    list_users()