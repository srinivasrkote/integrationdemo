from django.urls import path
from .views import (
    ProviderMeView,
    ClaimsCreateView,
    ClaimsListView,
    ClaimDetailView,
    ProviderStatsView,
    PatientSearchView
)
from .mongo_views import (
    MongoClaimListView,
    MongoClaimDetailView,
    MongoUserListView,
    MongoAuthView,
    MongoRegisterView,
    mongo_register_user,
    MongoDashboardStatsView,
    MongoUserProfileView
)
from .payor_views import (
    PayorIntegrationView,
    ClaimSyncView,
    PolicyValidationView
)

app_name = 'claims'

urlpatterns = [
    # Original Django ORM endpoints (for compatibility)
    path('provider/me/', ProviderMeView.as_view(), name='provider-me'),
    path('provider/stats/', ProviderStatsView.as_view(), name='provider-stats'),
    path('provider/patients/search/', PatientSearchView.as_view(), name='patient-search'),
    path('claims/', ClaimsListView.as_view(), name='claims-list'),
    path('claims/create/', ClaimsCreateView.as_view(), name='claims-create'),
    path('claims/<str:pk>/', ClaimDetailView.as_view(), name='claim-detail'),
    
    # MongoDB-based endpoints
    path('mongo/auth/', MongoAuthView.as_view(), name='mongo-auth'),
    path('mongo/register/', MongoRegisterView.as_view(), name='mongo-register'),
    path('mongo/register-test/', mongo_register_user, name='mongo-register-test'),
    path('mongo/claims/', MongoClaimListView.as_view(), name='mongo-claims-list'),
    path('mongo/claims/<str:claim_id>/', MongoClaimDetailView.as_view(), name='mongo-claim-detail'),
    path('mongo/users/', MongoUserListView.as_view(), name='mongo-users-list'),
    path('mongo/dashboard/stats/', MongoDashboardStatsView.as_view(), name='mongo-dashboard-stats'),
    path('mongo/profile/', MongoUserProfileView.as_view(), name='mongo-user-profile'),
    
    # Payor Integration endpoints
    path('payor/integration/', PayorIntegrationView.as_view(), name='payor-integration'),
    path('payor/sync/', ClaimSyncView.as_view(), name='payor-sync-all'),
    path('payor/sync/<str:claim_id>/', ClaimSyncView.as_view(), name='payor-sync-claim'),
    path('payor/validate/', PolicyValidationView.as_view(), name='payor-validate'),
]