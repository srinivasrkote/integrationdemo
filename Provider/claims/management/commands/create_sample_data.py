from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from claims.models import Claim
from decimal import Decimal
from datetime import date, timedelta
import pymongo
from django.conf import settings

User = get_user_model()

class Command(BaseCommand):
    help = 'Create sample data for testing'
    
    def handle(self, *args, **options):
        self.stdout.write('Creating sample data...')
        
        # Create users
        provider_user, created = User.objects.get_or_create(
            username='provider1',
            defaults={
                'email': 'provider@example.com',
                'role': 'provider',
                'first_name': 'Dr. John',
                'last_name': 'Smith',
                'phone': '(555) 123-4567',
            }
        )
        
        patient_user, created = User.objects.get_or_create(
            username='patient1',
            defaults={
                'email': 'patient@example.com',
                'role': 'patient',
                'first_name': 'Jane',
                'last_name': 'Doe',
                'phone': '(555) 987-6543',
                'insurance_id': 'BC-789-456-123',
                'date_of_birth': date(1990, 5, 15),
            }
        )
        
        payor_user, created = User.objects.get_or_create(
            username='payor1',
            defaults={
                'email': 'payor@example.com',
                'role': 'payor',
                'first_name': 'Insurance',
                'last_name': 'Manager',
                'phone': '(555) 555-0123',
            }
        )
        
        # Set passwords
        for user in [provider_user, patient_user, payor_user]:
            user.set_password('password123')
            user.save()
        
        # Create sample claims
        claims_data = [
            {
                'patient': patient_user,
                'provider': provider_user,
                'diagnosis_code': 'J20.9',
                'diagnosis_description': 'Acute Bronchitis, unspecified',
                'procedure_code': '99213',
                'procedure_description': 'Office visit, established patient, level 3',
                'amount_requested': Decimal('1250.00'),
                'status': 'approved',
                'priority': 'medium',
                'date_of_service': date.today() - timedelta(days=7),
                'amount_approved': Decimal('1125.00'),
                'provider_npi': '1234567890',
                'notes': 'Routine treatment for acute bronchitis'
            },
            {
                'patient': patient_user,
                'provider': provider_user,
                'diagnosis_code': 'Z00.00',
                'diagnosis_description': 'Encounter for general adult medical examination without abnormal findings',
                'procedure_code': '99396',
                'procedure_description': 'Periodic comprehensive preventive medicine evaluation',
                'amount_requested': Decimal('350.00'),
                'status': 'pending',
                'priority': 'low',
                'date_of_service': date.today() - timedelta(days=3),
                'provider_npi': '1234567890',
                'notes': 'Annual physical examination'
            },
            {
                'patient': patient_user,
                'provider': provider_user,
                'diagnosis_code': 'I25.10',
                'diagnosis_description': 'Atherosclerotic heart disease of native coronary artery without angina pectoris',
                'procedure_code': '93010',
                'procedure_description': 'Electrocardiogram, routine ECG with at least 12 leads',
                'amount_requested': Decimal('800.00'),
                'status': 'under_review',
                'priority': 'high',
                'date_of_service': date.today() - timedelta(days=1),
                'provider_npi': '1234567890',
                'notes': 'Cardiac evaluation following chest pain complaint'
            }
        ]
        
        for claim_data in claims_data:
            claim, created = Claim.objects.get_or_create(
                patient=claim_data['patient'],
                provider=claim_data['provider'],
                diagnosis_code=claim_data['diagnosis_code'],
                date_of_service=claim_data['date_of_service'],
                defaults=claim_data
            )
            if created:
                self.stdout.write(f'Created claim: {claim.claim_number}')
        
        self.stdout.write(self.style.SUCCESS('Sample data created successfully!'))
        self.stdout.write(f'Provider user: {provider_user.username} (password: password123)')
        self.stdout.write(f'Patient user: {patient_user.username} (password: password123)')
        self.stdout.write(f'Payor user: {payor_user.username} (password: password123)')