"""
Management command to create sample data in MongoDB Atlas
"""

from django.core.management.base import BaseCommand
from datetime import datetime, timedelta
from decimal import Decimal
import uuid
from claims.mongo_models import User, Claim, ClaimStatusHistory


class Command(BaseCommand):
    help = 'Create sample data in MongoDB Atlas'
    
    def handle(self, *args, **options):
        self.stdout.write('Creating sample data in MongoDB...')
        
        try:
            # Create sample users
            self.create_sample_users()
            self.create_sample_claims()
            
            self.stdout.write(
                self.style.SUCCESS('✅ Sample data created successfully in MongoDB!')
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Error creating sample data: {str(e)}')
            )
    
    def create_sample_users(self):
        """Create sample users"""
        users_data = [
            {
                'username': 'provider1',
                'email': 'provider@example.com',
                'first_name': 'Dr. John',
                'last_name': 'Smith',
                'password': 'password123',  # In production, this should be hashed
                'role': 'provider',
                'phone': '(555) 123-4567',
                'is_active': True,
                'is_staff': True,
            },
            {
                'username': 'patient1',
                'email': 'patient1@example.com',
                'first_name': 'Jane',
                'last_name': 'Doe',
                'password': 'password123',
                'role': 'patient',
                'phone': '(555) 987-6543',
                'insurance_id': 'BC-789-456-123',
                'date_of_birth': datetime(1990, 5, 15),
                'is_active': True,
            },
            {
                'username': 'patient2',
                'email': 'patient2@example.com',
                'first_name': 'Michael',
                'last_name': 'Johnson',
                'password': 'password123',
                'role': 'patient',
                'phone': '(555) 456-7890',
                'insurance_id': 'BC-123-789-456',
                'date_of_birth': datetime(1985, 8, 22),
                'is_active': True,
            },
            {
                'username': 'payor1',
                'email': 'payor@example.com',
                'first_name': 'Insurance',
                'last_name': 'Manager',
                'password': 'password123',
                'role': 'payor',
                'phone': '(555) 555-0123',
                'is_active': True,
                'is_staff': True,
            }
        ]
        
        created_users = {}
        for user_data in users_data:
            # Check if user already exists
            existing_user = User.objects(username=user_data['username']).first()
            if existing_user:
                self.stdout.write(f'User {user_data["username"]} already exists')
                created_users[user_data['username']] = existing_user
                continue
            
            user = User(**user_data)
            user.save()
            created_users[user_data['username']] = user
            self.stdout.write(f'Created user: {user.username} ({user.role})')
        
        self.created_users = created_users
    
    def create_sample_claims(self):
        """Create sample claims"""
        if not hasattr(self, 'created_users'):
            self.stdout.write('No users found to create claims for')
            return
        
        provider = self.created_users.get('provider1')
        patient1 = self.created_users.get('patient1')
        patient2 = self.created_users.get('patient2')
        
        if not all([provider, patient1, patient2]):
            self.stdout.write('Required users not found')
            return
        
        claims_data = [
            {
                'patient': patient1,
                'provider': provider,
                'diagnosis_code': 'M25.512',
                'diagnosis_description': 'Pain in left shoulder',
                'procedure_code': '20610',
                'procedure_description': 'Arthrocentesis (joint fluid removal), major joint',
                'amount_requested': Decimal('350.00'),
                'status': 'pending',
                'priority': 'medium',
                'date_of_service': datetime.now() - timedelta(days=5),
                'notes': 'Patient experiencing chronic shoulder pain, arthrocentesis performed to rule out infection.',
                'provider_npi': '1234567890',
                'provider_tax_id': '12-3456789',
            },
            {
                'patient': patient1,
                'provider': provider,
                'diagnosis_code': 'Z00.00',
                'diagnosis_description': 'Encounter for general adult medical examination without abnormal findings',
                'procedure_code': '99395',
                'procedure_description': 'Periodic comprehensive preventive medicine reevaluation',
                'amount_requested': Decimal('225.00'),
                'amount_approved': Decimal('200.00'),
                'status': 'approved',
                'priority': 'low',
                'date_of_service': datetime.now() - timedelta(days=15),
                'date_processed': datetime.now() - timedelta(days=2),
                'notes': 'Annual wellness exam completed successfully.',
                'provider_npi': '1234567890',
                'provider_tax_id': '12-3456789',
            },
            {
                'patient': patient2,
                'provider': provider,
                'diagnosis_code': 'J06.9',
                'diagnosis_description': 'Acute upper respiratory infection, unspecified',
                'procedure_code': '99213',
                'procedure_description': 'Office or other outpatient visit for evaluation and management',
                'amount_requested': Decimal('150.00'),
                'status': 'under_review',
                'priority': 'high',
                'date_of_service': datetime.now() - timedelta(days=3),
                'notes': 'Upper respiratory infection, prescribed antibiotics.',
                'provider_npi': '1234567890',
                'provider_tax_id': '12-3456789',
            },
            {
                'patient': patient2,
                'provider': provider,
                'diagnosis_code': 'M79.3',
                'diagnosis_description': 'Panniculitis, unspecified',
                'procedure_code': '11042',
                'procedure_description': 'Debridement, subcutaneous tissue',
                'amount_requested': Decimal('450.00'),
                'status': 'rejected',
                'priority': 'medium',
                'date_of_service': datetime.now() - timedelta(days=20),
                'date_processed': datetime.now() - timedelta(days=5),
                'rejection_reason': 'Procedure not covered under current insurance plan. Alternative treatment options available.',
                'notes': 'Panniculitis treatment, debridement performed.',
                'provider_npi': '1234567890',
                'provider_tax_id': '12-3456789',
            },
            {
                'patient': patient1,
                'provider': provider,
                'diagnosis_code': 'E11.9',
                'diagnosis_description': 'Type 2 diabetes mellitus without complications',
                'procedure_code': '82947',
                'procedure_description': 'Glucose; quantitative, blood',
                'amount_requested': Decimal('85.00'),
                'amount_approved': Decimal('75.00'),
                'status': 'approved',
                'priority': 'medium',
                'date_of_service': datetime.now() - timedelta(days=10),
                'date_processed': datetime.now() - timedelta(days=1),
                'notes': 'Routine diabetes monitoring blood glucose test.',
                'provider_npi': '1234567890',
                'provider_tax_id': '12-3456789',
            }
        ]
        
        for claim_data in claims_data:
            patient = claim_data.pop('patient')
            provider = claim_data.pop('provider')
            
            claim = Claim(
                patient_id=patient.id,
                provider_id=provider.id,
                patient_name=f"{patient.first_name} {patient.last_name}",
                patient_email=patient.email,
                provider_name=f"{provider.first_name} {provider.last_name}",
                provider_email=provider.email,
                **claim_data
            )
            
            claim.save()
            self.stdout.write(f'Created claim: {claim.claim_number} - {claim.diagnosis_description[:30]}...')
            
            # Create status history for processed claims
            if claim.status in ['approved', 'rejected']:
                status_history = ClaimStatusHistory(
                    claim_id=claim.id,
                    previous_status='pending',
                    new_status=claim.status,
                    changed_by_id=provider.id,
                    changed_by_name=f"{provider.first_name} {provider.last_name}",
                    notes=f'Claim {claim.status} after review'
                )
                status_history.save()
        
        self.stdout.write(f'Created {len(claims_data)} sample claims')