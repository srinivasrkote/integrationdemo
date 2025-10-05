# PAYOR SYSTEM CONFIGURATION FOR WEBHOOK INTEGRATION

# Add this to your payor system's settings.py file

# Provider Webhook Configuration
PROVIDER_WEBHOOK_CONFIG = {
    # Provider system URL - UPDATE THIS BASED ON YOUR SETUP
    'BASE_URL': 'http://127.0.0.1:8000',  # For local development
    # 'BASE_URL': 'https://your-ngrok-url.ngrok-free.app',  # For ngrok/external access
    
    # Webhook endpoints on provider system
    'ENDPOINTS': {
        'claim_approved': '/api/webhooks/payor/claim-approved/',
        'claim_denied': '/api/webhooks/payor/claim-denied/', 
        'claim_under_review': '/api/webhooks/payor/claim-under-review/',
        'health': '/api/webhooks/health/',
        'test': '/api/webhooks/test/'
    },
    
    # Connection settings
    'TIMEOUT': 30,
    'RETRY_ATTEMPTS': 3,
    'RETRY_DELAY': 5
}

# Logging configuration for webhook debugging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'webhook_file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': 'webhook.log',
            'formatter': 'verbose',
        },
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
    },
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'loggers': {
        'webhook_service': {
            'handlers': ['webhook_file', 'console'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}

# Alternative: Environment Variable Configuration
# You can also set these as environment variables:

# PROVIDER_WEBHOOK_URL=http://127.0.0.1:8000
# PROVIDER_WEBHOOK_TIMEOUT=30
# PROVIDER_WEBHOOK_RETRY_ATTEMPTS=3