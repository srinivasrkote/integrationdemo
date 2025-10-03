# Provider-Payor API Quick Reference

## Base URL
```
http://127.0.0.1:8001/api/provider/
```

## Endpoints

### 1. Submit Claim
```bash
POST /api/provider/submit-claim/

Body:
{
  "patient_name": "John Doe",
  "insurance_id": "BC-789-456",
  "diagnosis_code": "J20.9",
  "procedure_code": "99213",
  "amount": "1250.00",
  "date_of_service": "2024-10-03"
}

Response (Success):
{
  "success": true,
  "claim_id": "CLM-20241003-ABC123",
  "status": "approved",
  "auto_approved": true
}
```

### 2. Get Claim Status
```bash
GET /api/provider/claim-status/{claim_id}/

Response:
{
  "success": true,
  "status": "approved",
  "approved_amount": 1000.00
}
```

### 3. Test Connection
```bash
POST /api/provider/test-connection/

Response:
{
  "success": true,
  "message": "Successfully connected to payor system"
}
```

### 4. Sync Claims
```bash
GET /api/provider/sync-claims/

Response:
{
  "success": true,
  "synced": 5,
  "updated": 2
}
```

### 5. Update Configuration
```bash
POST /api/provider/update-config/
Authorization: Required

Body:
{
  "payor_url": "https://new-url.ngrok.app/api",
  "provider_id": "PROV-001"
}
```

### 6. Webhook Receiver
```bash
POST /api/provider/webhook/payor-claims/
X-Webhook-Signature: sha256=...

Body: (from Payor system)
{
  "event_type": "claim_status_update",
  "claim_id": "CLM-123",
  "new_status": "approved"
}
```

## Test Command
```bash
python test_provider_payor_integration.py
```

## Configuration (.env)
```env
PAYOR_BASE_URL=https://9323de5960fc.ngrok-free.app/api
PROVIDER_ID=PROV-001
PROVIDER_NAME=City Medical Center
PAYOR_WEBHOOK_SECRET=your-secret
```
