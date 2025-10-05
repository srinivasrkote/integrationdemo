"""
Custom JWT authentication views for MongoDB users
"""
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from claims.mongo_models import User as MongoUser
import logging

logger = logging.getLogger(__name__)


class MongoTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Custom serializer that authenticates against MongoDB"""
    
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        # Add custom claims
        token['username'] = user.username
        token['role'] = getattr(user, 'role', 'provider')
        return token


@api_view(['POST'])
@permission_classes([AllowAny])
def mongo_token_obtain(request):
    """
    Custom JWT token obtain view that authenticates against MongoDB
    POST /api/auth/token/
    Body: {"username": "provider2", "password": "password@123", "role": "provider"} or {"username": "email@example.com", "password": "password@123", "role": "patient"}
    Returns: {"access": "...", "refresh": "...", "user": {...}}
    Note: 'username' field can accept either username or email address
    Note: 'role' field must match the user's actual role in the database
    """
    try:
        username = request.data.get('username')
        password = request.data.get('password')
        role = request.data.get('role')  # Get the selected role from frontend
        
        if not username or not password:
            return Response({
                'error': 'Username and password required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if not role:
            return Response({
                'error': 'Role selection required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        logger.info(f"JWT login attempt for: {username} as role: {role}")
        
        # Authenticate against MongoDB - check both username and email
        user = None
        try:
            # First try to find by username
            user = MongoUser.objects.get(username=username)
            logger.info(f"Found MongoDB user by username: {username}")
        except MongoUser.DoesNotExist:
            try:
                # If not found by username, try by email
                user = MongoUser.objects.get(email=username)
                logger.info(f"Found MongoDB user by email: {username}")
            except MongoUser.DoesNotExist:
                logger.error(f"User not found by username or email: {username}")
                return Response({
                    'error': 'Invalid credentials'
                }, status=status.HTTP_401_UNAUTHORIZED)
        
        # Verify password (check both hashed and plain text)
        from django.contrib.auth.hashers import check_password
        password_valid = False
        
        # Try Django hashed password first
        try:
            password_valid = check_password(password, user.password)
        except Exception:
            pass
        
        # If not valid as hash, try plain text comparison (for development)
        if not password_valid and user.password == password:
            password_valid = True
            logger.warning(f"User {username} using plain text password - should be hashed!")
        
        if not password_valid:
            logger.error(f"Invalid password for user: {user.username}")
            return Response({
                'error': 'Invalid credentials'
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        # Validate role matches user's actual role
        if user.role != role:
            logger.error(f"Role mismatch for user {user.username}: requested {role}, actual {user.role}")
            return Response({
                'error': f'Invalid credentials. You cannot login as {role} with this account.'
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        # Create Django User object in memory (for JWT compatibility)
        from django.contrib.auth import get_user_model
        DjangoUser = get_user_model()
        
        # Try to get or create Django user using the actual username from MongoDB
        try:
            django_user, created = DjangoUser.objects.get_or_create(
                username=user.username,  # Use actual username from MongoDB user
                defaults={
                    'email': user.email,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                }
            )
            if created:
                django_user.set_password(password)
                django_user.save()
                logger.info(f"Created Django user for: {user.username}")
        except Exception as e:
            logger.error(f"Error creating Django user: {e}")
            # Create a temporary user object for JWT
            django_user = DjangoUser(
                username=user.username,  # Use actual username from MongoDB user
                email=user.email,
                first_name=user.first_name,
                last_name=user.last_name
            )
            django_user.id = 1  # Temporary ID
        
        # Generate JWT tokens
        refresh = RefreshToken.for_user(django_user)
        refresh['username'] = user.username  # Use actual username from MongoDB user
        refresh['role'] = user.role
        
        logger.info(f"JWT tokens generated for: {user.username}")
        
        return Response({
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'user': {
                'username': user.username,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'role': user.role,
            }
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"JWT login error: {e}", exc_info=True)
        return Response({
            'error': 'Authentication failed',
            'detail': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([AllowAny])
def mongo_token_refresh(request):
    """
    Refresh JWT access token
    POST /api/auth/token/refresh/
    Body: {"refresh": "..."}
    Returns: {"access": "..."}
    """
    try:
        refresh_token = request.data.get('refresh')
        
        if not refresh_token:
            return Response({
                'error': 'Refresh token required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        refresh = RefreshToken(refresh_token)
        
        return Response({
            'access': str(refresh.access_token),
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Token refresh error: {e}")
        return Response({
            'error': 'Invalid refresh token'
        }, status=status.HTTP_401_UNAUTHORIZED)
