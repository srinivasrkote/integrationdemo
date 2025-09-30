from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Claim, ClaimDocument, ClaimStatusHistory

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    """Serializer for user information"""
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'role', 'phone', 'date_of_birth', 'insurance_id']
        read_only_fields = ['id']


class ClaimDocumentSerializer(serializers.ModelSerializer):
    """Serializer for claim documents"""
    
    class Meta:
        model = ClaimDocument
        fields = ['id', 'document_type', 'file', 'filename', 'uploaded_at', 'uploaded_by']
        read_only_fields = ['id', 'uploaded_at', 'uploaded_by']


class ClaimStatusHistorySerializer(serializers.ModelSerializer):
    """Serializer for claim status history"""
    changed_by_name = serializers.CharField(source='changed_by.username', read_only=True)
    
    class Meta:
        model = ClaimStatusHistory
        fields = ['id', 'previous_status', 'new_status', 'changed_by', 'changed_by_name', 'changed_at', 'notes']
        read_only_fields = ['id', 'changed_at', 'changed_by', 'changed_by_name']


class ClaimSerializer(serializers.ModelSerializer):
    """Serializer for claims"""
    
    patient_name = serializers.CharField(source='patient.username', read_only=True)
    patient_email = serializers.CharField(source='patient.email', read_only=True)
    provider_name = serializers.CharField(source='provider.username', read_only=True)
    documents = ClaimDocumentSerializer(many=True, read_only=True)
    status_history = ClaimStatusHistorySerializer(many=True, read_only=True)
    amount = serializers.SerializerMethodField()  # For backward compatibility
    
    def get_amount(self, obj):
        """Return amount_requested for backward compatibility"""
        return obj.amount_requested
    
    class Meta:
        model = Claim
        fields = [
            'id', 'claim_number', 'patient', 'patient_name', 'patient_email',
            'provider', 'provider_name', 'insurance_id', 'diagnosis_code', 'diagnosis_description',
            'procedure_code', 'procedure_description', 'amount_requested', 'amount_approved', 'amount',
            'status', 'priority', 'date_of_service', 'date_submitted', 'date_updated',
            'date_processed', 'notes', 'rejection_reason', 'provider_npi', 'provider_tax_id',
            'documents', 'status_history'
        ]
        read_only_fields = [
            'id', 'claim_number', 'date_submitted', 'date_updated', 'patient_name', 
            'patient_email', 'provider_name', 'documents', 'status_history'
        ]
    
    def validate_amount_requested(self, value):
        """Validate that amount_requested is positive"""
        if value <= 0:
            raise serializers.ValidationError("Amount requested must be greater than 0")
        return value
    
    def validate_date_of_service(self, value):
        """Validate that date_of_service is not in the future"""
        from datetime import date
        if value > date.today():
            raise serializers.ValidationError("Date of service cannot be in the future")
        return value


class ClaimCreateSerializer(serializers.ModelSerializer):
    """Serializer specifically for creating claims"""
    
    class Meta:
        model = Claim
        fields = [
            'patient', 'insurance_id', 'diagnosis_code', 'diagnosis_description',
            'procedure_code', 'procedure_description', 'amount_requested',
            'priority', 'date_of_service', 'notes', 'provider_npi', 'provider_tax_id'
        ]
    
    def validate_amount_requested(self, value):
        """Validate that amount_requested is positive"""
        if value <= 0:
            raise serializers.ValidationError("Amount requested must be greater than 0")
        return value
    
    def validate_date_of_service(self, value):
        """Validate that date_of_service is not in the future"""
        from datetime import date
        if value > date.today():
            raise serializers.ValidationError("Date of service cannot be in the future")
        return value