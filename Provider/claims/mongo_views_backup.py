"""
MongoDB-based API views using MongoEngine models
"""

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth import authenticate, login
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
import json
from datetime import datetime, timedelta
from bson import ObjectId
from .mongo_models import User, Claim, ClaimDocument, ClaimStatusHistory
from .payor_integration import payor_service


def serialize_claim(claim):
    """S        except Exception as e:
            return Response(
                {'error': f'Failed to get user profile: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


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
            )ize a Claim document to dictionary"""
    return {
        'id': str(claim.id),
        'claim_id': str(claim.claim_id),
        'claim_number': claim.claim_number,
        'patient_id': str(claim.patient_id) if claim.patient_id else None,
        'provider_id': str(claim.provider_id) if claim.provider_id else None,
        'patient_name': claim.patient_name,
        'patient_email': claim.patient_email,
        'provider_name': claim.provider_name,
        'provider_email': claim.provider_email,
        'insurance_id': claim.insurance_id,
        'diagnosis_code': claim.diagnosis_code,
        'diagnosis_description': claim.diagnosis_description,
        'procedure_code': claim.procedure_code,
        'procedure_description': claim.procedure_description,
        'amount_requested': float(claim.amount_requested) if claim.amount_requested else 0,
        'amount_approved': float(claim.amount_approved) if claim.amount_approved else 0,
        'status': claim.status,
        'priority': claim.priority,
        'date_of_service': claim.date_of_service.isoformat() if claim.date_of_service else None,
        'date_submitted': claim.date_submitted.isoformat() if claim.date_submitted else None,
        'date_updated': claim.date_updated.isoformat() if claim.date_updated else None,
        'date_processed': claim.date_processed.isoformat() if claim.date_processed else None,
        'notes': claim.notes,
        'rejection_reason': claim.rejection_reason,
        'provider_npi': claim.provider_npi,
        'provider_tax_id': claim.provider_tax_id,
        # Payor integration fields
        'payor_claim_id': claim.payor_claim_id,
        'payor_name': claim.payor_name,
        'submitted_to_payor': claim.submitted_to_payor,
        'payor_submission_date': claim.payor_submission_date.isoformat() if claim.payor_submission_date else None,
        'payor_response': claim.payor_response,
    }


def serialize_user(user):
    """Serialize a User document to dictionary"""
    return {
        'id': str(user.id),
        'username': user.username,
        'email': user.email,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'role': user.role,
        'phone': user.phone,
        'date_of_birth': user.date_of_birth.isoformat() if user.date_of_birth else None,
        'insurance_id': user.insurance_id,
        'is_active': user.is_active,
        'date_joined': user.date_joined.isoformat() if user.date_joined else None,
    }


@method_decorator(csrf_exempt, name='dispatch')
class MongoClaimListView(APIView):
    """MongoDB-based claim list view"""
    authentication_classes = []  # Disable DRF authentication
    permission_classes = [AllowAny]  # Allow access without authentication for now
    
    def get(self, request):
        """Get all claims with filtering"""
        try:
            # Get query parameters
            status_filter = request.GET.get('status', None)
            provider_id = request.GET.get('provider_id', None)
            patient_id = request.GET.get('patient_id', None)
            
            # Try to identify current user from auth header
            current_provider_id = None
            auth_header = request.META.get('HTTP_AUTHORIZATION', '')
            if auth_header and auth_header.startswith('Basic '):
                try:
                    import base64
                    encoded_credentials = auth_header.split(' ')[1]
                    decoded_credentials = base64.b64decode(encoded_credentials).decode('utf-8')
                    username, _ = decoded_credentials.split(':', 1)
                    
                    # Find provider user
                    provider_user = User.objects(username=username, is_active=True).first()
                    if provider_user:
                        current_provider_id = provider_user.id
                        print(f"📋 Loading claims for provider: {username}")
                except Exception as e:
                    print(f"⚠️ Could not identify provider for claims filter: {e}")
            
            # Build query
            query = {}
            if status_filter:
                query['status'] = status_filter
            if provider_id:
                query['provider_id'] = ObjectId(provider_id)
            elif current_provider_id:
                # Filter by current provider if no specific provider_id requested
                query['provider_id'] = current_provider_id
            if patient_id:
                query['patient_id'] = ObjectId(patient_id)
            
            # Get claims
            claims = Claim.objects(**query).order_by('-date_submitted')
            
            # Serialize claims
            claims_data = [serialize_claim(claim) for claim in claims]
            
            return Response({
                'count': len(claims_data),
                'results': claims_data
            })
            
        except Exception as e:
            return Response(
                {'error': f'Failed to fetch claims: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def post(self, request):
        """Create a new claim"""
        try:
            data = request.data
            print(f"🏥 CLAIM CREATION REQUEST: {data}")
            
            # Validate required fields
            required_fields = ['patient_name', 'insurance_id', 'diagnosis_description', 'amount_requested']
            missing_fields = [field for field in required_fields if not data.get(field)]
            if missing_fields:
                print(f"❌ Missing required fields: {missing_fields}")
                return Response(
                    {'error': f'Missing required fields: {", ".join(missing_fields)}'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Create new claim
            claim = Claim(
                insurance_id=data.get('insurance_id', ''),
                diagnosis_description=data.get('diagnosis_description', ''),
                diagnosis_code=data.get('diagnosis_code', ''),
                procedure_description=data.get('procedure_description', ''),
                procedure_code=data.get('procedure_code', ''),
                amount_requested=float(data.get('amount_requested', 0)),
                status=data.get('status', 'pending'),
                priority=data.get('priority', 'medium'),
                notes=data.get('notes', ''),
                provider_npi=data.get('provider_npi', ''),
                provider_tax_id=data.get('provider_tax_id', ''),
            )
            
            # Set patient info
            claim.patient_name = data.get('patient_name', '')
            
            # Set provider info from authentication (if available)
            auth_header = request.META.get('HTTP_AUTHORIZATION', '')
            if auth_header and auth_header.startswith('Basic '):
                try:
                    import base64
                    encoded_credentials = auth_header.split(' ')[1]
                    decoded_credentials = base64.b64decode(encoded_credentials).decode('utf-8')
                    username, _ = decoded_credentials.split(':', 1)
                    
                    # Find provider user
                    provider_user = User.objects(username=username, is_active=True).first()
                    if provider_user:
                        claim.provider_id = provider_user.id
                        claim.provider_name = f"{provider_user.first_name} {provider_user.last_name}".strip()
                        claim.provider_email = provider_user.email
                        print(f"🏥 Claim assigned to provider: {claim.provider_name} ({username})")
                except Exception as e:
                    print(f"⚠️ Could not identify provider: {e}")
            
            # Set patient ID and email if provided
            if data.get('patient_id'):
                claim.patient_id = ObjectId(data['patient_id'])
                # Get patient email from database
                try:
                    patient = User.objects(id=ObjectId(data['patient_id'])).first()
                    if patient:
                        claim.patient_email = patient.email
                except:
                    pass
            elif data.get('patient'):
                # Handle numeric patient ID
                try:
                    patient = User.objects().skip(int(data['patient']) - 1).first()
                    if patient:
                        claim.patient_id = patient.id
                        claim.patient_email = patient.email
                except:
                    pass
            
            if data.get('provider_id'):
                claim.provider_id = ObjectId(data['provider_id'])
                # Get provider info
                try:
                    provider = User.objects(id=ObjectId(data['provider_id'])).first()
                    if provider:
                        claim.provider_name = f"{provider.first_name} {provider.last_name}"
                        claim.provider_email = provider.email
                except:
                    pass
            
            # Set dates
            if data.get('date_of_service'):
                claim.date_of_service = datetime.fromisoformat(data['date_of_service'].replace('Z', '+00:00'))
            
            print(f"💾 Saving claim to MongoDB...")
            claim.save()
            print(f"✅ Claim saved successfully with ID: {claim.id}")
            
            # PAYOR INTEGRATION: Submit claim to payor system
            print(f"🏢 Submitting claim to payor system...")
            try:
                # Prepare claim data for payor submission
                claim_data_for_payor = {
                    'patient_name': claim.patient_name,
                    'insurance_id': claim.insurance_id,
                    'diagnosis_code': claim.diagnosis_code,
                    'diagnosis_description': claim.diagnosis_description,
                    'procedure_code': claim.procedure_code,
                    'procedure_description': claim.procedure_description,
                    'amount_requested': float(claim.amount_requested),
                    'date_of_service': claim.date_of_service.isoformat() if claim.date_of_service else None,
                    'provider_name': claim.provider_name,
                    'provider_email': claim.provider_email,
                    'provider_npi': claim.provider_npi,
                    'notes': claim.notes,
                    'priority': claim.priority
                }
                
                # Submit to payor system
                payor_result = payor_service.submit_claim_to_payor(claim_data_for_payor)
                
                if payor_result['success']:
                    # Update claim with payor information
                    claim.submitted_to_payor = True
                    claim.payor_claim_id = payor_result['payor_claim_id']
                    claim.payor_submission_date = datetime.now()
                    claim.payor_response = payor_result['payor_response']
                    
                    # Get payor name from insurance mapping
                    if claim.insurance_id in payor_service.insurance_mappings:
                        claim.payor_name = payor_service.insurance_mappings[claim.insurance_id]['payor_name']
                    
                    claim.save()
                    print(f"✅ Claim submitted to payor successfully. Payor Claim ID: {claim.payor_claim_id}")
                else:
                    print(f"⚠️ Failed to submit to payor: {payor_result['error']}")
                    # Still save the claim locally even if payor submission fails
                    claim.submitted_to_payor = False
                    claim.payor_response = {'error': payor_result['error']}
                    claim.save()
                    
            except Exception as e:
                print(f"❌ Error submitting to payor: {str(e)}")
                # Still save the claim locally
                claim.submitted_to_payor = False
                claim.payor_response = {'error': str(e)}
                claim.save()
            
            serialized_claim = serialize_claim(claim)
            print(f"📄 Serialized claim: {serialized_claim}")
            
            return Response(serialized_claim, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            print(f"❌ Error creating claim: {str(e)}")
            import traceback
            print(f"🔍 Full traceback: {traceback.format_exc()}")
            return Response(
                {'error': f'Failed to create claim: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )


@method_decorator(csrf_exempt, name='dispatch')
class MongoClaimDetailView(APIView):
    """MongoDB-based claim detail view"""
    authentication_classes = []  # Disable DRF authentication
    permission_classes = [AllowAny]
    
    def get(self, request, claim_id):
        """Get a specific claim"""
        try:
            claim = Claim.objects(id=ObjectId(claim_id)).first()
            if not claim:
                return Response(
                    {'error': 'Claim not found'},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            return Response(serialize_claim(claim))
            
        except Exception as e:
            return Response(
                {'error': f'Failed to fetch claim: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def put(self, request, claim_id):
        """Update a specific claim"""
        try:
            claim = Claim.objects(id=ObjectId(claim_id)).first()
            if not claim:
                return Response(
                    {'error': 'Claim not found'},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            data = request.data
            
            # Update fields
            updatable_fields = [
                'insurance_id', 'diagnosis_description', 'diagnosis_code', 'procedure_description',
                'procedure_code', 'amount_requested', 'amount_approved', 'status',
                'priority', 'notes', 'rejection_reason', 'provider_npi', 'provider_tax_id'
            ]
            
            for field in updatable_fields:
                if field in data:
                    setattr(claim, field, data[field])
            
            # Handle date fields
            if 'date_of_service' in data and data['date_of_service']:
                claim.date_of_service = datetime.fromisoformat(data['date_of_service'].replace('Z', '+00:00'))
            
            if 'date_processed' in data and data['date_processed']:
                claim.date_processed = datetime.fromisoformat(data['date_processed'].replace('Z', '+00:00'))
            
            claim.save()
            
            return Response(serialize_claim(claim))
            
        except Exception as e:
            return Response(
                {'error': f'Failed to update claim: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    def delete(self, request, claim_id):
        """Delete a specific claim"""
        try:
            claim = Claim.objects(id=ObjectId(claim_id)).first()
            if not claim:
                return Response(
                    {'error': 'Claim not found'},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            claim.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
            
        except Exception as e:
            return Response(
                {'error': f'Failed to delete claim: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


@method_decorator(csrf_exempt, name='dispatch')
class MongoUserListView(APIView):
    """MongoDB-based user list view"""
    
    def get(self, request):
        """Get all users with filtering"""
        try:
            role_filter = request.GET.get('role', None)
            
            query = {}
            if role_filter:
                query['role'] = role_filter
            
            users = User.objects(**query).order_by('username')
            users_data = [serialize_user(user) for user in users]
            
            return Response({
                'count': len(users_data),
                'results': users_data
            })
            
        except Exception as e:
            return Response(
                {'error': f'Failed to fetch users: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


@api_view(['POST'])
@permission_classes([AllowAny])
@csrf_exempt
def mongo_register_user(request):
    """Function-based view for user registration (for testing)"""
    try:
        print(f"Function-based registration request: {request.data}")
        
        data = request.data if hasattr(request, 'data') else json.loads(request.body)
        
        # Required fields
        username = data.get('username', '').strip()
        email = data.get('email', '').strip()
        password = data.get('password', '')
        first_name = data.get('first_name', '').strip()
        last_name = data.get('last_name', '').strip()
        role = data.get('role', 'patient')
        
        print(f"Function-based parsed data - username: {username}, email: {email}")
        
        # Validate required fields
        if not all([username, email, password, first_name, last_name]):
            return JsonResponse(
                {'error': 'All fields are required: username, email, password, first_name, last_name'},
                status=400
            )
        
        # Check if username already exists
        if User.objects(username=username).first():
            return JsonResponse({'error': 'Username already exists'}, status=400)
        
        # Check if email already exists
        if User.objects(email=email).first():
            return JsonResponse({'error': 'Email already exists'}, status=400)
        
        # Create new user
        user = User(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            role=role,
            phone=data.get('phone', ''),
            insurance_id=data.get('insurance_id', ''),
            is_active=True,
            date_joined=datetime.now()
        )
        
        user.save()
        print(f"Function-based user {username} saved successfully")
        
        return JsonResponse({
            'message': 'User registered successfully',
            'user': serialize_user(user)
        }, status=201)
        
    except Exception as e:
        print(f"Function-based registration error: {str(e)}")
        import traceback
        traceback.print_exc()
        return JsonResponse({'error': f'Registration failed: {str(e)}'}, status=500)


@method_decorator(csrf_exempt, name='dispatch')
class MongoDashboardStatsView(APIView):
    """MongoDB-based dashboard stats view"""
    authentication_classes = []  # Disable DRF authentication
    permission_classes = [AllowAny]
    
    def get(self, request):
        """Get dashboard statistics from MongoDB"""
        try:
            # Try to identify current user from auth header
            current_provider_id = None
            auth_header = request.META.get('HTTP_AUTHORIZATION', '')
            if auth_header and auth_header.startswith('Basic '):
                try:
                    import base64
                    encoded_credentials = auth_header.split(' ')[1]
                    decoded_credentials = base64.b64decode(encoded_credentials).decode('utf-8')
                    username, _ = decoded_credentials.split(':', 1)
                    
                    # Find provider user
                    provider_user = User.objects(username=username, is_active=True).first()
                    if provider_user:
                        current_provider_id = provider_user.id
                        print(f"📊 Loading stats for provider: {username}")
                except Exception as e:
                    print(f"⚠️ Could not identify provider for stats: {e}")
            
            # Filter claims by current provider
            base_query = {}
            if current_provider_id:
                base_query['provider_id'] = current_provider_id
            
            # Get counts
            total_claims = Claim.objects(**base_query).count()
            pending_claims = Claim.objects(status='pending', **base_query).count()
            approved_claims = Claim.objects(status='approved', **base_query).count()
            rejected_claims = Claim.objects(status='rejected', **base_query).count()
            
            # Get recent claims
            recent_claims = Claim.objects(**base_query).order_by('-date_submitted')[:5]
            recent_claims_data = [serialize_claim(claim) for claim in recent_claims]
            
            # Calculate approval rate
            processed_claims = approved_claims + rejected_claims
            approval_rate = (approved_claims / processed_claims * 100) if processed_claims > 0 else 0
            
            return Response({
                'total_claims': total_claims,
                'pending_claims': pending_claims,
                'approved_claims': approved_claims,
                'rejected_claims': rejected_claims,
                'approval_rate': round(approval_rate, 2),
                'recent_claims': recent_claims_data,
            })
            
        except Exception as e:
            return Response(
                {'error': f'Failed to get dashboard stats: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


@method_decorator(csrf_exempt, name='dispatch')
class MongoAuthView(APIView):
    """MongoDB-based authentication view"""
    authentication_classes = []  # Disable DRF authentication
    permission_classes = [AllowAny]
    
    def post(self, request):
        """Authenticate user with MongoDB"""
        try:
            data = request.data
            username = data.get('username')
            password = data.get('password')
            
            # Debug: Log the login attempt
            print(f"🔐 LOGIN ATTEMPT: username='{username}', password='{password}'")
            
            if not username or not password:
                print("❌ Missing username or password")
                return Response(
                    {'error': 'Username and password required'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Find user in MongoDB
            user = User.objects(username=username, is_active=True).first()
            
            if not user:
                print(f"❌ User '{username}' not found in database")
                return Response(
                    {'error': 'Invalid credentials'},
                    status=status.HTTP_401_UNAUTHORIZED
                )
            
            print(f"✅ Found user: {user.username}, stored password: '{user.password}'")
            
            # In a real application, you should hash and verify passwords
            # For now, we'll do a simple comparison (NOT SECURE FOR PRODUCTION)
            if user.password != password:  # In production, use proper password hashing
                print(f"❌ Password mismatch - received: '{password}', stored: '{user.password}'")
                return Response(
                    {'error': 'Invalid credentials'},
                    status=status.HTTP_401_UNAUTHORIZED
                )
            
            # Update last login
            user.last_login = datetime.now()
            user.save()
            
            print(f"✅ LOGIN SUCCESS: {user.username} ({user.role})")
            
            return Response({
                'message': 'Login successful',
                'user': serialize_user(user)
            })
            
        except Exception as e:
            return Response(
                {'error': f'Authentication failed: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


@method_decorator(csrf_exempt, name='dispatch')
class MongoRegisterView(APIView):
    """MongoDB-based user registration view"""
    permission_classes = [AllowAny]
    
    def post(self, request):
        """Register a new user in MongoDB"""
        try:
            # Debug: Log the incoming request
            print(f"Registration request received: {request.data}")
            
            data = request.data
            
            # Required fields
            username = data.get('username', '').strip()
            email = data.get('email', '').strip()
            password = data.get('password', '')
            first_name = data.get('first_name', '').strip()
            last_name = data.get('last_name', '').strip()
            role = data.get('role', 'patient')
            
            # Debug: Log parsed data
            print(f"Parsed data - username: {username}, email: {email}, role: {role}")
            
            # Validate required fields
            if not all([username, email, password, first_name, last_name]):
                return Response(
                    {'error': 'All fields are required: username, email, password, first_name, last_name'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Validate role
            valid_roles = ['patient', 'provider', 'payor']
            if role not in valid_roles:
                return Response(
                    {'error': f'Invalid role. Must be one of: {", ".join(valid_roles)}'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Check if username already exists
            print(f"Checking if username {username} exists...")
            existing_user = User.objects(username=username).first()
            if existing_user:
                print(f"Username {username} already exists")
                return Response(
                    {'error': 'Username already exists'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Check if email already exists
            print(f"Checking if email {email} exists...")
            existing_email = User.objects(email=email).first()
            if existing_email:
                print(f"Email {email} already exists")
                return Response(
                    {'error': 'Email already exists'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Create new user
            user = User(
                username=username,
                email=email,
                password=password,  # In production, hash this password
                first_name=first_name,
                last_name=last_name,
                role=role,
                phone=data.get('phone', ''),
                insurance_id=data.get('insurance_id', ''),
                is_active=True,
                date_joined=datetime.now()
            )
            
            # Set date_of_birth if provided
            if data.get('date_of_birth'):
                try:
                    user.date_of_birth = datetime.fromisoformat(data['date_of_birth'].replace('Z', '+00:00'))
                except:
                    pass
            
            print(f"Saving new user: {username}")
            user.save()
            print(f"User {username} saved successfully")
            
            response_data = {
                'message': 'User registered successfully',
                'user': serialize_user(user)
            }
            print(f"Returning response: {response_data}")
            
            return Response(response_data, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            print(f"Registration error: {str(e)}")
            import traceback
            traceback.print_exc()
            return Response(
                {'error': f'Registration failed: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


@method_decorator(csrf_exempt, name='dispatch')
class MongoUserProfileView(APIView):
    """MongoDB-based user profile view"""
    authentication_classes = []  # Disable DRF authentication
    permission_classes = [AllowAny]
    
    def get(self, request):
        """Get user profile from MongoDB based on Basic Auth credentials"""
        try:
            # Get authorization header
            auth_header = request.META.get('HTTP_AUTHORIZATION', '')
            print(f"Profile request auth header: {auth_header}")
            
            if not auth_header or not auth_header.startswith('Basic '):
                # For testing, return a default provider user if no auth header
                user = User.objects(role='provider', is_active=True).first()
                if user:
                    print(f"No auth header, returning default provider: {user.username}")
                    return Response({
                        'message': 'Profile retrieved successfully',
                        'user': serialize_user(user)
                    })
                else:
                    return Response(
                        {'error': 'Authorization header required'},
                        status=status.HTTP_401_UNAUTHORIZED
                    )
            
            # Decode Basic Auth
            import base64
            try:
                encoded_credentials = auth_header.split(' ')[1]
                decoded_credentials = base64.b64decode(encoded_credentials).decode('utf-8')
                username, password = decoded_credentials.split(':', 1)
                print(f"Profile request - Username: {username}, Password: {password}")
            except Exception as e:
                print(f"Error decoding auth header: {e}")
                return Response(
                    {'error': 'Invalid authorization header format'},
                    status=status.HTTP_401_UNAUTHORIZED
                )
            
            # Find and validate user in MongoDB
            user = User.objects(username=username, is_active=True).first()
            
            if not user:
                print(f"User {username} not found in MongoDB")
                return Response(
                    {'error': 'Invalid credentials'},
                    status=status.HTTP_401_UNAUTHORIZED
                )
            
            print(f"Found user: {user.username}, stored password: {user.password}")
            
            if user.password != password:
                print(f"Password mismatch - received: {password}, stored: {user.password}")
                return Response(
                    {'error': 'Invalid credentials'},
                    status=status.HTTP_401_UNAUTHORIZED
                )
            
            return Response({
                'message': 'Profile retrieved successfully',
                'user': serialize_user(user)
            })
                
        except Exception as e:
            return Response(
                {'error': f'Failed to get profile: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )