# Test Claim Submission - John Doe (BCBS Member)

## 📋 Overview

This document provides the complete claim submission test for **John Doe**, a BlueCross BlueShield (BCBS) member, to verify data flow between provider and payor systems.

## 👤 Member Information

```json
{
  "member_id": "MEM-BC-001",
  "insurance_id": "BC-789-456",
  "first_name": "John",
  "last_name": "Doe",
  "date_of_birth": "1985-06-15",
  "gender": "M",
  "policy_number": "BC-789-456-123",
  "plan_name": "BlueCross Gold Plan",
  "status": "active",
  "payor_id": "PAY001"
}
```

### Medical Conditions
- **Type 2 Diabetes** (ICD-10: E11.9) - Active, Moderate severity
- **Hypertension** (ICD-10: I10) - Active, Mild severity

### Allergies
- Penicillin (Reaction: Rash, Severity: Moderate)

### Financial Status
- Deductible Met: $1,200
- Out-of-Pocket Met: $2,500

## 🏥 Claim Details

### Claim Summary
- **Patient**: John Doe
- **Insurance ID**: BC-789-456
- **Service Date**: October 1, 2025
- **Total Amount**: $450.00
- **Primary Diagnosis**: E11.9 (Type 2 Diabetes)
- **Secondary Diagnosis**: I10 (Hypertension)

### Services Rendered

1. **Office Visit (CPT 99214)** - $250.00
   - Established patient, moderate complexity
   - Diabetes management consultation

2. **Hemoglobin A1C Test (CPT 83036)** - $100.00
   - Diabetes monitoring lab test

3. **Comprehensive Metabolic Panel (CPT 80053)** - $100.00
   - Blood chemistry test for diabetes/hypertension management

### Complete Claim Data

```json
{
  "patient_name": "John Doe",
  "insurance_id": "BC-789-456",
  "diagnosis_code": "E11.9",
  "diagnosis_description": "Type 2 diabetes mellitus without complications",
  "procedure_code": "99214",
  "procedure_description": "Office visit for diabetes management with lab work",
  "amount": 450.00,
  "date_of_service": "2025-10-01",
  "notes": "Routine diabetes follow-up. Secondary diagnosis: Hypertension (I10). Labs performed: HbA1c test (83036), Comprehensive metabolic panel (80053). Patient deductible met: $1200, OOP met: $2500"
}
```

## 🚀 How to Submit the Test Claim

### Prerequisites

**IMPORTANT**: You must restart the Django server to pick up the new ngrok URL from `.env`:

1. **Stop the server** (if running): Press `CTRL+C` in the terminal
2. **Restart the server**:
   ```bash
   cd c:\Users\sagar\integrationdemo\Provider
   python manage.py runserver 0.0.0.0:8001
   ```
3. **Wait for**: `Starting development server at http://0.0.0.0:8001/`

### Method 1: Using the Test Script (Recommended)

```bash
cd c:\Users\sagar\integrationdemo\Provider
python submit_test_claim_john_doe.py
```

This script will:
- Display the complete claim data
- Submit the claim to the provider API
- Show the submission response
- Verify the claim in the payor system
- Provide detailed success/error messages

### Method 2: Using curl

```bash
curl -X POST http://127.0.0.1:8001/api/provider/submit-claim/ ^
  -H "Content-Type: application/json" ^
  -d "{\"patient_name\":\"John Doe\",\"insurance_id\":\"BC-789-456\",\"diagnosis_code\":\"E11.9\",\"diagnosis_description\":\"Type 2 diabetes mellitus without complications\",\"procedure_code\":\"99214\",\"procedure_description\":\"Office visit for diabetes management with lab work\",\"amount\":450.00,\"date_of_service\":\"2025-10-01\",\"notes\":\"Routine diabetes follow-up with lab work\"}"
```

### Method 3: Using the Frontend Dashboard

1. Navigate to `http://localhost:8001`
2. Login to provider dashboard
3. Click "Create New Claim"
4. Fill in the form:
   - Patient Name: `John Doe`
   - Insurance ID: `BC-789-456`
   - Diagnosis Code: `E11.9`
   - Diagnosis Description: `Type 2 diabetes mellitus without complications`
   - Procedure Code: `99214`
   - Procedure Description: `Office visit for diabetes management with lab work`
   - Amount: `450.00`
   - Date of Service: `2025-10-01`
   - Notes: `Routine diabetes follow-up with lab work`
5. Click "Submit Claim"

## ✅ Expected Results

### Successful Submission (Status 201)

```json
{
  "success": true,
  "message": "Claim submitted successfully to payor",
  "claim_id": "67030abc1234567890abcdef",
  "payor_claim_id": "CLM-PAY001-20251003-123456",
  "status": "submitted",
  "payor_response": {
    "claim_id": "CLM-PAY001-20251003-123456",
    "status": "submitted",
    "message": "Claim received and queued for processing"
  }
}
```

### What Happens

1. ✅ **Claim validated** by provider system
2. ✅ **Saved locally** in provider MongoDB
3. ✅ **Submitted to payor** via ngrok tunnel
4. ✅ **Saved in payor system** MongoDB
5. ✅ **Member verification** - Insurance ID matched to member
6. ✅ **Policy verification** - Active policy confirmed
7. ✅ **Auto-processing** - Claim queued for approval/review

## 🔍 Verification Steps

### Step 1: Check Provider System

```bash
# View the claim in provider's local database
python -c "from claims.mongo_models import Claim; import mongoengine; mongoengine.connect('provider_db'); claim = Claim.objects.filter(insurance_id='BC-789-456').first(); print(f'Provider Claim: {claim.id}', f'Status: {claim.status}')"
```

### Step 2: Check Payor System Status

```bash
# Query the payor system for claim status
curl http://127.0.0.1:8001/api/provider/claim-status/<PAYOR_CLAIM_ID>/
```

Replace `<PAYOR_CLAIM_ID>` with the ID from the submission response.

### Step 3: Check Payor Dashboard

1. Navigate to payor system: `http://localhost:8000` (if payor server running)
2. Login to payor dashboard
3. View claims list
4. Search for Insurance ID: `BC-789-456`
5. Verify claim appears with correct data

## 🔧 Troubleshooting

### Issue: Connection Error

```
ERROR: Connection error: Expecting value: line 1 column 1 (char 0)
```

**Solution**: 
- Django server not restarted after `.env` update
- Restart server: `python manage.py runserver 0.0.0.0:8001`

### Issue: 400 Validation Error

**Solution**: 
- Check all required fields are present
- Verify field names match exactly (snake_case)
- Ensure `amount` is a number, not string

### Issue: Member Not Found

**Solution**: 
- Verify member exists in payor system
- Check insurance_id matches exactly: `BC-789-456`
- Ensure payor database has the member data

### Issue: Ngrok URL Not Working

**Solution**:
1. Check ngrok is running: `ngrok http 8000`
2. Update `.env` with new ngrok URL
3. Restart Django server
4. Test connection: `curl -X POST http://127.0.0.1:8001/api/provider/test-connection/`

## 📊 Data Flow Diagram

```
Provider System (Port 8001)
     │
     │ 1. Receive claim submission
     ▼
Validate claim data
     │
     │ 2. Save to local MongoDB
     ▼
Submit to Payor API
     │
     │ 3. Send via ngrok tunnel
     ▼
Payor System (Port 8000)
     │
     │ 4. Validate & verify member
     ▼
Save to payor MongoDB
     │
     │ 5. Process claim (auto-approve/review)
     ▼
Return response to provider
     │
     │ 6. Update local claim status
     ▼
Confirmation to user
```

## 🎯 Success Criteria

- [x] Claim data correctly formatted
- [x] All required fields present
- [ ] Connection to payor system successful
- [ ] Claim saved in provider MongoDB
- [ ] Claim saved in payor MongoDB
- [ ] Member verified against insurance ID
- [ ] Policy verified as active
- [ ] Claim status returned to provider

## 📝 Notes

- The member's deductible ($1,200) and OOP max ($2,500) are already met
- Patient has pre-existing conditions documented in the system
- Allergies (Penicillin) are on file - avoid prescribing
- This is a routine follow-up, not an emergency claim
- Lab tests support the diagnosis codes used

## 🔐 Security Notes

- All PII data transmitted via HTTPS (ngrok tunnel)
- Member data encrypted at rest in MongoDB
- Authentication required for both systems
- HIPAA compliance maintained throughout

## 📞 Support

If you encounter issues:
1. Check all services are running (Django, MongoDB, ngrok)
2. Verify `.env` configuration is correct
3. Review server logs for error details
4. Test connection endpoint first before submitting claims
