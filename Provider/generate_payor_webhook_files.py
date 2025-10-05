#!/usr/bin/env python3
"""
Quick setup script for adding webhook functionality to payor system
This script generates the necessary files for payor-to-provider webhook integration
"""

import os
import sys

def create_webhook_service_file():
    """Create the webhook service file for payor system"""
    content = '''"""
Payor Webhook Service for sending notifications to provider
Add this file to your payor system
"""

import requests
import json
import logging
from datetime import datetime
from django.conf import settings
import time

logger = logging.getLogger(__name__)

class ProviderWebhookService:
    """Service to send webhook notifications to provider systems"""
    
    def __init__(self):
        # Get provider webhook URL from settings or environment
        self.provider_base_url = getattr(settings, 'PROVIDER_WEBHOOK_URL', 'http://127.0.0.1:8001')
        self.timeout = 30
        self.retry_attempts = 3
        self.retry_delay = 5
    
    def send_claim_approval(self, claim_data):
        """Send claim approval notification to provider"""
        payload = {
            "claim_id": claim_data.get('claim_id'),
            "provider_id": claim_data.get('provider_id', 'PROV-001'),
            "provider_name": claim_data.get('provider_name', 'Provider System'),
            "patient_name": claim_data.get('patient_name'),
            "insurance_id": claim_data.get('insurance_id'),
            "amount": float(claim_data.get('amount', 0)),
            "status": "approved",
            "approval_date": datetime.now().isoformat(),
            "approved_amount": float(claim_data.get('approved_amount', claim_data.get('amount', 0))),
            "patient_responsibility": float(claim_data.get('patient_responsibility', 0)),
            "reason_code": claim_data.get('reason_code', 'STANDARD_APPROVAL'),
            "notes": claim_data.get('notes', 'Claim approved after review'),
            "reviewer_id": claim_data.get('reviewer_id', 'system'),
            "payor_reference": claim_data.get('claim_id')
        }
        
        return self._send_webhook('/api/webhooks/payor/claim-approved/', payload, 'claim_approval')
    
    def send_claim_denial(self, claim_data):
        """Send claim denial notification to provider"""
        payload = {
            "claim_id": claim_data.get('claim_id'),
            "provider_id": claim_data.get('provider_id', 'PROV-001'),
            "provider_name": claim_data.get('provider_name', 'Provider System'),
            "patient_name": claim_data.get('patient_name'),
            "insurance_id": claim_data.get('insurance_id'),
            "amount": float(claim_data.get('amount', 0)),
            "status": "denied",
            "denial_date": datetime.now().isoformat(),
            "denial_reason": claim_data.get('denial_reason', 'INSUFFICIENT_DOCUMENTATION'),
            "notes": claim_data.get('notes', 'Claim denied - missing required documentation'),
            "reviewer_id": claim_data.get('reviewer_id', 'system'),
            "payor_reference": claim_data.get('claim_id')
        }
        
        return self._send_webhook('/api/webhooks/payor/claim-denied/', payload, 'claim_denial')
    
    def _send_webhook(self, endpoint, payload, webhook_type):
        """Internal method to send webhook with retry logic"""
        url = f"{self.provider_base_url}{endpoint}"
        headers = {
            'Content-Type': 'application/json',
            'User-Agent': 'PayorSystem/1.0 WebhookBot'
        }
        
        for attempt in range(self.retry_attempts):
            try:
                logger.info(f"Sending {webhook_type} webhook to {url} (attempt {attempt + 1})")
                
                response = requests.post(
                    url,
                    json=payload,
                    headers=headers,
                    timeout=self.timeout
                )
                
                if response.status_code in [200, 201]:
                    logger.info(f"Webhook {webhook_type} sent successfully")
                    return {
                        'success': True,
                        'message': f'{webhook_type} webhook sent successfully',
                        'response': response.json(),
                        'attempt': attempt + 1
                    }
                else:
                    logger.warning(f"Webhook {webhook_type} failed with status {response.status_code}")
                    
                    if attempt == self.retry_attempts - 1:
                        return {
                            'success': False,
                            'error': f'HTTP {response.status_code}: {response.text}',
                            'attempts': attempt + 1
                        }
                
            except requests.RequestException as e:
                logger.error(f"Webhook {webhook_type} request failed (attempt {attempt + 1}): {str(e)}")
                
                if attempt == self.retry_attempts - 1:
                    return {
                        'success': False,
                        'error': f'Request failed after {self.retry_attempts} attempts: {str(e)}',
                        'attempts': attempt + 1
                    }
            
            # Wait before retry
            if attempt < self.retry_attempts - 1:
                time.sleep(self.retry_delay)
        
        return {
            'success': False,
            'error': 'All retry attempts failed'
        }

# Global service instance
webhook_service = ProviderWebhookService()
'''
    
    return content

def create_dashboard_integration_code():
    """Create code to integrate webhooks with payor dashboard"""
    content = '''"""
Add this code to your payor dashboard views to send webhooks
"""

from .webhook_service import webhook_service
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

@csrf_exempt
@require_http_methods(["POST"])
def approve_claim_with_webhook(request, claim_id):
    """Approve a claim and notify provider via webhook"""
    try:
        # Parse request data
        data = json.loads(request.body) if request.body else {}
        
        # Get claim from your database (replace with your logic)
        claim = get_claim_by_id(claim_id)  # Implement this function
        
        if not claim:
            return JsonResponse({
                'success': False,
                'error': f'Claim not found: {claim_id}'
            }, status=404)
        
        # Update claim status in your database
        claim.status = 'approved'
        claim.approved_amount = data.get('approved_amount', claim.amount)
        claim.patient_responsibility = data.get('patient_responsibility', 0)
        claim.notes = data.get('notes', 'Claim approved via dashboard')
        claim.save()  # Use your save method
        
        # Prepare webhook data
        webhook_data = {
            'claim_id': claim.claim_id,  # Use your claim ID field
            'provider_id': getattr(claim, 'provider_id', 'PROV-001'),
            'provider_name': getattr(claim, 'provider_name', 'Provider System'),
            'patient_name': claim.patient_name,
            'insurance_id': getattr(claim, 'insurance_id', ''),
            'amount': float(claim.amount),
            'approved_amount': float(claim.approved_amount),
            'patient_responsibility': float(claim.patient_responsibility),
            'reason_code': 'APPROVED_DASHBOARD',
            'notes': claim.notes,
            'reviewer_id': 'dashboard_user'
        }
        
        # Send webhook notification
        webhook_result = webhook_service.send_claim_approval(webhook_data)
        
        return JsonResponse({
            'success': True,
            'message': 'Claim approved successfully',
            'claim_id': claim_id,
            'webhook_sent': webhook_result['success'],
            'webhook_message': webhook_result.get('message', webhook_result.get('error'))
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Failed to approve claim: {str(e)}'
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def deny_claim_with_webhook(request, claim_id):
    """Deny a claim and notify provider via webhook"""
    try:
        # Parse request data
        data = json.loads(request.body) if request.body else {}
        
        # Get claim from your database (replace with your logic)
        claim = get_claim_by_id(claim_id)  # Implement this function
        
        if not claim:
            return JsonResponse({
                'success': False,
                'error': f'Claim not found: {claim_id}'
            }, status=404)
        
        # Update claim status in your database
        claim.status = 'denied'
        claim.denial_reason = data.get('denial_reason', 'INSUFFICIENT_DOCUMENTATION')
        claim.notes = data.get('notes', 'Claim denied via dashboard')
        claim.save()  # Use your save method
        
        # Prepare webhook data
        webhook_data = {
            'claim_id': claim.claim_id,  # Use your claim ID field
            'provider_id': getattr(claim, 'provider_id', 'PROV-001'),
            'provider_name': getattr(claim, 'provider_name', 'Provider System'),
            'patient_name': claim.patient_name,
            'insurance_id': getattr(claim, 'insurance_id', ''),
            'amount': float(claim.amount),
            'denial_reason': claim.denial_reason,
            'notes': claim.notes,
            'reviewer_id': 'dashboard_user'
        }
        
        # Send webhook notification
        webhook_result = webhook_service.send_claim_denial(webhook_data)
        
        return JsonResponse({
            'success': True,
            'message': 'Claim denied successfully',
            'claim_id': claim_id,
            'webhook_sent': webhook_result['success'],
            'webhook_message': webhook_result.get('message', webhook_result.get('error'))
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Failed to deny claim: {str(e)}'
        }, status=500)


def get_claim_by_id(claim_id):
    """
    Replace this with your actual claim retrieval logic
    Example for different ORMs:
    
    # Django ORM:
    from .models import Claim
    return Claim.objects.get(id=claim_id)
    
    # MongoEngine:
    from .models import Claim
    return Claim.objects(claim_id=claim_id).first()
    
    # Raw MongoDB:
    from pymongo import MongoClient
    client = MongoClient()
    db = client.your_database
    return db.claims.find_one({'claim_id': claim_id})
    """
    # Placeholder - implement based on your database setup
    pass
'''
    
    return content

def create_frontend_integration_code():
    """Create JavaScript code for payor dashboard frontend"""
    content = '''/*
Add this JavaScript code to your payor dashboard frontend
*/

class PayorDashboardWebhooks {
    constructor(baseUrl = '/api') {
        this.baseUrl = baseUrl;
    }
    
    async approveClaim(claimId, approvedAmount, patientResponsibility, notes) {
        try {
            const response = await fetch(`${this.baseUrl}/claims/${claimId}/approve-webhook/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCsrfToken()
                },
                body: JSON.stringify({
                    approved_amount: approvedAmount,
                    patient_responsibility: patientResponsibility,
                    notes: notes
                })
            });
            
            const result = await response.json();
            
            if (result.success) {
                this.showNotification(
                    `Claim ${claimId} approved. ${result.webhook_sent ? 'Provider notified.' : 'Provider notification failed.'}`, 
                    'success'
                );
                this.refreshClaimsList();
            } else {
                this.showNotification(`Error: ${result.error}`, 'error');
            }
            
            return result;
        } catch (error) {
            this.showNotification(`Failed to approve claim: ${error.message}`, 'error');
            throw error;
        }
    }
    
    async denyClaim(claimId, denialReason, notes) {
        try {
            const response = await fetch(`${this.baseUrl}/claims/${claimId}/deny-webhook/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCsrfToken()
                },
                body: JSON.stringify({
                    denial_reason: denialReason,
                    notes: notes
                })
            });
            
            const result = await response.json();
            
            if (result.success) {
                this.showNotification(
                    `Claim ${claimId} denied. ${result.webhook_sent ? 'Provider notified.' : 'Provider notification failed.'}`, 
                    'success'
                );
                this.refreshClaimsList();
            } else {
                this.showNotification(`Error: ${result.error}`, 'error');
            }
            
            return result;
        } catch (error) {
            this.showNotification(`Failed to deny claim: ${error.message}`, 'error');
            throw error;
        }
    }
    
    getCsrfToken() {
        const token = document.querySelector('[name=csrfmiddlewaretoken]');
        return token ? token.value : '';
    }
    
    showNotification(message, type) {
        // Replace with your notification system
        console.log(`${type.toUpperCase()}: ${message}`);
        alert(message); // Simple fallback
    }
    
    refreshClaimsList() {
        // Replace with your claims list refresh logic
        location.reload(); // Simple fallback
    }
}

// Initialize dashboard
const dashboardWebhooks = new PayorDashboardWebhooks();

// Example usage in your HTML:
/*
<button onclick="approveClaim('CLM-123', 1000, 250, 'Approved via dashboard')">
    Approve Claim
</button>

<button onclick="denyClaim('CLM-123', 'INSUFFICIENT_DOCUMENTATION', 'Missing lab reports')">
    Deny Claim
</button>

<script>
function approveClaim(claimId, approvedAmount, patientResponsibility, notes) {
    dashboardWebhooks.approveClaim(claimId, approvedAmount, patientResponsibility, notes);
}

function denyClaim(claimId, denialReason, notes) {
    dashboardWebhooks.denyClaim(claimId, denialReason, notes);
}
</script>
*/
'''
    
    return content

def create_settings_template():
    """Create settings template for payor system"""
    content = '''# Add these settings to your payor system's settings.py

# Provider Webhook Configuration
PROVIDER_WEBHOOK_URL = 'http://127.0.0.1:8001'  # Local development
# PROVIDER_WEBHOOK_URL = 'https://provider-ngrok-url.ngrok-free.app'  # For ngrok

# Webhook settings
WEBHOOK_TIMEOUT = 30
WEBHOOK_RETRY_ATTEMPTS = 3
WEBHOOK_RETRY_DELAY = 5

# Logging configuration for webhooks
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'webhook_file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': 'webhook.log',
        },
    },
    'loggers': {
        'webhook_service': {
            'handlers': ['webhook_file'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}
'''
    
    return content

def create_urls_template():
    """Create URL patterns for payor system"""
    content = '''# Add these URL patterns to your payor system's urls.py

from django.urls import path
from . import webhook_views  # Your webhook views file

urlpatterns = [
    # ... your existing URLs ...
    
    # Webhook-enabled claim decision endpoints
    path('api/claims/<str:claim_id>/approve-webhook/', webhook_views.approve_claim_with_webhook, name='approve-claim-webhook'),
    path('api/claims/<str:claim_id>/deny-webhook/', webhook_views.deny_claim_with_webhook, name='deny-claim-webhook'),
]
'''
    
    return content

def main():
    """Generate all webhook integration files"""
    print("🚀 Payor Webhook Integration Setup Generator")
    print("="*50)
    
    # Create output directory
    output_dir = "payor_webhook_integration"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"📁 Created directory: {output_dir}")
    
    files_to_create = [
        ("webhook_service.py", create_webhook_service_file()),
        ("webhook_views.py", create_dashboard_integration_code()),
        ("webhook_frontend.js", create_frontend_integration_code()),
        ("webhook_settings.py", create_settings_template()),
        ("webhook_urls.py", create_urls_template())
    ]
    
    print("\\n📝 Creating webhook integration files...")
    
    for filename, content in files_to_create:
        filepath = os.path.join(output_dir, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✅ Created: {filepath}")
    
    # Create README
    readme_content = """# Payor Webhook Integration Files

This directory contains all the files needed to add webhook functionality to your payor system.

## Setup Instructions:

1. **Copy webhook_service.py** to your payor project directory
2. **Integrate webhook_views.py** code into your existing views
3. **Add webhook_frontend.js** to your dashboard frontend
4. **Add webhook_settings.py** settings to your settings.py
5. **Add webhook_urls.py** patterns to your urls.py

## Configuration:

1. Update PROVIDER_WEBHOOK_URL in settings to your provider's ngrok URL
2. Test webhook connectivity using the provided endpoints
3. Update your dashboard buttons to use the new webhook-enabled endpoints

## Files:

- `webhook_service.py` - Core webhook service for sending notifications
- `webhook_views.py` - Django views with webhook integration
- `webhook_frontend.js` - JavaScript for dashboard integration
- `webhook_settings.py` - Settings template
- `webhook_urls.py` - URL patterns template

## Testing:

Use the test_webhooks.py script in the provider system to verify webhooks are working.
"""
    
    readme_path = os.path.join(output_dir, "README.md")
    with open(readme_path, 'w', encoding='utf-8') as f:
        f.write(readme_content)
    print(f"✅ Created: {readme_path}")
    
    print("\\n🎉 Webhook integration files generated successfully!")
    print(f"\\n📁 All files are in: {output_dir}/")
    print("\\n📋 Next steps:")
    print("   1. Copy these files to your payor system")
    print("   2. Follow the setup instructions in README.md")
    print("   3. Configure provider webhook URL in settings")
    print("   4. Test the webhook integration")
    print("   5. Update your dashboard to use webhook-enabled endpoints")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)