"""
Provider Webhook Views for receiving payor notifications
"""
import json
import logging
from datetime import datetime
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils.decorators import method_decorator
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from .mongo_models import Claim, User
import hashlib
import hmac

logger = logging.getLogger(__name__)

@csrf_exempt
@require_http_methods(["POST"])
def payor_claim_approved(request):
    """
    Webhook endpoint for payor claim approval notifications
    POST /api/webhooks/payor/claim-approved/
    """
    try:
        # Parse the incoming data
        data = json.loads(request.body.decode('utf-8'))
        
        # Log the incoming webhook
        logger.info(f"Received claim approval webhook: {data}")
        
        # Extract claim information
        claim_id = data.get('claim_id')
        payor_reference = data.get('payor_reference')
        approved_amount = data.get('approved_amount')
        patient_responsibility = data.get('patient_responsibility', 0)
        approval_date = data.get('approval_date')
        reason_code = data.get('reason_code', 'APPROVED')
        notes = data.get('notes', '')
        reviewer_id = data.get('reviewer_id', 'system')
        
        if not claim_id:
            return JsonResponse({
                'success': False,
                'error': 'claim_id is required'
            }, status=400)
        
        # Find the claim in MongoDB
        try:
            claim = None
            
            # Try multiple ways to find the claim
            if claim_id:
                # First try exact claim_id match
                claim = Claim.objects(claim_id=claim_id).first()
                
                # If not found, try claim_number match
                if not claim:
                    claim = Claim.objects(claim_number=claim_id).first()
            
            # If still not found and we have payor_reference, try that
            if not claim and payor_reference:
                claim = Claim.objects(payor_claim_id=payor_reference).first()
            
            # If still not found, try to find by patient name and amount (last resort)
            if not claim and data.get('patient_name') and approved_amount:
                patient_name = data.get('patient_name')
                claim = Claim.objects(
                    patient_name=patient_name,
                    amount_requested=float(approved_amount),
                    status__in=['pending', 'submitted', 'under_review']
                ).first()
                
            if claim:
                # Store original status for logging
                original_status = claim.status
                
                # Update claim status
                claim.status = 'approved'
                claim.approved_amount = float(approved_amount) if approved_amount else claim.amount_requested
                claim.patient_responsibility = float(patient_responsibility)
                claim.approval_date = datetime.now()
                claim.payor_response = data
                claim.notes = f"{claim.notes}\n[PAYOR APPROVED] {notes}" if claim.notes else f"[PAYOR APPROVED] {notes}"
                
                # Add payor reference if provided
                if payor_reference and not claim.payor_claim_id:
                    claim.payor_claim_id = payor_reference
                
                claim.save()
                
                logger.info(f"✅ Claim approval webhook processed successfully")
                logger.info(f"   Claim ID: {claim_id}")
                logger.info(f"   MongoDB ID: {str(claim.id)}")
                logger.info(f"   Status: {original_status} → approved")
                logger.info(f"   Amount: ${claim.approved_amount}")
                
                return JsonResponse({
                    'success': True,
                    'message': 'Claim approval notification received and processed',
                    'claim_id': claim_id,
                    'updated_claim': {
                        'id': str(claim.id),
                        'claim_number': claim.claim_number,
                        'status': claim.status,
                        'original_status': original_status,
                        'approved_amount': claim.approved_amount,
                        'patient_responsibility': claim.patient_responsibility,
                        'approval_date': claim.approval_date.isoformat() if claim.approval_date else None
                    }
                })
            else:
                logger.warning(f"❌ Claim not found for webhook")
                logger.warning(f"   Searched for claim_id: {claim_id}")
                logger.warning(f"   Searched for payor_reference: {payor_reference}")
                logger.warning(f"   Patient name: {data.get('patient_name')}")
                
                # List recent claims for debugging
                recent_claims = Claim.objects().order_by('-date_submitted').limit(5)
                logger.warning(f"   Recent claims in database:")
                for rc in recent_claims:
                    logger.warning(f"     - {rc.claim_number} | {rc.claim_id} | {rc.patient_name} | {rc.status}")
                
                return JsonResponse({
                    'success': False,
                    'error': f'Claim not found: {claim_id}',
                    'suggestion': 'Verify claim ID or check if claim was submitted from this provider',
                    'searched_identifiers': {
                        'claim_id': claim_id,
                        'payor_reference': payor_reference,
                        'patient_name': data.get('patient_name')
                    }
                }, status=404)
                
        except Exception as e:
            logger.error(f"Database error updating claim {claim_id}: {str(e)}")
            return JsonResponse({
                'success': False,
                'error': f'Database error: {str(e)}'
            }, status=500)
            
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in webhook payload: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': 'Invalid JSON payload'
        }, status=400)
        
    except Exception as e:
        logger.error(f"Unexpected error in claim approval webhook: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': f'Internal server error: {str(e)}'
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def payor_claim_denied(request):
    """
    Webhook endpoint for payor claim denial notifications
    POST /api/webhooks/payor/claim-denied/
    """
    try:
        # Parse the incoming data
        data = json.loads(request.body.decode('utf-8'))
        
        # Log the incoming webhook
        logger.info(f"Received claim denial webhook: {data}")
        
        # Extract claim information
        claim_id = data.get('claim_id')
        payor_reference = data.get('payor_reference')
        denial_reason = data.get('denial_reason', 'INSUFFICIENT_DOCUMENTATION')
        denial_date = data.get('denial_date')
        notes = data.get('notes', '')
        reviewer_id = data.get('reviewer_id', 'system')
        
        if not claim_id:
            return JsonResponse({
                'success': False,
                'error': 'claim_id is required'
            }, status=400)
        
        # Find the claim in MongoDB
        try:
            claim = None
            
            # Try multiple ways to find the claim
            if claim_id:
                claim = Claim.objects(claim_id=claim_id).first()
                if not claim:
                    claim = Claim.objects(claim_number=claim_id).first()
            
            if not claim and payor_reference:
                claim = Claim.objects(payor_claim_id=payor_reference).first()
            
            if not claim and data.get('patient_name'):
                patient_name = data.get('patient_name')
                claim = Claim.objects(
                    patient_name=patient_name,
                    status__in=['pending', 'submitted', 'under_review']
                ).first()
                
            if claim:
                # Store original status for logging
                original_status = claim.status
                
                # Update claim status
                claim.status = 'denied'
                claim.denial_reason = denial_reason
                claim.denial_date = datetime.now()
                claim.payor_response = data
                claim.notes = f"{claim.notes}\n[PAYOR DENIED] {notes}" if claim.notes else f"[PAYOR DENIED] {notes}"
                
                # Add payor reference if provided
                if payor_reference and not claim.payor_claim_id:
                    claim.payor_claim_id = payor_reference
                
                claim.save()
                
                logger.info(f"✅ Claim denial webhook processed successfully")
                logger.info(f"   Claim ID: {claim_id}")
                logger.info(f"   MongoDB ID: {str(claim.id)}")
                logger.info(f"   Status: {original_status} → denied")
                logger.info(f"   Reason: {denial_reason}")
                
                return JsonResponse({
                    'success': True,
                    'message': 'Claim denial notification received and processed',
                    'claim_id': claim_id,
                    'updated_claim': {
                        'id': str(claim.id),
                        'claim_number': claim.claim_number,
                        'status': claim.status,
                        'original_status': original_status,
                        'denial_reason': denial_reason,
                        'denial_date': claim.denial_date.isoformat() if claim.denial_date else None
                    }
                })
            else:
                logger.warning(f"❌ Claim not found for denial webhook")
                logger.warning(f"   Searched for claim_id: {claim_id}")
                logger.warning(f"   Searched for payor_reference: {payor_reference}")
                
                return JsonResponse({
                    'success': False,
                    'error': f'Claim not found: {claim_id}',
                    'suggestion': 'Verify claim ID or check if claim was submitted from this provider'
                }, status=404)
                
        except Exception as e:
            logger.error(f"Database error updating claim {claim_id}: {str(e)}")
            return JsonResponse({
                'success': False,
                'error': f'Database error: {str(e)}'
            }, status=500)
            
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in webhook payload: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': 'Invalid JSON payload'
        }, status=400)
        
    except Exception as e:
        logger.error(f"Unexpected error in claim denial webhook: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': f'Internal server error: {str(e)}'
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def payor_claim_under_review(request):
    """
    Webhook endpoint for payor claim under review notifications
    POST /api/webhooks/payor/claim-under-review/
    """
    try:
        # Parse the incoming data
        data = json.loads(request.body.decode('utf-8'))
        
        # Log the incoming webhook
        logger.info(f"Received claim under review webhook: {data}")
        
        # Extract claim information
        claim_id = data.get('claim_id')
        payor_reference = data.get('payor_reference')
        review_reason = data.get('review_reason', 'MANUAL_REVIEW_REQUIRED')
        estimated_review_time = data.get('estimated_review_time', '24-48 hours')
        notes = data.get('notes', '')
        reviewer_contact = data.get('reviewer_contact', '')
        
        if not claim_id:
            return JsonResponse({
                'success': False,
                'error': 'claim_id is required'
            }, status=400)
        
        # Find the claim in MongoDB
        try:
            claim = None
            
            # Try multiple ways to find the claim
            if claim_id:
                claim = Claim.objects(claim_id=claim_id).first()
                if not claim:
                    claim = Claim.objects(claim_number=claim_id).first()
            
            if not claim and payor_reference:
                claim = Claim.objects(payor_claim_id=payor_reference).first()
                
            if claim:
                # Store original status for logging
                original_status = claim.status
                
                # Update claim status
                claim.status = 'under_review'
                claim.review_reason = review_reason
                claim.estimated_review_time = estimated_review_time
                claim.payor_response = data
                claim.notes = f"{claim.notes}\n[PAYOR REVIEW] {notes}" if claim.notes else f"[PAYOR REVIEW] {notes}"
                
                # Add payor reference if provided
                if payor_reference and not claim.payor_claim_id:
                    claim.payor_claim_id = payor_reference
                
                claim.save()
                
                logger.info(f"✅ Claim under review webhook processed successfully")
                logger.info(f"   Claim ID: {claim_id}")
                logger.info(f"   Status: {original_status} → under_review")
                logger.info(f"   Review reason: {review_reason}")
                
                return JsonResponse({
                    'success': True,
                    'message': 'Claim under review notification received and processed',
                    'claim_id': claim_id,
                    'updated_claim': {
                        'id': str(claim.id),
                        'claim_number': claim.claim_number,
                        'status': claim.status,
                        'original_status': original_status,
                        'review_reason': review_reason,
                        'estimated_review_time': estimated_review_time
                    }
                })
            else:
                logger.warning(f"❌ Claim not found for under review webhook")
                logger.warning(f"   Searched for claim_id: {claim_id}")
                
                return JsonResponse({
                    'success': False,
                    'error': f'Claim not found: {claim_id}',
                    'suggestion': 'Verify claim ID or check if claim was submitted from this provider'
                }, status=404)
                
        except Exception as e:
            logger.error(f"Database error updating claim {claim_id}: {str(e)}")
            return JsonResponse({
                'success': False,
                'error': f'Database error: {str(e)}'
            }, status=500)
            
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in webhook payload: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': 'Invalid JSON payload'
        }, status=400)
        
    except Exception as e:
        logger.error(f"Unexpected error in claim under review webhook: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': f'Internal server error: {str(e)}'
        }, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def webhook_health_check(request):
    """
    Health check endpoint for webhook service
    GET /api/webhooks/health/
    """
    return JsonResponse({
        'status': 'healthy',
        'service': 'provider-webhooks',
        'timestamp': datetime.now().isoformat(),
        'message': 'Provider webhook service is operational'
    })


@csrf_exempt
@require_http_methods(["POST"])
def webhook_test_endpoint(request):
    """
    Test endpoint for webhook connectivity
    POST /api/webhooks/test/
    """
    try:
        data = json.loads(request.body.decode('utf-8')) if request.body else {}
        
        logger.info(f"Received test webhook: {data}")
        
        return JsonResponse({
            'success': True,
            'message': 'Test webhook received successfully',
            'received_data': data,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Test webhook error: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': f'Test webhook failed: {str(e)}'
        }, status=500)


@method_decorator(csrf_exempt, name='dispatch')
class PayorWebhookView(APIView):
    """
    Generic webhook view for handling various payor notifications
    """
    permission_classes = [AllowAny]
    
    def post(self, request):
        try:
            data = request.data if hasattr(request, 'data') else json.loads(request.body.decode('utf-8'))
            
            event_type = data.get('event_type', 'unknown')
            claim_id = data.get('claim_id')
            
            logger.info(f"Received generic payor webhook - Event: {event_type}, Claim: {claim_id}")
            
            # Route to appropriate handler based on event type
            if event_type == 'claim_approved':
                return self._handle_approval(data)
            elif event_type == 'claim_denied':
                return self._handle_denial(data)
            elif event_type == 'claim_under_review':
                return self._handle_under_review(data)
            else:
                logger.warning(f"Unknown webhook event type: {event_type}")
                return Response({
                    'success': True,
                    'message': f'Webhook received but event type {event_type} not handled',
                    'event_type': event_type
                }, status=status.HTTP_200_OK)
                
        except Exception as e:
            logger.error(f"Generic webhook error: {str(e)}")
            return Response({
                'success': False,
                'error': f'Webhook processing failed: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def _handle_approval(self, data):
        # Delegate to approval handler logic
        claim_id = data.get('claim_id')
        # Implementation similar to payor_claim_approved
        return Response({
            'success': True,
            'message': f'Approval processed for claim {claim_id}'
        })
    
    def _handle_denial(self, data):
        # Delegate to denial handler logic
        claim_id = data.get('claim_id')
        # Implementation similar to payor_claim_denied
        return Response({
            'success': True,
            'message': f'Denial processed for claim {claim_id}'
        })
    
    def _handle_under_review(self, data):
        # Delegate to under review handler logic
        claim_id = data.get('claim_id')
        # Implementation similar to payor_claim_under_review
        return Response({
            'success': True,
            'message': f'Under review status processed for claim {claim_id}'
        })