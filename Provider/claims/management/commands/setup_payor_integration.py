"""
Django management command to setup payor integration
"""

from django.core.management.base import BaseCommand
from django.conf import settings
from django.utils import timezone
import json
import os


class Command(BaseCommand):
    help = 'Setup payor integration configuration'

    def add_arguments(self, parser):
        parser.add_argument(
            '--payor-url',
            type=str,
            help='Payor system URL (ngrok URL)'
        )
        parser.add_argument(
            '--email',
            type=str,
            help='Payor admin email'
        )
        parser.add_argument(
            '--password',
            type=str,
            help='Payor admin password'
        )
        parser.add_argument(
            '--interactive',
            action='store_true',
            help='Interactive setup mode'
        )

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('🏥 Provider-Payor Integration Setup')
        )
        
        if options['interactive']:
            self.interactive_setup()
        else:
            self.setup_from_args(options)

    def interactive_setup(self):
        """Interactive setup mode"""
        self.stdout.write('\n📋 Please provide the following information:\n')
        
        payor_url = input('Enter Payor System URL (ngrok URL): ').strip()
        email = input('Enter Payor Admin Email: ').strip()
        password = input('Enter Payor Admin Password: ').strip()
        
        if not all([payor_url, email, password]):
            self.stdout.write(
                self.style.ERROR('❌ All fields are required!')
            )
            return
        
        self.setup_configuration(payor_url, email, password)

    def setup_from_args(self, options):
        """Setup from command line arguments"""
        payor_url = options.get('payor_url')
        email = options.get('email')
        password = options.get('password')
        
        if not all([payor_url, email, password]):
            self.stdout.write(
                self.style.ERROR('❌ --payor-url, --email, and --password are required!')
            )
            self.stdout.write('Use --interactive for interactive setup')
            return
        
        self.setup_configuration(payor_url, email, password)

    def setup_configuration(self, payor_url, email, password):
        """Setup the payor configuration"""
        try:
            # Import here to avoid circular imports
            from claims.payor_integration import payor_service
            
            self.stdout.write('🔧 Updating payor configuration...')
            
            # Update configuration
            payor_service.update_payor_configuration(payor_url, email, password)
            
            # Test connection
            self.stdout.write('🔍 Testing connection to payor system...')
            connection_test = payor_service.test_connection()
            
            if connection_test['success']:
                self.stdout.write(
                    self.style.SUCCESS(f'✅ {connection_test["message"]}')
                )
                
                # Get insurance policies
                self.stdout.write('📋 Fetching insurance policies...')
                policies = payor_service.get_insurance_policies()
                
                if policies:
                    self.stdout.write(
                        self.style.SUCCESS(f'✅ Found {len(policies)} insurance policies')
                    )
                    for policy in policies[:3]:  # Show first 3
                        self.stdout.write(f'   - {policy.get("policy_name", "Unknown")} ({policy.get("policy_number", "N/A")})')
                    if len(policies) > 3:
                        self.stdout.write(f'   ... and {len(policies) - 3} more')
                else:
                    self.stdout.write(
                        self.style.WARNING('⚠️ No insurance policies found in payor system')
                    )
                
                # Save configuration to file
                self.save_configuration_file(payor_url, email, password)
                
                self.stdout.write('\n🎉 Payor integration setup completed successfully!')
                self.stdout.write('\n📝 Next steps:')
                self.stdout.write('   1. Test claim submission with insurance ID "INS001"')
                self.stdout.write('   2. Check payor dashboard for submitted claims')
                self.stdout.write('   3. Use sync endpoints to update claim statuses')
                
            else:
                self.stdout.write(
                    self.style.ERROR(f'❌ Connection failed: {connection_test["message"]}')
                )
                self.stdout.write('Please check your payor URL and credentials')
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Setup failed: {str(e)}')
            )

    def save_configuration_file(self, payor_url, email, password):
        """Save configuration to a file"""
        config = {
            'payor_url': payor_url,
            'email': email,
            'password': password,
            'setup_date': str(timezone.now()),
            'insurance_mappings': {
                'INS001': 'BlueCross BlueShield',
                'INS002': 'Aetna Health',
                'INS003': 'United Healthcare',
                'HI12345': 'Health Insurance Premium'
            }
        }
        
        config_file = os.path.join(settings.BASE_DIR, 'payor_config.json')
        
        try:
            with open(config_file, 'w') as f:
                json.dump(config, f, indent=2)
            
            self.stdout.write(f'💾 Configuration saved to: {config_file}')
        except Exception as e:
            self.stdout.write(
                self.style.WARNING(f'⚠️ Could not save config file: {str(e)}')
            )