"""
Django views for Provider-Payor integration
Handles claim submission, status updates, and webhook notifications
"""

from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.authentication import BasicAuthentication
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.response import Response
from rest_framework import status
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.utils.decorators import method_decorator
import json
import logging
from datetime import datetime

from .provider_payor_api import provider_payor_api

logger = logging.getLogger(__name__)


@api_view(['POST'])
@authentication_classes([JWTAuthentication, BasicAuthentication])  # Support both JWT and Basic Auth
@permission_classes([AllowAny])
def submit_claim_to_payor(request):
    """
    Submit a claim to the Payor system
    POST /api/provider/submit-claim/
    
    Request body should contain claim data as per integration guide
    """
    try:
        claim_data = request.data
        
        # Debug: Log received claim data
        logger.info(f"Received claim data: {json.dumps(dict(claim_data), indent=2)}")
        
        # Validate claim data
        validation = provider_payor_api.validate_claim_data(claim_data)
        if not validation['is_valid']:
            return Response({
                'success': False,
                'error': 'Claim validation failed',
                'validation_errors': validation['errors'],
                'validation_warnings': validation['warnings']
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Submit claim to payor with retry logic
        result = provider_payor_api.submit_claim_with_retry(claim_data, max_retries=3)
        
        if result['success']:
            # Save claim in MongoDB
            try:
                from .mongo_models import Claim as MongoClaim
                
                # Handle both array and legacy formats
                diagnosis_codes = claim_data.get('diagnosis_codes', [])
                procedure_codes = claim_data.get('procedure_codes', [])
                
                # If legacy single codes provided, convert to array format
                if not diagnosis_codes and claim_data.get('diagnosis_code'):
                    diagnosis_codes = [{
                        'code': claim_data.get('diagnosis_code'),
                        'description': claim_data.get('diagnosis_description', '')
                    }]
                if not procedure_codes and claim_data.get('procedure_code'):
                    procedure_codes = [{
                        'code': claim_data.get('procedure_code'),
                        'description': claim_data.get('procedure_description', '')
                    }]
                
                # For display purposes, use first diagnosis description
                primary_diagnosis = diagnosis_codes[0]['description'] if diagnosis_codes else ''
                
                mongo_claim = MongoClaim(
                    claim_number=result.get('payor_claim_id', f"CLM-{datetime.now().strftime('%Y%m%d-%H%M%S')}"),
                    patient_name=claim_data.get('patient_name'),
                    diagnosis_codes=diagnosis_codes,
                    procedure_codes=procedure_codes,
                    diagnosis_code=diagnosis_codes[0]['code'] if diagnosis_codes else '',
                    diagnosis_description=primary_diagnosis,
                    procedure_code=procedure_codes[0]['code'] if procedure_codes else '',
                    procedure_description=procedure_codes[0]['description'] if procedure_codes else '',
                    amount_requested=float(claim_data.get('amount_requested', claim_data.get('amount', 0))),
                    amount_approved=result.get('payment_details', {}).get('approved_amount', 0),
                    status=result.get('status', 'submitted'),
                    payor_claim_id=result.get('payor_claim_id'),
                    payor_response=result.get('raw_response', {}),
                    insurance_id=claim_data.get('insurance_id'),
                    date_of_service=datetime.strptime(claim_data.get('date_of_service', datetime.now().strftime('%Y-%m-%d')), '%Y-%m-%d'),
                    date_submitted=datetime.now(),
                    notes=claim_data.get('notes', ''),
                    priority=claim_data.get('priority', 'medium')
                )
                mongo_claim.save()
                
                logger.info(f"Claim saved to MongoDB: {mongo_claim.claim_number}")
                
            except Exception as e:
                logger.error(f"Error saving claim to MongoDB: {e}")
                # Continue anyway as claim was submitted to payor
            
            return Response({
                'success': True,
                'message': 'Claim submitted successfully to Payor system',
                'claim_id': result.get('payor_claim_id'),
                'status': result.get('status'),
                'auto_approved': result.get('auto_approved'),
                'coverage_validated': result.get('coverage_validated'),
                'coverage_message': result.get('coverage_message'),
                'payment_details': result.get('payment_details'),
                'validation_warnings': validation.get('warnings', []),
                'payor_response': result
            }, status=status.HTTP_201_CREATED)
        
        else:
            return Response({
                'success': False,
                'error': result.get('error'),
                'error_code': result.get('error_code'),
                'suggestions': result.get('suggestions', []),
                'validation_warnings': validation.get('warnings', [])
            }, status=status.HTTP_400_BAD_REQUEST)
            
    except Exception as e:
        logger.error(f"Error in submit_claim_to_payor: {e}", exc_info=True)
        return Response({
            'success': False,
            'error': f'Internal server error: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_payor_claim_status(request, claim_id):
    """
    Get claim status from Payor system
    GET /api/provider/claim-status/<claim_id>/
    """
    try:
        result = provider_payor_api.get_claim_status(claim_id)
        
        if result['success']:
            # Update MongoDB if claim exists
            try:
                from .mongo_models import Claim as MongoClaim
                mongo_claim = MongoClaim.objects(payor_claim_id=claim_id).first()
                if mongo_claim:
                    mongo_claim.status = result.get('status', mongo_claim.status)
                    mongo_claim.amount_approved = result.get('approved_amount', mongo_claim.amount_approved)
                    mongo_claim.payor_response = result.get('claim', {})
                    mongo_claim.save()
                    logger.info(f"Updated claim status in MongoDB: {claim_id}")
            except Exception as e:
                logger.error(f"Error updating claim in MongoDB: {e}")
            
            return Response({
                'success': True,
                'claim': result.get('claim'),
                'status': result.get('status'),
                'claim_id': result.get('claim_id')
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'success': False,
                'error': result.get('error')
            }, status=status.HTTP_404_NOT_FOUND)
            
    except Exception as e:
        logger.error(f"Error in get_payor_claim_status: {e}", exc_info=True)
        return Response({
            'success': False,
            'error': f'Internal server error: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([AllowAny])
@csrf_exempt
def payor_webhook_receiver(request):
    """
    Receive webhook notifications from Payor system
    POST /api/provider/webhook/payor-claims/
    
    As per PROVIDER_INTEGRATION_GUIDE.md - Webhook Integration
    """
    try:
        # Get webhook signature from headers
        webhook_signature = request.headers.get('X-Webhook-Signature', '')
        
        # Get raw body for signature verification
        raw_body = request.body.decode('utf-8')
        
        # Verify webhook signature
        if webhook_signature:
            is_valid = provider_payor_api.verify_webhook_signature(raw_body, webhook_signature)
            if not is_valid:
                logger.warning("Invalid webhook signature received")
                return Response({
                    'error': 'Invalid webhook signature'
                }, status=status.HTTP_401_UNAUTHORIZED)
        
        # Parse webhook data
        webhook_data = json.loads(raw_body)
        
        logger.info(f"Received webhook: {webhook_data.get('event_type')} for claim {webhook_data.get('claim_id')}")
        
        # Process webhook
        result = provider_payor_api.process_webhook_notification(webhook_data)
        
        if result['success']:
            processed_data = result['processed_data']
            claim_id = processed_data.get('claim_id')
            new_status = processed_data.get('new_status')
            
            # Update claim in MongoDB
            try:
                from .mongo_models import Claim as MongoClaim
                mongo_claim = MongoClaim.objects(payor_claim_id=claim_id).first()
                if mongo_claim:
                    mongo_claim.status = new_status
                    mongo_claim.payor_response = webhook_data
                    
                    # Update payment details if approved
                    if new_status == 'approved':
                        payment_details = processed_data.get('payment_details', {})
                        mongo_claim.amount_approved = payment_details.get('approved_amount', mongo_claim.amount_approved)
                    
                    # Add rejection reason if rejected
                    elif new_status == 'rejected':
                        mongo_claim.notes = f"{mongo_claim.notes}\nRejection: {processed_data.get('message', '')}"
                    
                    mongo_claim.save()
                    logger.info(f"Updated claim in MongoDB: {claim_id} -> {new_status}")
                else:
                    logger.warning(f"Claim not found in MongoDB: {claim_id}")
                    
            except Exception as e:
                logger.error(f"Error updating claim from webhook: {e}")
            
            # TODO: Send notifications to relevant staff
            # - Email notifications
            # - Dashboard alerts
            # - SMS for urgent updates
            
            return Response({
                'received': True,
                'message': 'Webhook processed successfully',
                'claim_id': claim_id,
                'status': new_status
            }, status=status.HTTP_200_OK)
        else:
            logger.error(f"Error processing webhook: {result.get('error')}")
            return Response({
                'received': True,
                'error': result.get('error'),
                'message': 'Webhook received but processing failed'
            }, status=status.HTTP_200_OK)  # Still return 200 to acknowledge receipt
            
    except Exception as e:
        logger.error(f"Error in payor_webhook_receiver: {e}", exc_info=True)
        return Response({
            'received': True,
            'error': str(e)
        }, status=status.HTTP_200_OK)  # Still return 200 to acknowledge receipt


@api_view(['POST'])
@permission_classes([AllowAny])
def test_payor_connection(request):
    """
    Test connection to Payor system
    POST /api/provider/test-connection/
    """
    try:
        result = provider_payor_api.test_connection()
        
        if result['success']:
            return Response({
                'success': True,
                'message': result['message'],
                'payor_url': result['payor_url'],
                'provider_id': result['provider_id']
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'success': False,
                'message': result['message'],
                'payor_url': result['payor_url']
            }, status=status.HTTP_503_SERVICE_UNAVAILABLE)
            
    except Exception as e:
        logger.error(f"Error in test_payor_connection: {e}", exc_info=True)
        return Response({
            'success': False,
            'error': f'Internal server error: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_payor_configuration(request):
    """
    Update Payor integration configuration
    POST /api/provider/update-config/
    
    Request body:
    {
        "payor_url": "https://new-ngrok-url.ngrok.app/api",
        "api_key": "optional-api-key",
        "provider_id": "PROV-001",
        "webhook_secret": "optional-webhook-secret"
    }
    """
    try:
        config_data = request.data
        
        provider_payor_api.update_configuration(
            payor_url=config_data.get('payor_url'),
            api_key=config_data.get('api_key'),
            provider_id=config_data.get('provider_id'),
            webhook_secret=config_data.get('webhook_secret')
        )
        
        # Test new configuration
        test_result = provider_payor_api.test_connection()
        
        return Response({
            'success': True,
            'message': 'Configuration updated successfully',
            'connection_test': test_result
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Error in update_payor_configuration: {e}", exc_info=True)
        return Response({
            'success': False,
            'error': f'Internal server error: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([AllowAny])
def sync_all_claims_status(request):
    """
    Sync status of all pending claims with Payor system
    GET /api/provider/sync-claims/
    """
    try:
        from .mongo_models import Claim as MongoClaim
        # Get all claims that are not in final status
        pending_statuses = ['submitted', 'pending', 'under_review', 'processing']
        pending_claims = MongoClaim.objects(status__in=pending_statuses, payor_claim_id__ne=None)
        
        synced_count = 0
        updated_count = 0
        errors = []
        
        for claim in pending_claims:
            try:
                result = provider_payor_api.get_claim_status(claim.payor_claim_id)
                synced_count += 1
                
                if result['success']:
                    new_status = result.get('status')
                    if new_status != claim.status:
                        claim.status = new_status
                        claim.amount_approved = result.get('approved_amount', claim.amount_approved)
                        claim.payor_response = result.get('claim', {})
                        claim.save()
                        updated_count += 1
                        logger.info(f"Updated claim {claim.claim_number}: {claim.status} -> {new_status}")
                        
            except Exception as e:
                logger.error(f"Error syncing claim {claim.claim_number}: {e}")
                errors.append({
                    'claim_number': claim.claim_number,
                    'error': str(e)
                })
        
        return Response({
            'success': True,
            'message': f'Synced {synced_count} claims, updated {updated_count}',
            'synced': synced_count,
            'updated': updated_count,
            'errors': errors
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Error in sync_all_claims_status: {e}", exc_info=True)
        return Response({
            'success': False,
            'error': f'Internal server error: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
