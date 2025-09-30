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
    """Serialize a Claim document to dictionary"""
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
    """MongoDB-based claims list and create view"""
    authentication_classes = []  # Disable DRF authentication
    permission_classes = [AllowAny]
    
    def get(self, request):
        """Get list of claims"""
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
                        print(f"📋 Loading claims for provider: {username}")
                except Exception as e:
                    print(f"⚠️ Could not identify provider: {e}")
            
            # Filter claims by current provider
            base_query = {}
            if current_provider_id:
                base_query['provider_id'] = current_provider_id
            
            claims = Claim.objects(**base_query).order_by('-date_submitted')
            claims_data = [serialize_claim(claim) for claim in claims]
            
            print(f"📋 Found {len(claims_data)} claims for provider")
            
            return Response({
                'count': len(claims_data),
                'results': claims_data
            })
            
        except Exception as e:
            print(f"❌ Error fetching claims: {str(e)}")
            return Response(
                {'error': f'Failed to fetch claims: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def post(self, request):
        """Create a new claim"""
        try:
            data = json.loads(request.body)
            print(f"📥 Received claim data: {data}")
            
            # Validate required fields
            required_fields = ['insurance_id', 'diagnosis_description']
            for field in required_fields:
                if not data.get(field):
                    return Response(
                        {'error': f'{field} is required'},
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
            # Find the claim
            claim = Claim.objects(id=ObjectId(claim_id)).first()
            if not claim:
                return Response(
                    {'error': 'Claim not found'},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # Check if the user can edit this claim
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
                except Exception as e:
                    print(f"⚠️ Could not identify provider: {e}")
            
            # Only allow providers to edit their own claims
            if current_provider_id and claim.provider_id != current_provider_id:
                return Response(
                    {'error': 'You can only edit your own claims'},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            data = json.loads(request.body)
            print(f"📝 Updating claim {claim_id} with data: {data}")
            
            # Update fields if provided
            if 'patient_name' in data:
                claim.patient_name = data['patient_name']
            if 'insurance_id' in data:
                claim.insurance_id = data['insurance_id']
            if 'diagnosis_code' in data:
                claim.diagnosis_code = data['diagnosis_code']
            if 'diagnosis_description' in data:
                claim.diagnosis_description = data['diagnosis_description']
            if 'procedure_code' in data:
                claim.procedure_code = data['procedure_code']
            if 'procedure_description' in data:
                claim.procedure_description = data['procedure_description']
            if 'amount_requested' in data:
                claim.amount_requested = float(data['amount_requested'])
            if 'status' in data:
                claim.status = data['status']
            if 'priority' in data:
                claim.priority = data['priority']
            if 'notes' in data:
                claim.notes = data['notes']
            if 'provider_npi' in data:
                claim.provider_npi = data['provider_npi']
            if 'provider_tax_id' in data:
                claim.provider_tax_id = data['provider_tax_id']
            
            # Update dates
            if 'date_of_service' in data and data['date_of_service']:
                claim.date_of_service = datetime.fromisoformat(data['date_of_service'].replace('Z', '+00:00'))
            
            # Update the date_updated field
            claim.date_updated = datetime.now()
            
            # Save the updated claim
            claim.save()
            print(f"✅ Claim {claim_id} updated successfully")
            
            return Response(serialize_claim(claim))
            
        except Exception as e:
            print(f"❌ Error updating claim {claim_id}: {str(e)}")
            import traceback
            print(f"🔍 Full traceback: {traceback.format_exc()}")
            return Response(
                {'error': f'Failed to update claim: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    def patch(self, request, claim_id):
        """Partially update a specific claim"""
        # Use the same logic as PUT for partial updates
        return self.put(request, claim_id)


@method_decorator(csrf_exempt, name='dispatch')
class MongoUserListView(APIView):
    """MongoDB-based users list view"""
    authentication_classes = []  # Disable DRF authentication
    permission_classes = [AllowAny]
    
    def get(self, request):
        """Get list of users"""
        try:
            users = User.objects(is_active=True).order_by('-date_joined')[:50]  # Limit to 50 users
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


@method_decorator(csrf_exempt, name='dispatch')
class MongoAuthView(APIView):
    """MongoDB-based authentication view"""
    authentication_classes = []  # Disable DRF authentication
    permission_classes = [AllowAny]
    
    def post(self, request):
        """Authenticate user with MongoDB"""
        try:
            data = json.loads(request.body)
            username = data.get('username')
            password = data.get('password')
            
            if not username or not password:
                return Response(
                    {'error': 'Username and password are required'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Find user in MongoDB
            user = User.objects(username=username, is_active=True).first()
            
            if not user:
                return Response(
                    {'error': 'Invalid credentials'},
                    status=status.HTTP_401_UNAUTHORIZED
                )
            
            # Check password (plain text comparison for now)
            if user.password != password:
                return Response(
                    {'error': 'Invalid credentials'},
                    status=status.HTTP_401_UNAUTHORIZED
                )
            
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
    authentication_classes = []  # Disable DRF authentication
    permission_classes = [AllowAny]
    
    def post(self, request):
        """Register a new user with MongoDB"""
        try:
            data = json.loads(request.body)
            
            # Required fields
            required_fields = ['username', 'email', 'password', 'first_name', 'last_name', 'role']
            for field in required_fields:
                if not data.get(field):
                    return Response(
                        {'error': f'{field} is required'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            
            # Check if user already exists
            if User.objects(username=data['username']).first():
                return Response(
                    {'error': 'Username already exists'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            if User.objects(email=data['email']).first():
                return Response(
                    {'error': 'Email already exists'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Create new user
            user = User(
                username=data['username'],
                email=data['email'],
                password=data['password'],  # Store plain text for now
                first_name=data['first_name'],
                last_name=data['last_name'],
                role=data['role'],
                phone=data.get('phone', ''),
                insurance_id=data.get('insurance_id', ''),
                is_active=True,
                date_joined=datetime.now()
            )
            
            if data.get('date_of_birth'):
                user.date_of_birth = datetime.fromisoformat(data['date_of_birth'].replace('Z', '+00:00'))
            
            user.save()
            
            return Response({
                'message': 'User registered successfully',
                'user': serialize_user(user)
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response(
                {'error': f'Registration failed: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


@api_view(['POST'])
@permission_classes([AllowAny])
@csrf_exempt
def mongo_register_user(request):
    """Simple function-based view for user registration"""
    try:
        data = json.loads(request.body)
        
        username = data.get('username', 'testuser')
        email = data.get('email', 'test@example.com')
        password = data.get('password', 'testpass')
        first_name = data.get('first_name', 'Test')
        last_name = data.get('last_name', 'User')
        role = data.get('role', 'provider')
        
        # Check if user exists
        existing_user = User.objects(username=username).first()
        if existing_user:
            return JsonResponse({'error': f'User {username} already exists'}, status=400)
        
        # Create user
        user = User(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            role=role,
            is_active=True,
            date_joined=datetime.now()
        )
        user.save()
        
        return JsonResponse({
            'message': f'User {username} created successfully',
            'user_id': str(user.id)
        })
        
    except Exception as e:
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
class MongoUserProfileView(APIView):
    """MongoDB-based user profile view"""
    authentication_classes = []
    permission_classes = [AllowAny]
    
    def get(self, request):
        """Get user profile using Basic Auth"""
        try:
            # Get credentials from Authorization header
            auth_header = request.META.get('HTTP_AUTHORIZATION', '')
            if not auth_header or not auth_header.startswith('Basic '):
                return Response(
                    {'error': 'Basic authentication required'},
                    status=status.HTTP_401_UNAUTHORIZED
                )
            
            # Decode credentials
            import base64
            encoded_credentials = auth_header.split(' ')[1]
            decoded_credentials = base64.b64decode(encoded_credentials).decode('utf-8')
            username, password = decoded_credentials.split(':', 1)
            
            print(f"Profile request for username: {username}")
            
            # Find user
            user = User.objects(username=username, is_active=True).first()
            if not user:
                print(f"User not found: {username}")
                return Response(
                    {'error': 'User not found'},
                    status=status.HTTP_404_NOT_FOUND
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