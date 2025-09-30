"""
MongoEngine models for MongoDB Atlas integration
These models replace the Django ORM models for better MongoDB compatibility
"""

from mongoengine import Document, EmbeddedDocument, fields
from django.contrib.auth.models import AbstractUser
from datetime import datetime
import uuid


class User(Document):
    """MongoEngine User model for MongoDB"""
    
    ROLE_CHOICES = [
        ('patient', 'Patient'),
        ('provider', 'Provider'),
        ('payor', 'Payor'),
    ]
    
    # MongoDB ObjectId will be used as primary key
    username = fields.StringField(required=True, unique=True, max_length=150)
    email = fields.EmailField(required=True)
    first_name = fields.StringField(max_length=30)
    last_name = fields.StringField(max_length=30)
    password = fields.StringField(required=True)  # Will be hashed
    role = fields.StringField(choices=ROLE_CHOICES, default='patient')
    phone = fields.StringField(max_length=20)
    date_of_birth = fields.DateTimeField()
    insurance_id = fields.StringField(max_length=50)
    is_active = fields.BooleanField(default=True)
    is_staff = fields.BooleanField(default=False)
    is_superuser = fields.BooleanField(default=False)
    date_joined = fields.DateTimeField(default=datetime.now)
    last_login = fields.DateTimeField()
    
    meta = {
        'collection': 'users',
        'indexes': ['username', 'email', 'role']
    }
    
    def __str__(self):
        return f"{self.username} ({self.role})"


class Claim(Document):
    """MongoEngine Claim model for MongoDB"""
    
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
    claim_id = fields.UUIDField(default=uuid.uuid4, unique=True)
    claim_number = fields.StringField(max_length=20, unique=True)
    
    # References to users (using ObjectId references)
    patient_id = fields.ObjectIdField()
    provider_id = fields.ObjectIdField()
    
    # Patient and provider info (denormalized for better performance)
    patient_name = fields.StringField(max_length=100)
    patient_email = fields.EmailField()
    provider_name = fields.StringField(max_length=100)
    provider_email = fields.EmailField()
    
    # Insurance information
    insurance_id = fields.StringField(max_length=50, default='N/A')
    
    # Payor integration fields
    payor_claim_id = fields.StringField(max_length=100)  # ID in payor system
    payor_name = fields.StringField(max_length=100)      # Payor company name
    submitted_to_payor = fields.BooleanField(default=False)  # Whether submitted to payor
    payor_submission_date = fields.DateTimeField()      # When submitted to payor
    payor_response = fields.DictField()                  # Full payor response data
    
    # Claim details
    diagnosis_code = fields.StringField(max_length=20)
    diagnosis_description = fields.StringField(required=True)
    procedure_code = fields.StringField(max_length=20)
    procedure_description = fields.StringField()
    
    # Financial information
    amount_requested = fields.DecimalField(min_value=0.01, precision=2)
    amount_approved = fields.DecimalField(min_value=0, precision=2)
    
    # Status and priority
    status = fields.StringField(choices=STATUS_CHOICES, default='pending')
    priority = fields.StringField(choices=PRIORITY_CHOICES, default='medium')
    
    # Dates
    date_of_service = fields.DateTimeField()
    date_submitted = fields.DateTimeField(default=datetime.now)
    date_updated = fields.DateTimeField(default=datetime.now)
    date_processed = fields.DateTimeField()
    
    # Additional information
    notes = fields.StringField()
    rejection_reason = fields.StringField()
    
    # Provider information
    provider_npi = fields.StringField(max_length=10)
    provider_tax_id = fields.StringField(max_length=20)
    
    meta = {
        'collection': 'claims',
        'indexes': [
            'status', 'provider_id', 'patient_id', 'date_submitted', 
            'claim_number', 'priority'
        ],
        'ordering': ['-date_submitted']
    }
    
    def save(self, *args, **kwargs):
        if not self.claim_number:
            # Generate unique claim number with retry logic
            year = datetime.now().year
            max_attempts = 10
            
            for attempt in range(max_attempts):
                # Get the highest claim number for this year
                last_claims = Claim.objects(
                    claim_number__startswith=f'CLM-{year}-'
                ).order_by('-claim_number').limit(1)
                
                if last_claims:
                    last_num = int(last_claims[0].claim_number.split('-')[-1])
                    new_num = last_num + 1
                else:
                    new_num = 1
                
                self.claim_number = f'CLM-{year}-{new_num:03d}'
                
                # Check if this claim number already exists
                existing = Claim.objects(claim_number=self.claim_number).first()
                if not existing:
                    break  # Found unique number
                    
                # If we reach here, the number exists, try next one
                if attempt == max_attempts - 1:
                    # Last attempt, add timestamp to make it unique
                    import time
                    timestamp = int(time.time() % 10000)
                    self.claim_number = f'CLM-{year}-{new_num:03d}-{timestamp}'
        
        self.date_updated = datetime.now()
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.claim_number} - {self.patient_name} - {self.diagnosis_description[:50]}"


class ClaimDocument(Document):
    """MongoEngine model for claim documents"""
    
    DOCUMENT_TYPES = [
        ('medical_record', 'Medical Record'),
        ('lab_report', 'Lab Report'),
        ('invoice', 'Invoice'),
        ('prescription', 'Prescription'),
        ('receipt', 'Receipt'),
        ('referral', 'Referral'),
        ('other', 'Other'),
    ]
    
    claim_id = fields.ObjectIdField(required=True)
    document_type = fields.StringField(choices=DOCUMENT_TYPES, required=True)
    filename = fields.StringField(max_length=255, required=True)
    file_path = fields.StringField()  # Path to file storage
    file_size = fields.IntField()
    uploaded_at = fields.DateTimeField(default=datetime.now)
    uploaded_by_id = fields.ObjectIdField(required=True)
    uploaded_by_name = fields.StringField(max_length=100)
    
    meta = {
        'collection': 'claim_documents',
        'indexes': ['claim_id', 'document_type', 'uploaded_at']
    }
    
    def __str__(self):
        return f"{self.filename} - {self.document_type}"


class ClaimStatusHistory(Document):
    """MongoEngine model for claim status history"""
    
    claim_id = fields.ObjectIdField(required=True)
    previous_status = fields.StringField(choices=Claim.STATUS_CHOICES)
    new_status = fields.StringField(choices=Claim.STATUS_CHOICES, required=True)
    changed_by_id = fields.ObjectIdField(required=True)
    changed_by_name = fields.StringField(max_length=100)
    changed_at = fields.DateTimeField(default=datetime.now)
    notes = fields.StringField()
    
    meta = {
        'collection': 'claim_status_history',
        'indexes': ['claim_id', 'changed_at'],
        'ordering': ['-changed_at']
    }
    
    def __str__(self):
        return f"Status change: {self.previous_status} → {self.new_status}"