# Quick Setup with New Ngrok URL

## ✅ Configuration Updated

The new payor ngrok URL has been added to `.env`:

```env
PAYOR_BASE_URL=https://e131ed05871e.ngrok-free.app/api
```

## 🔄 Restart Django Server

**IMPORTANT**: You must restart the Django server to pick up the new URL from `.env`

### Option 1: Restart in Current Terminal
1. Press `CTRL+C` in the terminal where Django is running
2. Restart the server:
   ```bash
   python manage.py runserver 0.0.0.0:8001
   ```

### Option 2: If Server is in Background
```bash
# Find the process
taskkill /F /IM python.exe

# Or restart manually
python manage.py runserver 0.0.0.0:8001
```

## ✅ Test the Connection

After restarting the server, test the connection:

```bash
curl -X POST http://127.0.0.1:8001/api/provider/test-connection/
```

Expected response:
```json
{
  "success": true,
  "message": "Successfully connected to payor system",
  "payor_url": "https://e131ed05871e.ngrok-free.app/api",
  "provider_id": "PROV-001"
}
```

## 🧪 Run Full Integration Tests

```bash
python test_provider_payor_integration.py
```

This will test:
- ✅ Connection to payor system
- ✅ Claim submission
- ✅ Claim status retrieval
- ✅ Webhook processing
- ✅ All endpoints

## 📝 Submit a Test Claim

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
    "priority": "medium"
  }'
```

## 🔄 Future Ngrok URL Changes

When the ngrok URL changes in the future:

### Method 1: Update .env (Recommended)
1. Edit `.env` file:
   ```env
   PAYOR_BASE_URL=https://new-url.ngrok-free.app/api
   ```
2. Restart Django server

### Method 2: Update via API (No Restart Needed)
```bash
curl -X POST http://127.0.0.1:8001/api/provider/update-config/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Basic <your-credentials>" \
  -d '{
    "payor_url": "https://new-url.ngrok-free.app/api"
  }'
```

## 📍 Current Configuration

```
Provider API:  http://127.0.0.1:8001/api
Payor API:     https://e131ed05871e.ngrok-free.app/api
Provider ID:   PROV-001
Frontend:      http://localhost:3001
```

## 🎯 Next Steps

1. ✅ **Configuration Updated** - .env file has new URL
2. ⏳ **Restart Server** - Run `python manage.py runserver 0.0.0.0:8001`
3. ⏳ **Test Connection** - Run test command above
4. ⏳ **Run Full Tests** - Execute `python test_provider_payor_integration.py`
5. ⏳ **Submit Test Claim** - Try the curl command above

---

**Status**: Configuration updated, waiting for server restart
**Ngrok URL**: https://e131ed05871e.ngrok-free.app/api
**Updated**: October 3, 2025
