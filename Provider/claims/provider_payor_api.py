"""
Provider-side API integration for Payor Claims System
Implements full integration as per PROVIDER_INTEGRATION_GUIDE.md
"""

import requests
import hashlib
import hmac
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from django.conf import settings
from django.core.cache import cache

logger = logging.getLogger(__name__)


class ProviderPayorAPI:
    """
    Provider-side API client for submitting claims and receiving updates from Payor system
    Implements the full integration spec from PROVIDER_INTEGRATION_GUIDE.md
    """
    
    def __init__(self):
        # Payor API Configuration
        self.payor_base_url = getattr(
            settings, 
            'PAYOR_BASE_URL', 
            'https://9323de5960fc.ngrok-free.app/api'
        )
        self.api_key = getattr(settings, 'PAYOR_API_KEY', None)
        self.provider_id = getattr(settings, 'PROVIDER_ID', 'PROV-001')
        self.provider_name = getattr(settings, 'PROVIDER_NAME', 'City Medical Center')
        self.webhook_secret = getattr(settings, 'PAYOR_WEBHOOK_SECRET', 'default-secret-key')
        self.timeout = 30
        
        logger.info(f"Initialized ProviderPayorAPI with base URL: {self.payor_base_url}")

    def get_headers(self, include_auth: bool = True) -> Dict[str, str]:
        """
        Get HTTP headers for API requests
        
        Args:
            include_auth: Whether to include authentication headers
            
        Returns:
            Dict of headers
        """
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        
        if include_auth and self.api_key:
            headers['X-API-Key'] = self.api_key
            headers['X-Provider-ID'] = self.provider_id
        
        return headers

    def submit_claim(self, claim_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Submit a claim to the Payor system
        As per PROVIDER_INTEGRATION_GUIDE.md - POST /api/claims/
        
        Args:
            claim_data: Claim data containing patient, diagnosis, procedure info
            
        Returns:
            Dict with submission result including payor response
        """
        try:
            # Extract diagnosis and procedure codes from arrays or single values
            diagnosis_code = claim_data.get('diagnosis_code', '')
            diagnosis_description = claim_data.get('diagnosis_description', '')
            procedure_code = claim_data.get('procedure_code', '')
            procedure_description = claim_data.get('procedure_description', '')
            
            # Handle array format (new multi-code support)
            diagnosis_codes = claim_data.get('diagnosis_codes', [])
            if diagnosis_codes and len(diagnosis_codes) > 0:
                # Use first code as primary
                first_diag = diagnosis_codes[0]
                diagnosis_code = first_diag.get('code', '') if isinstance(first_diag, dict) else first_diag
                diagnosis_description = first_diag.get('description', '') if isinstance(first_diag, dict) else ''
            
            procedure_codes = claim_data.get('procedure_codes', [])
            if procedure_codes and len(procedure_codes) > 0:
                # Use first code as primary
                first_proc = procedure_codes[0]
                procedure_code = first_proc.get('code', '') if isinstance(first_proc, dict) else first_proc
                procedure_description = first_proc.get('description', '') if isinstance(first_proc, dict) else ''
            
            # Prepare claim data according to integration guide spec
            payor_claim_data = {
                # REQUIRED FIELDS
                "patient_name": claim_data.get('patient_name'),
                "insurance_id": claim_data.get('insurance_id'),
                "diagnosis_code": diagnosis_code,
                "amount": str(claim_data.get('amount_requested', claim_data.get('amount', 0))),
                
                # RECOMMENDED FIELDS
                "procedure_code": procedure_code,
                "diagnosis_description": diagnosis_description,
                "procedure_description": procedure_description,
                "date_of_service": claim_data.get('date_of_service', datetime.now().strftime('%Y-%m-%d')),
                "priority": claim_data.get('priority', 'medium'),
                
                # OPTIONAL FIELDS
                "patient_id": claim_data.get('patient_id', ''),
                "notes": claim_data.get('notes', ''),
                "provider_id": self.provider_id,
                "provider_name": self.provider_name,
                "referring_physician": claim_data.get('referring_physician', ''),
                "prior_authorization": claim_data.get('prior_authorization', ''),
                
                # ADDITIONAL PATIENT INFO
                "patient_dob": claim_data.get('patient_dob', ''),
                "patient_gender": claim_data.get('patient_gender', ''),
                "emergency": claim_data.get('emergency', False)
            }
            
            # Remove empty optional fields to keep payload clean
            payor_claim_data = {k: v for k, v in payor_claim_data.items() if v not in [None, '', []]}
            
            # Submit to payor
            url = f"{self.payor_base_url}/claims/"
            headers = self.get_headers(include_auth=True)
            
            logger.info(f"Submitting claim to payor: {url}")
            logger.info(f"Claim data: {json.dumps(payor_claim_data, indent=2)}")
            
            response = requests.post(
                url, 
                json=payor_claim_data, 
                headers=headers, 
                timeout=self.timeout
            )
            
            logger.info(f"Payor response status: {response.status_code}")
            logger.info(f"Payor response content-type: {response.headers.get('content-type')}")
            logger.info(f"Payor response text (first 500 chars): {response.text[:500]}")
            
            # Parse response
            if response.status_code in [200, 201]:
                try:
                    result = response.json()
                except ValueError as json_err:
                    logger.error(f"Failed to parse payor response as JSON: {json_err}")
                    logger.error(f"Response text: {response.text[:500]}")
                    return {
                        'success': False,
                        'error': 'Invalid JSON response from payor',
                        'error_code': 'INVALID_RESPONSE',
                        'claim': None,
                        'payor_claim_id': None
                    }
                
                # Log the response
                logger.info(f"Claim submitted successfully - Status: {result.get('status')}")
                
                return {
                    'success': True,
                    'status': result.get('status', 'submitted'),
                    'message': result.get('message', 'Claim submitted successfully'),
                    'claim': result.get('claim', {}),
                    'payor_claim_id': result.get('claim', {}).get('claim_id'),
                    'auto_approved': result.get('auto_approved', False),
                    'coverage_validated': result.get('claim', {}).get('coverage_validated', False),
                    'coverage_message': result.get('claim', {}).get('coverage_message', ''),
                    'payment_details': result.get('claim', {}).get('payment_details', {}),
                    'processing_time_ms': result.get('processing_time_ms', 0),
                    'raw_response': result
                }
            
            elif response.status_code in [400, 404]:
                try:
                    error_data = response.json()
                except ValueError:
                    logger.error(f"Failed to parse error response. Status: {response.status_code}, Text: {response.text[:500]}")
                    error_data = {'error': response.text or 'Unknown error'}
                logger.warning(f"Claim submission failed: {error_data.get('error')}")
                
                return {
                    'success': False,
                    'error': error_data.get('error', 'Unknown error'),
                    'error_code': error_data.get('error_code', 'UNKNOWN_ERROR'),
                    'suggestions': error_data.get('suggestions', []),
                    'claim': None,
                    'payor_claim_id': None
                }
            
            else:
                logger.error(f"Unexpected response: {response.status_code} - {response.text}")
                return {
                    'success': False,
                    'error': f'Payor system returned status {response.status_code}',
                    'error_code': 'HTTP_ERROR',
                    'claim': None,
                    'payor_claim_id': None
                }
                
        except requests.RequestException as e:
            logger.error(f"Error submitting claim to payor: {e}")
            return {
                'success': False,
                'error': f'Connection error: {str(e)}',
                'error_code': 'CONNECTION_ERROR',
                'claim': None,
                'payor_claim_id': None
            }

    def get_claim_status(self, payor_claim_id: str) -> Dict[str, Any]:
        """
        Get claim status from Payor system
        As per PROVIDER_INTEGRATION_GUIDE.md - GET /api/claims/{claim_id}/
        
        Args:
            payor_claim_id: The claim ID from payor system
            
        Returns:
            Dict with claim status and details
        """
        try:
            url = f"{self.payor_base_url}/claims/{payor_claim_id}/"
            headers = self.get_headers(include_auth=True)
            
            logger.info(f"Fetching claim status from payor: {url}")
            
            response = requests.get(url, headers=headers, timeout=self.timeout)
            
            if response.status_code == 200:
                result = response.json()
                
                return {
                    'success': True,
                    'claim': result,
                    'status': result.get('status'),
                    'claim_id': result.get('claim_id'),
                    'patient_name': result.get('patient_name'),
                    'amount': result.get('amount'),
                    'approved_amount': result.get('expected_payment'),
                    'patient_responsibility': result.get('patient_responsibility'),
                    'processed_date': result.get('processed_date'),
                    'submitted_date': result.get('submitted_date')
                }
            
            elif response.status_code == 404:
                return {
                    'success': False,
                    'error': f'Claim {payor_claim_id} not found in payor system',
                    'claim': None
                }
            
            else:
                logger.error(f"Failed to get claim status: {response.status_code}")
                return {
                    'success': False,
                    'error': f'Payor system error: {response.status_code}',
                    'claim': None
                }
                
        except requests.RequestException as e:
            logger.error(f"Error getting claim status: {e}")
            return {
                'success': False,
                'error': f'Connection error: {str(e)}',
                'claim': None
            }

    def verify_webhook_signature(self, payload: str, signature: str) -> bool:
        """
        Verify webhook signature from Payor system
        As per PROVIDER_INTEGRATION_GUIDE.md - Webhook Security
        
        Args:
            payload: Raw webhook payload as string
            signature: Signature from webhook headers (format: "sha256=...")
            
        Returns:
            bool indicating if signature is valid
        """
        try:
            # Extract the hash from signature
            if signature.startswith('sha256='):
                received_hash = signature[7:]
            else:
                received_hash = signature
            
            # Calculate expected signature
            expected_signature = hmac.new(
                self.webhook_secret.encode(),
                payload.encode(),
                hashlib.sha256
            ).hexdigest()
            
            # Secure comparison
            return hmac.compare_digest(expected_signature, received_hash)
            
        except Exception as e:
            logger.error(f"Error verifying webhook signature: {e}")
            return False

    def process_webhook_notification(self, webhook_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process webhook notification from Payor system
        As per PROVIDER_INTEGRATION_GUIDE.md - Webhook Payload Structure
        
        Args:
            webhook_data: Webhook payload from payor
            
        Returns:
            Dict with processed webhook information
        """
        try:
            event_type = webhook_data.get('event_type')
            claim_id = webhook_data.get('claim_id')
            new_status = webhook_data.get('new_status')
            previous_status = webhook_data.get('previous_status')
            
            logger.info(f"Processing webhook - Event: {event_type}, Claim: {claim_id}, Status: {previous_status} -> {new_status}")
            
            processed_data = {
                'event_type': event_type,
                'timestamp': webhook_data.get('timestamp'),
                'claim_id': claim_id,
                'previous_status': previous_status,
                'new_status': new_status,
                'message': webhook_data.get('message'),
                'patient_name': webhook_data.get('patient_name'),
                'insurance_id': webhook_data.get('insurance_id'),
                'amount': webhook_data.get('amount'),
                'coverage_validated': webhook_data.get('coverage_validated'),
                'auto_approved': webhook_data.get('auto_approved'),
                'payment_details': webhook_data.get('payment_details', {}),
                'processed_by': webhook_data.get('processed_by'),
                'processed_date': webhook_data.get('processed_date')
            }
            
            return {
                'success': True,
                'processed_data': processed_data,
                'requires_action': new_status in ['approved', 'rejected'],
                'action_type': new_status
            }
            
        except Exception as e:
            logger.error(f"Error processing webhook: {e}")
            return {
                'success': False,
                'error': str(e),
                'processed_data': None
            }

    def validate_claim_data(self, claim_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate claim data before submission
        As per PROVIDER_INTEGRATION_GUIDE.md - Required Fields
        
        Args:
            claim_data: Claim data to validate
            
        Returns:
            Dict with validation result
        """
        errors = []
        warnings = []
        
        # Required fields - support both single and array formats
        if not claim_data.get('patient_name'):
            errors.append("Missing required field: patient_name")
        
        if not claim_data.get('insurance_id'):
            errors.append("Missing required field: insurance_id")
        
        # Check for diagnosis code in either format
        has_diagnosis = claim_data.get('diagnosis_code') or \
                       (claim_data.get('diagnosis_codes') and len(claim_data.get('diagnosis_codes', [])) > 0)
        if not has_diagnosis:
            errors.append("Missing required field: diagnosis_code or diagnosis_codes")
        
        # Check amount (support both amount and amount_requested)
        if not claim_data.get('amount') and not claim_data.get('amount_requested'):
            errors.append("Missing required field: amount")
        
        # Recommended fields - check both single and array formats
        if not claim_data.get('procedure_code') and not claim_data.get('procedure_codes'):
            warnings.append("Missing recommended field: procedure_code or procedure_codes")
        if not claim_data.get('date_of_service'):
            warnings.append("Missing recommended field: date_of_service")
        
        # Validate amount - support both 'amount' and 'amount_requested'
        try:
            amount = float(claim_data.get('amount') or claim_data.get('amount_requested', 0))
            if amount <= 0:
                errors.append("Amount must be greater than 0")
        except (ValueError, TypeError):
            errors.append("Amount must be a valid number")
        
        # Validate diagnosis code format (basic ICD-10 validation)
        # Check single code
        diagnosis_code = claim_data.get('diagnosis_code', '')
        if diagnosis_code and not self._validate_icd10_format(diagnosis_code):
            warnings.append(f"Diagnosis code '{diagnosis_code}' may not be a valid ICD-10 format")
        
        # Check array of codes
        diagnosis_codes = claim_data.get('diagnosis_codes', [])
        if diagnosis_codes:
            for code_item in diagnosis_codes:
                code = code_item.get('code', '') if isinstance(code_item, dict) else code_item
                if code and not self._validate_icd10_format(code):
                    warnings.append(f"Diagnosis code '{code}' may not be a valid ICD-10 format")
        
        # Validate procedure code format (basic CPT validation)
        # Check single code
        procedure_code = claim_data.get('procedure_code', '')
        if procedure_code and not self._validate_cpt_format(procedure_code):
            warnings.append(f"Procedure code '{procedure_code}' may not be a valid CPT format")
        
        # Check array of codes
        procedure_codes = claim_data.get('procedure_codes', [])
        if procedure_codes:
            for code_item in procedure_codes:
                code = code_item.get('code', '') if isinstance(code_item, dict) else code_item
                if code and not self._validate_cpt_format(code):
                    warnings.append(f"Procedure code '{code}' may not be a valid CPT format")
        
        return {
            'is_valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings
        }

    def _validate_icd10_format(self, code: str) -> bool:
        """Basic ICD-10 format validation"""
        import re
        # ICD-10 format: Letter followed by 2 digits, optional decimal and 1-2 more digits
        return bool(re.match(r'^[A-Z]\d{2}(\.\d{1,2})?$', code))

    def _validate_cpt_format(self, code: str) -> bool:
        """Basic CPT format validation"""
        # CPT codes are 5 digits
        return code.isdigit() and len(code) == 5

    def submit_claim_with_retry(self, claim_data: Dict[str, Any], max_retries: int = 3) -> Dict[str, Any]:
        """
        Submit claim with automatic retry logic
        As per PROVIDER_INTEGRATION_GUIDE.md - Error Handling Best Practices
        
        Args:
            claim_data: Claim data to submit
            max_retries: Maximum number of retry attempts
            
        Returns:
            Dict with submission result
        """
        last_error = None
        
        for attempt in range(1, max_retries + 1):
            try:
                logger.info(f"Claim submission attempt {attempt}/{max_retries}")
                
                result = self.submit_claim(claim_data)
                
                if result['success']:
                    logger.info(f"Claim submitted successfully on attempt {attempt}")
                    return result
                
                # Don't retry on client errors (4xx)
                if result.get('error_code') in ['INSURANCE_NOT_FOUND', 'INVALID_DATA', 'CLIENT_ERROR']:
                    logger.info(f"Client error detected, not retrying: {result.get('error')}")
                    return result
                
                last_error = result
                
            except Exception as e:
                logger.error(f"Attempt {attempt} failed with exception: {e}")
                last_error = {
                    'success': False,
                    'error': str(e),
                    'error_code': 'EXCEPTION_ERROR'
                }
            
            # Wait before retry with exponential backoff
            if attempt < max_retries:
                wait_time = 2 ** attempt  # 2s, 4s, 8s
                logger.info(f"Waiting {wait_time}s before retry...")
                import time
                time.sleep(wait_time)
        
        # All retries failed
        logger.error(f"Claim submission failed after {max_retries} attempts")
        return {
            'success': False,
            'error': f"Failed after {max_retries} attempts: {last_error.get('error') if last_error else 'Unknown error'}",
            'error_code': 'MAX_RETRIES_EXCEEDED',
            'last_error': last_error
        }

    def test_connection(self) -> Dict[str, Any]:
        """
        Test connection to Payor system
        
        Returns:
            Dict with connection test result
        """
        try:
            # Try to access the base API
            base_url = self.payor_base_url.rstrip('/')
            if base_url.endswith('/api'):
                base_url = base_url[:-4]
            url = f"{base_url}/api/health/"
            headers = self.get_headers(include_auth=False)
            
            logger.info(f"Testing connection to payor at: {url}")
            
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                return {
                    'success': True,
                    'message': 'Successfully connected to payor system',
                    'payor_url': self.payor_base_url,
                    'provider_id': self.provider_id
                }
            else:
                return {
                    'success': False,
                    'message': f'Connection returned status {response.status_code}',
                    'payor_url': self.payor_base_url
                }
                
        except requests.RequestException as e:
            logger.error(f"Connection test failed: {e}")
            return {
                'success': False,
                'message': f'Connection error: {str(e)}',
                'payor_url': self.payor_base_url
            }

    def update_configuration(self, payor_url: str = None, api_key: str = None, 
                           provider_id: str = None, webhook_secret: str = None):
        """
        Update payor integration configuration
        
        Args:
            payor_url: New payor base URL
            api_key: New API key
            provider_id: New provider ID
            webhook_secret: New webhook secret
        """
        if payor_url:
            # Normalize URL - ensure it ends with /api
            base_url = payor_url.rstrip('/')
            if not base_url.endswith('/api'):
                base_url = base_url + '/api'
            self.payor_base_url = base_url
            logger.info(f"Updated payor URL to: {self.payor_base_url}")
        
        if api_key:
            self.api_key = api_key
            logger.info("Updated API key")
        
        if provider_id:
            self.provider_id = provider_id
            logger.info(f"Updated provider ID to: {provider_id}")
        
        if webhook_secret:
            self.webhook_secret = webhook_secret
            logger.info("Updated webhook secret")
        
        # Cache configuration
        cache.set('provider_payor_config', {
            'payor_url': self.payor_base_url,
            'provider_id': self.provider_id,
            'updated_at': datetime.now().isoformat()
        }, timeout=3600)


# Global instance
provider_payor_api = ProviderPayorAPI()
