from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django.db import models
from .models import Claim, ClaimDocument, ClaimStatusHistory
from .serializers import ClaimSerializer, ClaimCreateSerializer, UserSerializer

User = get_user_model()


class ProviderMeView(APIView):
    """Get current provider user information"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        if request.user.role != "provider":
            return Response({"error": "Forbidden"}, status=status.HTTP_403_FORBIDDEN)
        
        return Response({
            "userId": request.user.id,
            "name": request.user.username,
            "email": request.user.email,
            "role": request.user.role,
            "firstName": request.user.first_name,
            "lastName": request.user.last_name,
            "phone": request.user.phone,
        })


class ClaimsCreateView(generics.CreateAPIView):
    """Create a new claim"""
    serializer_class = ClaimCreateSerializer
    permission_classes = [IsAuthenticated]
    
    def perform_create(self, serializer):
        # Ensure only providers can create claims
        if self.request.user.role != "provider":
            return Response({"error": "Only providers can create claims"}, status=status.HTTP_403_FORBIDDEN)
        
        # Set the provider to the current user
        serializer.save(provider=self.request.user)
    
    def create(self, request, *args, **kwargs):
        # Check if user is a provider
        if request.user.role != "provider":
            return Response({"error": "Only providers can create claims"}, status=status.HTTP_403_FORBIDDEN)
        
        return super().create(request, *args, **kwargs)


class ClaimsListView(generics.ListAPIView):
    """List all claims for the current provider"""
    serializer_class = ClaimSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        # Ensure only providers can access this view
        if self.request.user.role != "provider":
            return Claim.objects.none()
        
        # Return claims created by the current provider
        queryset = Claim.objects.filter(provider=self.request.user)
        
        # Optional filtering by status
        status_filter = self.request.query_params.get('status', None)
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        # Optional filtering by priority
        priority_filter = self.request.query_params.get('priority', None)
        if priority_filter:
            queryset = queryset.filter(priority=priority_filter)
        
        # Optional search by patient name or claim number
        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(
                models.Q(patient__username__icontains=search) |
                models.Q(patient__first_name__icontains=search) |
                models.Q(patient__last_name__icontains=search) |
                models.Q(claim_number__icontains=search) |
                models.Q(diagnosis_description__icontains=search)
            )
        
        return queryset.select_related('patient', 'provider').prefetch_related('documents', 'status_history')


class ClaimDetailView(generics.RetrieveUpdateAPIView):
    """Retrieve and update a specific claim"""
    serializer_class = ClaimSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        # Providers can only access their own claims
        if self.request.user.role == "provider":
            return Claim.objects.filter(provider=self.request.user)
        # Patients can only access their own claims
        elif self.request.user.role == "patient":
            return Claim.objects.filter(patient=self.request.user)
        # Payors can access all claims
        elif self.request.user.role == "payor":
            return Claim.objects.all()
        else:
            return Claim.objects.none()
    
    def get_object(self):
        queryset = self.get_queryset()
        claim_id = self.kwargs.get('pk')
        
        # Support both UUID and claim_number lookup
        try:
            # Try UUID first
            obj = get_object_or_404(queryset, id=claim_id)
        except:
            # Try claim_number
            obj = get_object_or_404(queryset, claim_number=claim_id)
        
        return obj
    
    def perform_update(self, serializer):
        # Create status history when status changes
        claim = self.get_object()
        old_status = claim.status
        new_status = serializer.validated_data.get('status', old_status)
        
        # Save the claim
        updated_claim = serializer.save()
        
        # Create status history if status changed
        if old_status != new_status:
            ClaimStatusHistory.objects.create(
                claim=updated_claim,
                previous_status=old_status,
                new_status=new_status,
                changed_by=self.request.user,
                notes=f"Status changed from {old_status} to {new_status}"
            )


class ProviderStatsView(APIView):
    """Get provider statistics"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        if request.user.role != "provider":
            return Response({"error": "Forbidden"}, status=status.HTTP_403_FORBIDDEN)
        
        claims = Claim.objects.filter(provider=request.user)
        
        stats = {
            "total_claims": claims.count(),
            "pending_claims": claims.filter(status='pending').count(),
            "approved_claims": claims.filter(status='approved').count(),
            "rejected_claims": claims.filter(status='rejected').count(),
            "under_review_claims": claims.filter(status='under_review').count(),
            "total_revenue": float(sum(claim.amount_approved or 0 for claim in claims.filter(status='approved'))),
            "total_requested": float(sum(claim.amount_requested for claim in claims)),
        }
        
        return Response(stats)


class PatientSearchView(APIView):
    """Search for patients by insurance ID or name"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        if request.user.role != "provider":
            return Response({"error": "Forbidden"}, status=status.HTTP_403_FORBIDDEN)
        
        query = request.query_params.get('q', '')
        if not query:
            return Response({"error": "Query parameter 'q' is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        # Search patients by insurance_id, username, first_name, last_name, or email
        patients = User.objects.filter(
            role='patient'
        ).filter(
            models.Q(insurance_id__icontains=query) |
            models.Q(username__icontains=query) |
            models.Q(first_name__icontains=query) |
            models.Q(last_name__icontains=query) |
            models.Q(email__icontains=query)
        )[:10]  # Limit to 10 results
        
        serializer = UserSerializer(patients, many=True)
        return Response(serializer.data)
