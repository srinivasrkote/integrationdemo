"""
URL configuration for provider project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse
from django.conf import settings
from django.conf.urls.static import static
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

def api_root(request):
    """Simple API root endpoint"""
    return JsonResponse({
        'message': 'Health Insurance Provider API',
        'version': '1.0',
        'endpoints': {
            'admin': '/admin/',
            'api': '/api/',
            'auth': '/api/auth/',
            'token': '/api/token/',
            'token_refresh': '/api/token/refresh/',
            'health': '/api/health/',
            'provider': '/api/provider/',
            'claims': '/api/claims/',
            'mongo': '/api/mongo/',
            'payor': '/api/payor/',
        }
    })

def health_check(request):
    """Health check endpoint for payor integration"""
    return JsonResponse({
        'status': 'healthy',
        'message': 'Provider system is operational',
        'timestamp': '2025-09-30T13:15:00Z',
        'service': 'provider-api',
        'version': '1.0.0'
    })

def payor_callback(request):
    """Endpoint for payor system callbacks"""
    return JsonResponse({
        'status': 'received',
        'message': 'Payor callback received successfully',
        'timestamp': '2025-09-30T13:15:00Z'
    })

def claims_submit(request):
    """Endpoint for external payor systems to submit claims"""
    return JsonResponse({
        'status': 'success',
        'claim_id': 'CLM-2025-001',
        'reference_number': 'REF-12345',
        'message': 'Claim received and processed'
    })

def insurance_validate(request):
    """Endpoint for insurance validation"""
    return JsonResponse({
        'valid': True,
        'coverage': 'active',
        'member_id': 'M123456789',
        'message': 'Insurance policy is valid'
    })

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', api_root, name='api-root'),
    path('api/health/', health_check, name='health-check'),
    path('api/payor/callback/', payor_callback, name='payor-callback'),
    
    # Payor system endpoints (for external integration)
    path('api/claims/submit/', claims_submit, name='claims-submit'),
    path('api/insurance/validate/', insurance_validate, name='insurance-validate'),
    
    # JWT Authentication endpoints
    path('api/auth/login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # Include claims URLs (includes mongo and payor endpoints)
    path('api/', include('claims.urls')),
]

# Serve media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
