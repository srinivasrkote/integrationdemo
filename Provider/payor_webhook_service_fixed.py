"""
Payor Webhook Service (FIXED VERSION)
Sends notifications to provider systems about claim decisions
"""
import requests
import json
import logging
from datetime import datetime
from django.conf import settings
import time

logger = logging.getLogger(__name__)  # Fixed: __name__ instead of _name_

class ProviderWebhookService:
    """Service to send webhook notifications to provider systems"""
    
    def __init__(self):  # Fixed: __init__ instead of _init_
        # Get configuration from settings or use defaults
        self.config = getattr(settings, 'PROVIDER_WEBHOOK_CONFIG', {})
        
        # Provider system base URL - THIS IS THE KEY FIX
        self.base_url = self.config.get('BASE_URL', 'http://127.0.0.1:8000')  # Default to provider port
        
        # Webhook endpoints
        self.endpoints = self.config.get('ENDPOINTS', {
            'claim_approved': '/api/webhooks/payor/claim-approved/',
            'claim_denied': '/api/webhooks/payor/claim-denied/',
            'claim_under_review': '/api/webhooks/payor/claim-under-review/',
            'health': '/api/webhooks/health/',
            'test': '/api/webhooks/test/'
        })
        
        self.timeout = self.config.get('TIMEOUT', 30)
        self.retry_attempts = self.config.get('RETRY_ATTEMPTS', 3)
        self.retry_delay = self.config.get('RETRY_DELAY', 5)
        
        # Log configuration for debugging
        logger.info(f"Webhook service initialized with base_url: {self.base_url}")
    
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
            "payor_reference": claim_data.get('claim_id'),
            "event_type": "claim_approved",
            "timestamp": datetime.now().isoformat()
        }
        
        endpoint = self.endpoints.get('claim_approved', '/api/webhooks/payor/claim-approved/')
        return self._send_webhook(endpoint, payload, 'claim_approval')
    
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
            "denial_reason": claim_data.get('denial_reason', claim_data.get('reason_code', 'INSUFFICIENT_DOCUMENTATION')),
            "notes": claim_data.get('notes', 'Claim denied - missing required documentation'),
            "reviewer_id": claim_data.get('reviewer_id', 'system'),
            "payor_reference": claim_data.get('claim_id'),
            "event_type": "claim_denied",
            "timestamp": datetime.now().isoformat()
        }
        
        endpoint = self.endpoints.get('claim_denied', '/api/webhooks/payor/claim-denied/')
        return self._send_webhook(endpoint, payload, 'claim_denial')
    
    def send_claim_under_review(self, claim_data):
        """Send claim under review notification to provider"""
        payload = {
            "claim_id": claim_data.get('claim_id'),
            "provider_id": claim_data.get('provider_id', 'PROV-001'),
            "provider_name": claim_data.get('provider_name', 'Provider System'),
            "patient_name": claim_data.get('patient_name'),
            "insurance_id": claim_data.get('insurance_id'),
            "amount": float(claim_data.get('amount', 0)),
            "status": "under_review",
            "review_reason": claim_data.get('review_reason', 'MANUAL_REVIEW_REQUIRED'),
            "estimated_review_time": claim_data.get('estimated_review_time', '24-48 hours'),
            "notes": claim_data.get('notes', 'Claim requires manual review'),
            "reviewer_contact": claim_data.get('reviewer_contact', 'claims@payor.com'),
            "reviewer_id": claim_data.get('reviewer_id', 'system'),
            "payor_reference": claim_data.get('claim_id'),
            "event_type": "claim_under_review",
            "timestamp": datetime.now().isoformat()
        }
        
        endpoint = self.endpoints.get('claim_under_review', '/api/webhooks/payor/claim-under-review/')
        return self._send_webhook(endpoint, payload, 'claim_under_review')
    
    def test_provider_webhook(self):
        """Test provider webhook connectivity"""
        payload = {
            "test": True,
            "message": "Webhook connectivity test from payor system",
            "timestamp": datetime.now().isoformat()
        }
        
        endpoint = '/api/webhooks/test/'
        return self._send_webhook(endpoint, payload, 'connectivity_test')
    
    def check_provider_health(self):
        """Check provider webhook health"""
        try:
            health_endpoint = self.endpoints.get('health', '/api/webhooks/health/')
            url = f"{self.base_url}{health_endpoint}"
            
            headers = {
                'User-Agent': 'PayorSystem/1.0 WebhookBot',
                'ngrok-skip-browser-warning': 'true'
            }
            
            logger.info(f"Checking provider health at: {url}")
            response = requests.get(url, headers=headers, timeout=self.timeout)
            
            if response.status_code == 200:
                logger.info("Provider health check successful")
                return {
                    'success': True,
                    'message': 'Provider webhook service is healthy',
                    'response': response.json() if response.content else {}
                }
            else:
                logger.warning(f"Provider health check failed: {response.status_code}")
                return {
                    'success': False,
                    'message': f'Health check failed: {response.status_code}',
                    'response': response.text
                }
                
        except Exception as e:
            logger.error(f"Provider health check error: {str(e)}")
            return {
                'success': False,
                'message': f'Health check error: {str(e)}'
            }
    
    def _send_webhook(self, endpoint, payload, webhook_type):
        """Internal method to send webhook with retry logic"""
        if not self.base_url or not endpoint:
            logger.warning(f"Webhook configuration missing for {webhook_type}. Skipping notification.")
            return {
                'success': False,
                'error': 'Webhook configuration not set',
                'skipped': True
            }
        
        url = f"{self.base_url}{endpoint}"
        headers = {
            'Content-Type': 'application/json',
            'User-Agent': 'PayorSystem/1.0 WebhookBot',
            'ngrok-skip-browser-warning': 'true'  # Skip ngrok browser warning
        }
        
        # Enhanced logging for debugging
        logger.info(f"Preparing {webhook_type} webhook")
        logger.info(f"Target URL: {url}")
        logger.info(f"Payload: {json.dumps(payload, indent=2)}")
        
        for attempt in range(self.retry_attempts):
            try:
                logger.info(f"Sending {webhook_type} webhook to {url} (attempt {attempt + 1})")
                
                response = requests.post(
                    url,
                    json=payload,
                    headers=headers,
                    timeout=self.timeout
                )
                
                logger.info(f"Response status: {response.status_code}")
                logger.info(f"Response body: {response.text}")
                
                if response.status_code in [200, 201]:
                    logger.info(f"Webhook {webhook_type} sent successfully")
                    return {
                        'success': True,
                        'message': f'{webhook_type} webhook sent successfully',
                        'response': response.json() if response.content else {},
                        'attempt': attempt + 1,
                        'url': url
                    }
                else:
                    error_msg = f"HTTP {response.status_code}: {response.text}"
                    logger.warning(f"Webhook {webhook_type} failed with status {response.status_code}: {response.text}")
                    
                    if attempt == self.retry_attempts - 1:
                        logger.error(f"Webhook failed for provider {payload.get('provider_id', 'UNKNOWN')}: {response.status_code}")
                        return {
                            'success': False,
                            'error': error_msg,
                            'attempts': attempt + 1,
                            'url': url
                        }
                
            except requests.RequestException as e:
                error_msg = f"Request failed: {str(e)}"
                logger.error(f"Webhook {webhook_type} request failed (attempt {attempt + 1}): {str(e)}")
                
                if attempt == self.retry_attempts - 1:
                    logger.error(f"Webhook failed for provider {payload.get('provider_id', 'UNKNOWN')}: Connection error")
                    return {
                        'success': False,
                        'error': f'Request failed after {self.retry_attempts} attempts: {str(e)}',
                        'attempts': attempt + 1,
                        'url': url
                    }
            
            # Wait before retry
            if attempt < self.retry_attempts - 1:
                logger.info(f"Retrying in {self.retry_delay} seconds...")
                time.sleep(self.retry_delay)
        
        return {
            'success': False,
            'error': 'All retry attempts failed',
            'url': url
        }

# Global service instance
webhook_service = ProviderWebhookService()