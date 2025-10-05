from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator
import uuid

class Claim(models.Model):
    """Model for insurance claims"""
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('under_review', 'Under Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('processing', 'Processing'),
        ('requires_review', 'Requires Review'),
    ]
    
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]
    
    # Primary identifiers
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    claim_number = models.CharField(max_length=20, unique=True, blank=True)
    
    # Relationships
    patient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='patient_claims',
        limit_choices_to={'role': 'patient'},
        null=True,
        blank=True
    )
    provider = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='provider_claims',
        limit_choices_to={'role': 'provider'},
        null=True,
        blank=True
    )
    
    # Insurance information
    insurance_id = models.CharField(max_length=50, help_text='Insurance ID or policy number', default='N/A')
    
    # Claim details
    diagnosis_code = models.CharField(max_length=20, help_text='ICD-10 diagnosis code', blank=True, null=True)
    diagnosis_description = models.TextField()
    procedure_code = models.CharField(max_length=20, blank=True, null=True, help_text='CPT procedure code')
    procedure_description = models.TextField(blank=True, null=True)
    
    # Financial information
    amount_requested = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0.01)]
    )
    amount_approved = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0)]
    )
    
    # Status and priority
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    
    # Dates
    date_of_service = models.DateField(null=True, blank=True)
    date_submitted = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)
    date_processed = models.DateTimeField(null=True, blank=True)
    
    # Additional information
    notes = models.TextField(blank=True, null=True)
    rejection_reason = models.TextField(blank=True, null=True)
    
    # Provider information
    provider_npi = models.CharField(max_length=10, blank=True, null=True, help_text='National Provider Identifier')
    provider_tax_id = models.CharField(max_length=20, blank=True, null=True)
    
    class Meta:
        ordering = ['-date_submitted']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['provider']),
            models.Index(fields=['patient']),
            models.Index(fields=['date_submitted']),
        ]
    
    def save(self, *args, **kwargs):
        if not self.claim_number:
            # Generate claim number like CLM-2024-001
            from datetime import datetime
            year = datetime.now().year
            last_claim = Claim.objects.filter(
                claim_number__startswith=f'CLM-{year}-'
            ).order_by('claim_number').last()
            
            if last_claim:
                last_num = int(last_claim.claim_number.split('-')[-1])
                new_num = last_num + 1
            else:
                new_num = 1
            
            self.claim_number = f'CLM-{year}-{new_num:03d}'
        
        super().save(*args, **kwargs)
    
    def __str__(self):
        patient_name = self.patient.username if self.patient else "Unknown"
        return f"{self.claim_number} - {patient_name} - {self.diagnosis_description[:50]}"


class ClaimDocument(models.Model):
    """Model for claim supporting documents"""
    
    DOCUMENT_TYPES = [
        ('medical_record', 'Medical Record'),
        ('lab_report', 'Lab Report'),
        ('invoice', 'Invoice'),
        ('prescription', 'Prescription'),
        ('receipt', 'Receipt'),
        ('referral', 'Referral'),
        ('other', 'Other'),
    ]
    
    claim = models.ForeignKey(Claim, on_delete=models.CASCADE, related_name='documents')
    document_type = models.CharField(max_length=20, choices=DOCUMENT_TYPES)
    file = models.FileField(upload_to='claim_documents/')
    filename = models.CharField(max_length=255)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    
    def __str__(self):
        return f"{self.claim.claim_number} - {self.filename}"


class ClaimStatusHistory(models.Model):
    """Model to track claim status changes"""
    
    claim = models.ForeignKey(Claim, on_delete=models.CASCADE, related_name='status_history')
    previous_status = models.CharField(max_length=20, choices=Claim.STATUS_CHOICES, null=True, blank=True)
    new_status = models.CharField(max_length=20, choices=Claim.STATUS_CHOICES)
    changed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    changed_at = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True, null=True)
    
    class Meta:
        ordering = ['-changed_at']
        verbose_name_plural = 'Claim status histories'
    
    def __str__(self):
        return f"{self.claim.claim_number} - {self.previous_status} → {self.new_status}"
