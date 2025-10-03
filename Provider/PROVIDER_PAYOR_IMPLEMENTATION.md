# Provider-Payor Integration Implementation

## Overview
This implementation provides full integration between the Provider system and Payor system as specified in `PROVIDER_INTEGRATION_GUIDE.md`.

## Architecture

```
Provider System (Django) <--> Provider-Payor API Client <--> Payor System (ngrok URL)
          ↓
    MongoDB Storage
```

## Implemented Features

### 1. Claim Submission
- **Endpoint**: `POST /api/provider/submit-claim/`
- **Features**:
  - Full claim validation before submission
  - Automatic retry logic with exponential backoff
  - Real-time response from payor system
  - Support for auto-approval
  - MongoDB storage for local tracking

### 2. Claim Status Retrieval
- **Endpoint**: `GET /api/provider/claim-status/<claim_id>/`
- **Features**:
  - Real-time status from payor system
  - Automatic local database sync
  - Payment details retrieval

### 3. Webhook Integration
- **Endpoint**: `POST /api/provider/webhook/payor-claims/`
- **Features**:
  - Receive real-time updates from payor
  - HMAC signature verification for security
  - Automatic claim status updates
  - Event processing and logging

### 4. Bulk Synchronization
- **Endpoint**: `GET /api/provider/sync-claims/`
- **Features**:
  - Sync all pending claims with payor system
  - Batch status updates
  - Error handling for failed syncs

### 5. Configuration Management
- **Endpoint**: `POST /api/provider/update-config/`
- **Features**:
  - Dynamic payor URL configuration (for ngrok URLs)
  - API key management
  - Connection testing after update

### 6. Connection Testing
- **Endpoint**: `POST /api/provider/test-connection/`
- **Features**:
  - Health check to payor system
  - Configuration validation

## API Usage Examples

### Submit a Claim

```bash
curl -X POST http://127.0.0.1:8001/api/provider/submit-claim/ \
  -H "Content-Type: application/json" \
  -d '{
    "patient_name": "John Doe",
    "insurance_id": "BC-789-456",
    "diagnosis_code": "J20.9",
    "diagnosis_description": "Acute Bronchitis",
    "procedure_code": "99213",
    "procedure_description": "Office consultation",
    "amount": "1250.00",
    "date_of_service": "2024-10-03",
    "priority": "medium",
    "notes": "Patient presenting with persistent cough"
  }'
```

**Response (Auto-Approved)**:
```json
{
  "success": true,
  "message": "Claim submitted successfully to Payor system",
  "claim_id": "CLM-20241003-ABC123",
  "status": "approved",
  "auto_approved": true,
  "coverage_validated": true,
  "coverage_message": "Coverage validated successfully",
  "payment_details": {
    "approved_amount": 1000.00,
    "patient_responsibility": 250.00,
    "expected_payment_date": "2024-10-10"
  }
}
```

### Get Claim Status

```bash
curl http://127.0.0.1:8001/api/provider/claim-status/CLM-20241003-ABC123/
```

**Response**:
```json
{
  "success": true,
  "claim_id": "CLM-20241003-ABC123",
  "status": "approved",
  "patient_name": "John Doe",
  "amount": 1250.00,
  "approved_amount": 1000.00,
  "patient_responsibility": 250.00,
  "processed_date": "2024-10-03T10:30:01Z"
}
```

### Test Connection

```bash
curl -X POST http://127.0.0.1:8001/api/provider/test-connection/
```

### Sync All Claims

```bash
curl http://127.0.0.1:8001/api/provider/sync-claims/
```

### Update Configuration

```bash
curl -X POST http://127.0.0.1:8001/api/provider/update-config/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Basic <your-auth-token>" \
  -d '{
    "payor_url": "https://new-ngrok-url.ngrok.app/api",
    "provider_id": "PROV-001",
    "webhook_secret": "your-webhook-secret"
  }'
```

## Webhook Setup

### 1. Register Webhook URL
Contact payor support to register your webhook endpoint:
```
Webhook URL: https://your-domain.com/api/provider/webhook/payor-claims/
```

### 2. Webhook Payload Example
```json
{
  "event_type": "claim_status_update",
  "timestamp": "2024-10-03T15:30:00Z",
  "claim_id": "CLM-20241003-ABC123",
  "previous_status": "under_review",
  "new_status": "approved",
  "message": "Claim approved after validation",
  "patient_name": "John Doe",
  "insurance_id": "BC-789-456",
  "amount": 1250.00,
  "payment_details": {
    "approved_amount": 1000.00,
    "patient_responsibility": 250.00
  },
  "webhook_signature": "sha256=abc123..."
}
```

## Configuration

### Environment Variables (.env)
```env
# Payor Integration
PAYOR_BASE_URL=https://9323de5960fc.ngrok-free.app/api
PAYOR_API_KEY=optional-api-key
PROVIDER_ID=PROV-001
PROVIDER_NAME=City Medical Center
PAYOR_WEBHOOK_SECRET=your-webhook-secret-change-in-production
```

### Django Settings (provider/settings.py)
Already configured with defaults:
```python
PAYOR_BASE_URL = config('PAYOR_BASE_URL', default='https://9323de5960fc.ngrok-free.app/api')
PAYOR_API_KEY = config('PAYOR_API_KEY', default=None)
PROVIDER_ID = config('PROVIDER_ID', default='PROV-001')
PROVIDER_NAME = config('PROVIDER_NAME', default='City Medical Center')
PAYOR_WEBHOOK_SECRET = config('PAYOR_WEBHOOK_SECRET', default='default-webhook-secret-change-in-production')
```

## Testing

### Run Integration Tests
```bash
cd C:\Users\sagar\integrationdemo\Provider
python test_provider_payor_integration.py
```

This will test:
- ✓ Connection to payor system
- ✓ Claim submission (valid cases)
- ✓ Claim submission (invalid insurance)
- ✓ Claim submission (missing fields)
- ✓ Claim status retrieval
- ✓ Bulk claim synchronization
- ✓ Configuration updates
- ✓ Webhook payload processing

## Code Structure

```
Provider/
├── claims/
│   ├── provider_payor_api.py         # API client for payor integration
│   ├── provider_payor_views.py       # Django views/endpoints
│   ├── urls.py                        # URL routing
│   └── mongo_models.py                # MongoDB models for storage
├── provider/
│   └── settings.py                    # Configuration settings
└── test_provider_payor_integration.py # Integration tests
```

## Key Classes

### ProviderPayorAPI (`provider_payor_api.py`)
Main API client class with methods:
- `submit_claim(claim_data)` - Submit claim to payor
- `get_claim_status(payor_claim_id)` - Get claim status
- `verify_webhook_signature(payload, signature)` - Verify webhook security
- `process_webhook_notification(webhook_data)` - Process webhook events
- `validate_claim_data(claim_data)` - Validate before submission
- `submit_claim_with_retry(claim_data, max_retries)` - Submit with retry logic
- `test_connection()` - Test payor system connection

## Error Handling

The implementation includes comprehensive error handling:

1. **Validation Errors** - Caught before submission
2. **Network Errors** - Automatic retry with exponential backoff
3. **Client Errors (4xx)** - No retry, immediate response
4. **Server Errors (5xx)** - Retry up to 3 times
5. **Timeout Handling** - 30-second timeout on all requests

## Security

- **Webhook Signature Verification** - HMAC SHA-256 signatures
- **HTTPS Required** - For production webhooks
- **API Key Support** - Optional authentication
- **CSRF Protection** - Exempted for webhook endpoint

## Monitoring & Logging

All operations are logged with different levels:
- `INFO` - Successful operations
- `WARNING` - Validation failures, connection issues
- `ERROR` - Critical errors, exceptions

View logs in Django console or configure file logging.

## Next Steps

1. **Update ngrok URL** when it changes:
   ```bash
   curl -X POST http://127.0.0.1:8001/api/provider/update-config/ \
     -d '{"payor_url": "https://new-url.ngrok.app/api"}'
   ```

2. **Register webhook URL** with payor support

3. **Set up monitoring** for webhook delivery and claim status

4. **Configure notifications** for approved/rejected claims

5. **Add frontend integration** to submit claims from UI

## Support

For integration support:
- Review `PROVIDER_INTEGRATION_GUIDE.md` for full specifications
- Check Django logs for detailed error messages
- Run test script to verify configuration
- Contact payor support for webhook registration

---

**Implementation Status**: ✅ Complete and ready for testing
**Last Updated**: October 3, 2025
