"""
Payor Integration Service
Handles communication between Provider system and Payor backend
"""

import requests
import json
import base64
from datetime import datetime
from typing import Dict, Any, Optional, List
from django.conf import settings
from django.core.cache import cache
import logging

logger = logging.getLogger(__name__)

class PayorIntegrationService:
    """Service to handle payor system integration"""
    
    def __init__(self):
        # Get payor URL from settings (loaded from .env)
        # Remove '/api' suffix if present to get base URL
        payor_url = getattr(settings, 'PAYOR_BASE_URL', 'https://e131ed05871e.ngrok-free.app/api')
        if payor_url.endswith('/api'):
            self.payor_base_url = payor_url[:-4]  # Remove '/api' suffix
        else:
            self.payor_base_url = payor_url
            
        self.payor_email = getattr(settings, 'PAYOR_EMAIL', 'admin@payor.com')
        self.payor_password = getattr(settings, 'PAYOR_PASSWORD', 'admin123')
        self.timeout = 30
        
        # Insurance ID to Payor mappings (dynamically use current payor URL from .env)
        self.insurance_mappings = {
            'INS001': {
                'payor_name': 'BlueCross BlueShield',
                'payor_url': self.payor_base_url,
                'is_active': True
            },
            'INS002': {
                'payor_name': 'Aetna Health',
                'payor_url': self.payor_base_url,
                'is_active': True
            },
            'INS003': {
                'payor_name': 'United Healthcare',
                'payor_url': self.payor_base_url,
                'is_active': True
            },
            'HI12345': {
                'payor_name': 'Health Insurance Premium',
                'payor_url': self.payor_base_url,
                'is_active': True
            },
            'BC-789-456': {
                'payor_name': 'BlueCross BlueShield',
                'payor_url': self.payor_base_url,
                'is_active': True
            }
        }

    def get_auth_headers(self) -> Dict[str, str]:
        """Get authentication headers for payor API"""
        credentials = f"{self.payor_email}:{self.payor_password}"
        encoded_credentials = base64.b64encode(credentials.encode()).decode()
        
        return {
            'Authorization': f'Basic {encoded_credentials}',
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }

    def validate_insurance_policy(self, insurance_id: str, claim_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate claim against insurance policy rules
        
        Args:
            insurance_id: Insurance policy ID
            claim_data: Claim data to validate
            
        Returns:
            Dict with validation result
        """
        try:
            # Check if insurance ID is mapped to a payor
            if insurance_id not in self.insurance_mappings:
                return {
                    'is_valid': False,
                    'error': f'Insurance ID {insurance_id} not recognized',
                    'coverage_details': None
                }
            
            mapping = self.insurance_mappings[insurance_id]
            if not mapping['is_active']:
                return {
                    'is_valid': False,
                    'error': f'Insurance policy {insurance_id} is not active',
                    'coverage_details': None
                }
            
            # Call payor API to validate policy
            url = f"{self.payor_base_url}/api/insurance-policies/validate/"
            headers = self.get_auth_headers()
            
            payload = {
                'insurance_id': insurance_id,
                'diagnosis_code': claim_data.get('diagnosis_code'),
                'procedure_code': claim_data.get('procedure_code'),
                'amount_requested': claim_data.get('amount_requested'),
                'patient_age': claim_data.get('patient_age', 30)  # Default age if not provided
            }
            
            response = requests.post(url, json=payload, headers=headers, timeout=self.timeout)
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.warning(f"Policy validation failed: {response.status_code} - {response.text}")
                return {
                    'is_valid': True,  # Allow submission even if validation service is down
                    'error': None,
                    'coverage_details': {
                        'message': 'Policy validation service unavailable, claim will be processed normally'
                    }
                }
                
        except requests.RequestException as e:
            logger.error(f"Error validating insurance policy: {e}")
            return {
                'is_valid': True,  # Allow submission if validation service is down
                'error': None,
                'coverage_details': {
                    'message': 'Policy validation service unavailable, claim will be processed normally'
                }
            }

    def submit_claim_to_payor(self, claim_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Submit claim to payor system
        
        Args:
            claim_data: Claim data to submit
            
        Returns:
            Dict with submission result
        """
        try:
            insurance_id = claim_data.get('insurance_id')
            
            # Check if insurance ID is mapped
            if insurance_id not in self.insurance_mappings:
                return {
                    'success': False,
                    'error': f'Insurance ID {insurance_id} not recognized',
                    'payor_claim_id': None
                }
            
            # Submit to payor system
            url = f"{self.payor_base_url}/api/claims/"
            headers = self.get_auth_headers()
            
            # Prepare claim data for payor system
            payor_claim_data = {
                'patient_name': claim_data.get('patient_name'),
                'insurance_id': claim_data.get('insurance_id'),
                'diagnosis_code': claim_data.get('diagnosis_code'),
                'diagnosis_description': claim_data.get('diagnosis_description'),
                'procedure_code': claim_data.get('procedure_code'),
                'procedure_description': claim_data.get('procedure_description'),
                'amount_requested': float(claim_data.get('amount_requested', 0)),
                'date_of_service': claim_data.get('date_of_service'),
                'provider_name': claim_data.get('provider_name'),
                'provider_email': claim_data.get('provider_email'),
                'provider_npi': claim_data.get('provider_npi'),
                'notes': claim_data.get('notes', ''),
                'priority': claim_data.get('priority', 'normal'),
                'submitted_from': 'provider_system'
            }
            
            response = requests.post(url, json=payor_claim_data, headers=headers, timeout=self.timeout)
            
            if response.status_code in [200, 201]:
                result = response.json()
                return {
                    'success': True,
                    'error': None,
                    'payor_claim_id': result.get('id') or result.get('claim_id'),
                    'payor_response': result
                }
            else:
                logger.error(f"Claim submission failed: {response.status_code} - {response.text}")
                return {
                    'success': False,
                    'error': f'Payor system error: {response.status_code}',
                    'payor_claim_id': None
                }
                
        except requests.RequestException as e:
            logger.error(f"Error submitting claim to payor: {e}")
            return {
                'success': False,
                'error': f'Connection error: {str(e)}',
                'payor_claim_id': None
            }

    def get_claim_status_from_payor(self, payor_claim_id: str) -> Dict[str, Any]:
        """
        Get claim status from payor system
        
        Args:
            payor_claim_id: Claim ID in payor system
            
        Returns:
            Dict with claim status
        """
        try:
            url = f"{self.payor_base_url}/api/claims/{payor_claim_id}/"
            headers = self.get_auth_headers()
            
            response = requests.get(url, headers=headers, timeout=self.timeout)
            
            if response.status_code == 200:
                return {
                    'success': True,
                    'error': None,
                    'claim_data': response.json()
                }
            else:
                return {
                    'success': False,
                    'error': f'Payor system error: {response.status_code}',
                    'claim_data': None
                }
                
        except requests.RequestException as e:
            logger.error(f"Error getting claim status: {e}")
            return {
                'success': False,
                'error': f'Connection error: {str(e)}',
                'claim_data': None
            }

    def sync_claim_status(self, payor_claim_id: str) -> Dict[str, Any]:
        """
        Synchronize claim status between provider and payor systems
        
        Args:
            payor_claim_id: Claim ID in payor system
            
        Returns:
            Dict with synchronized status
        """
        payor_result = self.get_claim_status_from_payor(payor_claim_id)
        
        if payor_result['success']:
            payor_claim = payor_result['claim_data']
            
            return {
                'status': payor_claim.get('status', 'pending'),
                'amount_approved': payor_claim.get('amount_approved', 0),
                'rejection_reason': payor_claim.get('rejection_reason'),
                'date_processed': payor_claim.get('date_processed'),
                'last_updated': datetime.now().isoformat()
            }
        else:
            return {
                'error': payor_result['error']
            }

    def get_insurance_policies(self) -> List[Dict[str, Any]]:
        """
        Get available insurance policies from payor system
        
        Returns:
            List of insurance policies
        """
        try:
            url = f"{self.payor_base_url}/api/insurance-policies/"
            headers = self.get_auth_headers()
            
            response = requests.get(url, headers=headers, timeout=self.timeout)
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Failed to get insurance policies: {response.status_code}")
                return []
                
        except requests.RequestException as e:
            logger.error(f"Error getting insurance policies: {e}")
            return []

    def update_payor_configuration(self, payor_url: str, email: str, password: str):
        """
        Update payor system configuration
        
        Args:
            payor_url: Payor system URL (ngrok URL)
            email: Payor admin email
            password: Payor admin password
        """
        self.payor_base_url = payor_url
        self.payor_email = email
        self.payor_password = password
        
        # Cache the configuration
        cache.set('payor_config', {
            'url': payor_url,
            'email': email,
            'password': password
        }, timeout=3600)  # Cache for 1 hour

    def test_connection(self) -> Dict[str, Any]:
        """
        Test connection to payor system
        
        Returns:
            Dict with connection test result
        """
        try:
            url = f"{self.payor_base_url}/api/health/"
            headers = self.get_auth_headers()
            
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                return {
                    'success': True,
                    'message': 'Successfully connected to payor system',
                    'payor_info': response.json()
                }
            else:
                return {
                    'success': False,
                    'message': f'Connection failed: {response.status_code}',
                    'error': response.text
                }
                
        except requests.RequestException as e:
            return {
                'success': False,
                'message': f'Connection error: {str(e)}',
                'error': str(e)
            }


# Global instance
payor_service = PayorIntegrationService()