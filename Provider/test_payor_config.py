"""
Quick test to verify payor integration fixes
Checks that configuration is now dynamic and using .env
"""

import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'provider.settings')
import django
django.setup()

from claims.payor_integration import payor_service
from django.conf import settings

print("=" * 80)
print("PAYOR INTEGRATION CONFIGURATION TEST")
print("=" * 80)

# Test 1: Check settings
print("\n1. Django Settings:")
print(f"   PAYOR_BASE_URL from settings: {getattr(settings, 'PAYOR_BASE_URL', 'NOT SET')}")

# Test 2: Check payor_service configuration
print("\n2. PayorIntegrationService Configuration:")
print(f"   Payor Base URL: {payor_service.payor_base_url}")
print(f"   Payor Email: {payor_service.payor_email}")

# Test 3: Check insurance mappings
print("\n3. Insurance Mappings (should use dynamic URL):")
for ins_id, mapping in payor_service.insurance_mappings.items():
    print(f"   {ins_id}: {mapping['payor_name']}")
    print(f"      URL: {mapping['payor_url']}")
    print(f"      Active: {mapping['is_active']}")

# Test 4: Verify all mappings use the same URL
print("\n4. URL Consistency Check:")
urls = set(mapping['payor_url'] for mapping in payor_service.insurance_mappings.values())
if len(urls) == 1:
    print(f"   ✅ All mappings use same URL: {list(urls)[0]}")
else:
    print(f"   ❌ Multiple URLs found: {urls}")

# Test 5: Check if using new ngrok URL
print("\n5. Ngrok URL Check:")
expected_url = "https://e131ed05871e.ngrok-free.app"
if payor_service.payor_base_url == expected_url:
    print(f"   ✅ Using new ngrok URL: {expected_url}")
elif "fd9b073ae920" in payor_service.payor_base_url:
    print(f"   ❌ Still using OLD ngrok URL: {payor_service.payor_base_url}")
    print("   ⚠️  RESTART THE DJANGO SERVER to load new configuration!")
else:
    print(f"   ℹ️  Using URL: {payor_service.payor_base_url}")

# Test 6: Check if BC-789-456 is mapped
print("\n6. John Doe Insurance ID Check:")
if 'BC-789-456' in payor_service.insurance_mappings:
    print(f"   ✅ BC-789-456 is mapped to: {payor_service.insurance_mappings['BC-789-456']['payor_name']}")
else:
    print(f"   ❌ BC-789-456 not found in mappings")

# Test 7: Test connection (optional - will fail if payor not configured)
print("\n7. Connection Test:")
try:
    result = payor_service.test_connection()
    if result.get('success'):
        print(f"   ✅ Connection successful: {result.get('message')}")
    else:
        print(f"   ⚠️  Connection failed: {result.get('message')}")
        print(f"   Note: Make sure payor system ALLOWED_HOSTS includes ngrok domain")
except Exception as e:
    print(f"   ⚠️  Connection test error: {str(e)}")
    print(f"   This is expected if payor system isn't running or ALLOWED_HOSTS not configured")

print("\n" + "=" * 80)
print("TEST COMPLETE")
print("=" * 80)

print("\n📋 Summary:")
print("   - Configuration should be loaded from .env")
print("   - All insurance mappings should use the same dynamic URL")
print("   - URL should be: https://e131ed05871e.ngrok-free.app")
print("\n⚠️  If still showing old URL, RESTART the Django server:")
print("   python manage.py runserver 0.0.0.0:8001")
