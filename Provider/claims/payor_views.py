"""
Payor Integration Views
Views for managing payor system integration
"""

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json
from datetime import datetime
from bson import ObjectId

from .mongo_models import Claim
from .payor_integration import payor_service
from .mongo_views import serialize_claim


@method_decorator(csrf_exempt, name='dispatch')
class PayorIntegrationView(APIView):
    """Payor integration management view"""
    authentication_classes = []
    permission_classes = [AllowAny]
    
    def get(self, request):
        """Get payor integration status and configuration"""
        try:
            # Test connection to payor system
            connection_test = payor_service.test_connection()
            
            # Get insurance policies
            policies = payor_service.get_insurance_policies()
            
            return Response({
                'connection_status': connection_test,
                'insurance_mappings': payor_service.insurance_mappings,
                'insurance_policies': policies,
                'payor_config': {
                    'base_url': payor_service.payor_base_url,
                    'email': payor_service.payor_email
                }
            })
            
        except Exception as e:
            return Response(
                {'error': f'Failed to get payor integration status: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def post(self, request):
        """Update payor configuration"""
        try:
            data = json.loads(request.body)
            
            payor_url = data.get('payor_url')
            email = data.get('email')
            password = data.get('password')
            
            if not all([payor_url, email, password]):
                return Response(
                    {'error': 'payor_url, email, and password are required'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Update configuration
            payor_service.update_payor_configuration(payor_url, email, password)
            
            # Test the new configuration
            connection_test = payor_service.test_connection()
            
            return Response({
                'message': 'Payor configuration updated successfully',
                'connection_test': connection_test
            })
            
        except Exception as e:
            return Response(
                {'error': f'Failed to update payor configuration: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


@method_decorator(csrf_exempt, name='dispatch')
class ClaimSyncView(APIView):
    """Synchronize claim status with payor system"""
    authentication_classes = []
    permission_classes = [AllowAny]
    
    def post(self, request, claim_id=None):
        """Sync claim status with payor system"""
        try:
            if claim_id:
                # Sync specific claim
                claim = Claim.objects(id=ObjectId(claim_id)).first()
                if not claim:
                    return Response(
                        {'error': 'Claim not found'},
                        status=status.HTTP_404_NOT_FOUND
                    )
                
                if not claim.payor_claim_id:
                    return Response(
                        {'error': 'Claim was not submitted to payor system'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
                # Sync with payor
                sync_result = payor_service.sync_claim_status(claim.payor_claim_id)
                
                if 'error' not in sync_result:
                    # Update local claim
                    claim.status = sync_result.get('status', claim.status)
                    claim.amount_approved = sync_result.get('amount_approved', claim.amount_approved)
                    claim.rejection_reason = sync_result.get('rejection_reason', claim.rejection_reason)
                    if sync_result.get('date_processed'):
                        claim.date_processed = datetime.fromisoformat(sync_result['date_processed'].replace('Z', '+00:00'))
                    claim.date_updated = datetime.now()
                    claim.save()
                    
                    return Response({
                        'message': 'Claim synchronized successfully',
                        'claim': serialize_claim(claim),
                        'sync_result': sync_result
                    })
                else:
                    return Response(
                        {'error': f'Failed to sync with payor: {sync_result["error"]}'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            else:
                # Sync all claims with payor IDs
                claims_to_sync = Claim.objects(payor_claim_id__ne=None, submitted_to_payor=True)
                synced_count = 0
                errors = []
                
                for claim in claims_to_sync:
                    try:
                        sync_result = payor_service.sync_claim_status(claim.payor_claim_id)
                        
                        if 'error' not in sync_result:
                            claim.status = sync_result.get('status', claim.status)
                            claim.amount_approved = sync_result.get('amount_approved', claim.amount_approved)
                            claim.rejection_reason = sync_result.get('rejection_reason', claim.rejection_reason)
                            if sync_result.get('date_processed'):
                                claim.date_processed = datetime.fromisoformat(sync_result['date_processed'].replace('Z', '+00:00'))
                            claim.date_updated = datetime.now()
                            claim.save()
                            synced_count += 1
                        else:
                            errors.append(f"Claim {claim.claim_number}: {sync_result['error']}")
                    except Exception as e:
                        errors.append(f"Claim {claim.claim_number}: {str(e)}")
                
                return Response({
                    'message': f'Synchronized {synced_count} claims',
                    'synced_count': synced_count,
                    'total_claims': len(claims_to_sync),
                    'errors': errors
                })
                
        except Exception as e:
            return Response(
                {'error': f'Failed to sync claims: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


@method_decorator(csrf_exempt, name='dispatch')
class PolicyValidationView(APIView):
    """Validate insurance policy before claim submission"""
    authentication_classes = []
    permission_classes = [AllowAny]
    
    def post(self, request):
        """Validate claim against insurance policy"""
        try:
            data = json.loads(request.body)
            
            insurance_id = data.get('insurance_id')
            if not insurance_id:
                return Response(
                    {'error': 'insurance_id is required'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Validate policy
            validation_result = payor_service.validate_insurance_policy(insurance_id, data)
            
            return Response(validation_result)
            
        except Exception as e:
            return Response(
                {'error': f'Failed to validate policy: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )