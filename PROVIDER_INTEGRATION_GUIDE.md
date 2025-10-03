# 🏥 Provider Integration Guide for HCMS Payor Claims API

## Overview
This guide helps provider-side developers integrate with the HCMS Payor Backend to submit insurance claims and receive real-time processing responses. The system supports automatic claim validation, medical code checking, and instant approval/rejection notifications.

## 🚀 **Quick Start Integration**

### **Base URL**
```
Production: and 
Development:  https://9323de5960fc.ngrok-free.app/api
```

### **Authentication**
The API supports multiple authentication methods:

**Option 1: No Authentication (for claim submission)**
```javascript
// Claims submission endpoint is open for provider integration
const response = await fetch('/api/claims/', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json'
  },
  body: JSON.stringify(claimData)
});
```

**Option 2: API Key Authentication (recommended for production)**
```javascript
const response = await fetch('/api/claims/', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'X-API-Key': 'your-provider-api-key',
    'X-Provider-ID': 'PROV-001'
  },
  body: JSON.stringify(claimData)
});
```

## 📤 **Sending Claims to Payor**

### **Endpoint: POST /api/claims/**

### **Required Claim Data Structure**
```javascript
const claimData = {
  // REQUIRED FIELDS
  "patient_name": "John Doe",                    // Full patient name
  "insurance_id": "BC-789-456",                  // Patient's insurance ID (primary identifier)
  "diagnosis_code": "J20.9",                     // ICD-10 diagnosis code
  "amount": "1250.00",                           // Treatment cost (string or number)
  
  // RECOMMENDED FIELDS
  "procedure_code": "99213",                     // CPT procedure code
  "diagnosis_description": "Acute Bronchitis",   // Human-readable diagnosis
  "procedure_description": "Office consultation", // Human-readable procedure
  "date_of_service": "2024-10-03",              // YYYY-MM-DD format
  "priority": "medium",                          // low, medium, high, urgent
  
  // OPTIONAL FIELDS
  "patient_id": "P-12345",                       // Your internal patient ID
  "notes": "Patient presenting with persistent cough and chest discomfort",
  "provider_id": "PROV-001",                     // Your provider identifier
  "provider_name": "City Medical Center",        // Your facility name
  "referring_physician": "Dr. Smith",            // If applicable
  "prior_authorization": "AUTH-123456",          // If pre-authorized
  
  // ADDITIONAL PATIENT INFO (optional but helpful)
  "patient_dob": "1985-06-15",                   // YYYY-MM-DD
  "patient_gender": "M",                         // M/F/Other
  "emergency": false                             // Boolean for emergency claims
};
```

### **Complete JavaScript Integration Example**
```javascript
class PayorClaimsAPI {
  constructor(baseUrl, apiKey = null, providerId = null) {
    this.baseUrl = baseUrl;
    this.apiKey = apiKey;
    this.providerId = providerId;
  }

  async submitClaim(claimData) {
    try {
      const headers = {
        'Content-Type': 'application/json'
      };
      
      // Add authentication if provided
      if (this.apiKey) {
        headers['X-API-Key'] = this.apiKey;
      }
      if (this.providerId) {
        headers['X-Provider-ID'] = this.providerId;
      }

      const response = await fetch(`${this.baseUrl}/claims/`, {
        method: 'POST',
        headers: headers,
        body: JSON.stringify(claimData)
      });

      const result = await response.json();

      if (!response.ok) {
        throw new Error(result.error || `HTTP ${response.status}`);
      }

      return result;
    } catch (error) {
      console.error('Claim submission failed:', error);
      throw error;
    }
  }

  async getClaimStatus(claimId) {
    try {
      const response = await fetch(`${this.baseUrl}/claims/${claimId}/`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          'X-API-Key': this.apiKey,
          'X-Provider-ID': this.providerId
        }
      });

      return await response.json();
    } catch (error) {
      console.error('Status check failed:', error);
      throw error;
    }
  }
}

// Usage Example
const payorAPI = new PayorClaimsAPI(
  'http://localhost:8000/api',
  'your-api-key',
  'PROV-001'
);

// Submit a claim
const claimResult = await payorAPI.submitClaim({
  patient_name: "John Doe",
  insurance_id: "BC-789-456",
  diagnosis_code: "J20.9",
  procedure_code: "99213",
  amount: "1250.00",
  diagnosis_description: "Acute Bronchitis",
  procedure_description: "Office consultation and treatment",
  date_of_service: "2024-10-03",
  priority: "medium",
  notes: "Patient reports 5-day history of productive cough"
});

console.log('Claim submitted:', claimResult);
```

## 📥 **Receiving Responses from Payor**

### **Immediate Response (Synchronous)**

When you submit a claim, you'll receive an immediate response:

#### **Success Response (201 Created)**
```json
{
  "success": true,
  "message": "Claim submitted successfully",
  "claim": {
    "claim_id": "CLM-20241003-ABC123",
    "patient_name": "John Doe",
    "insurance_id": "BC-789-456",
    "diagnosis_code": "J20.9",
    "procedure_code": "99213",
    "amount": 1250.00,
    "status": "approved",
    "coverage_validated": true,
    "coverage_message": "Coverage validated successfully",
    "auto_approved": true,
    "submitted_date": "2024-10-03T10:30:00Z",
    "processed_date": "2024-10-03T10:30:01Z",
    "payor_id": "PAY001",
    "expected_payment": 1000.00,
    "patient_responsibility": 250.00,
    "notes": "Auto-approved based on policy coverage"
  },
  "status": "approved",
  "auto_approved": true,
  "processing_time_ms": 1250
}
```

#### **Error Response (400/404)**
```json
{
  "error": "Insurance ID BC-999-999 not found or not covered by this payor",
  "error_code": "INSURANCE_NOT_FOUND",
  "claim_id": null,
  "suggestions": [
    "Verify insurance ID format",
    "Check if patient is enrolled with this payor",
    "Contact payor customer service"
  ]
}
```

#### **Under Review Response (201 Created)**
```json
{
  "success": true,
  "message": "Claim submitted for manual review",
  "claim": {
    "claim_id": "CLM-20241003-DEF456",
    "status": "under_review",
    "coverage_validated": false,
    "coverage_message": "Procedure code 15776 is excluded from coverage",
    "auto_approved": false,
    "review_reason": "Procedure not covered under patient's current plan",
    "estimated_review_time": "24-48 hours",
    "reviewer_contact": "claims@payor.com"
  },
  "status": "under_review",
  "auto_approved": false
}
```

### **Handling Different Response Types**
```javascript
async function processClaim(claimData) {
  try {
    const response = await payorAPI.submitClaim(claimData);
    
    switch (response.status) {
      case 'approved':
        console.log('✅ Claim AUTO-APPROVED!');
        console.log(`Expected payment: $${response.claim.expected_payment}`);
        console.log(`Patient responsibility: $${response.claim.patient_responsibility}`);
        
        // Update your system with approval
        updateClaimStatus(response.claim.claim_id, 'approved', response.claim);
        break;
        
      case 'under_review':
        console.log('🔍 Claim submitted for manual review');
        console.log(`Review reason: ${response.claim.review_reason}`);
        console.log(`Estimated time: ${response.claim.estimated_review_time}`);
        
        // Set up polling or webhook for status updates
        scheduleStatusCheck(response.claim.claim_id);
        break;
        
      case 'rejected':
        console.log('❌ Claim rejected');
        console.log(`Reason: ${response.claim.rejection_reason}`);
        
        // Handle rejection in your system
        handleClaimRejection(response.claim);
        break;
    }
  } catch (error) {
    console.error('Claim submission failed:', error);
    // Handle submission errors
  }
}
```

## 🔔 **Receiving Status Updates (Webhook Integration)**

### **Webhook Notifications Overview**
The payor system **automatically sends real-time notifications** to your webhook endpoint when claims are processed. This eliminates the need for constant polling and provides instant updates on claim status changes.

**Webhook Events Sent:**
- ✅ **Claim Submitted** - Immediate confirmation when claim is received
- 🔍 **Under Review** - When manual review is required
- ✅ **Claim Approved** - Instant approval with payment details
- ❌ **Claim Rejected** - Rejection with detailed reasons

### **Set Up Webhook Endpoint**
Configure your webhook endpoint to receive status updates from the payor:

```javascript
// Your webhook endpoint (e.g., POST /webhooks/payor-claims)
app.post('/webhooks/payor-claims', (req, res) => {
  const claimUpdate = req.body;
  
  console.log('Received claim update:', claimUpdate);
  
  // Verify webhook signature (recommended for security)
  if (!verifyWebhookSignature(req.headers, req.body)) {
    return res.status(401).json({ error: 'Invalid signature' });
  }
  
  // Process the update
  processClaimUpdate(claimUpdate);
  
  // Respond to acknowledge receipt
  res.json({ received: true });
});

function processClaimUpdate(update) {
  const { claim_id, status, message, processed_by, processed_date } = update;
  
  // Update your database
  updateClaimInDatabase(claim_id, {
    status: status,
    payor_message: message,
    processed_by: processed_by,
    processed_date: processed_date
  });
  
  // Notify relevant staff
  if (status === 'approved') {
    notifyBillingDepartment(claim_id, 'approved');
  } else if (status === 'rejected') {
    notifyProviderStaff(claim_id, 'rejected', message);
  }
}
```

### **Webhook Payload Structure**
The payor sends comprehensive webhook notifications with all relevant claim information:

```json
{
  "event_type": "claim_status_update",
  "timestamp": "2024-10-03T15:30:00Z",
  "claim_id": "CLM-20241003-ABC123",
  "previous_status": "under_review",
  "new_status": "approved",
  "message": "Claim approved after validation",
  "processed_by": "automated_system",
  "processed_date": "2024-10-03T15:29:45Z",
  
  // Patient and claim details
  "patient_name": "John Doe",
  "insurance_id": "BC-789-456",
  "provider_id": "PROV-001",
  "amount": 1250.00,
  "coverage_validated": true,
  "coverage_message": "Coverage validated successfully",
  "auto_approved": true,
  
  // Payment information (when approved)
  "payment_details": {
    "approved_amount": 1000.00,
    "patient_responsibility": 250.00,
    "expected_payment_date": "2024-10-10",
    "payment_method": "ACH"
  },
  
  // Security signature
  "webhook_signature": "sha256=abc123def456..."
}
```

## 🔍 **Polling for Status Updates (Alternative to Webhooks)**

If webhooks aren't feasible, you can poll for claim status:

```javascript
class ClaimStatusPoller {
  constructor(payorAPI, pollInterval = 30000) { // 30 seconds
    this.payorAPI = payorAPI;
    this.pollInterval = pollInterval;
    this.activeClaims = new Map();
  }

  startPolling(claimId) {
    if (this.activeClaims.has(claimId)) {
      return; // Already polling this claim
    }

    const intervalId = setInterval(async () => {
      try {
        const status = await this.payorAPI.getClaimStatus(claimId);
        
        if (status.claim.status !== 'under_review') {
          // Status changed, stop polling
          this.stopPolling(claimId);
          this.handleStatusUpdate(status.claim);
        }
      } catch (error) {
        console.error(`Error polling claim ${claimId}:`, error);
      }
    }, this.pollInterval);

    this.activeClaims.set(claimId, intervalId);
  }

  stopPolling(claimId) {
    const intervalId = this.activeClaims.get(claimId);
    if (intervalId) {
      clearInterval(intervalId);
      this.activeClaims.delete(claimId);
    }
  }

  handleStatusUpdate(claim) {
    console.log(`Claim ${claim.claim_id} status changed to: ${claim.status}`);
    // Update your system accordingly
  }
}

// Usage
const poller = new ClaimStatusPoller(payorAPI);
poller.startPolling('CLM-20241003-ABC123');
```

## 🏥 **Medical Codes Integration**

### **Supported ICD-10 Diagnosis Codes**
Common codes that are typically covered:
```javascript
const commonICD10Codes = {
  'J20.9': 'Acute bronchitis, unspecified',
  'Z00.00': 'General medical exam without abnormal findings',
  'I25.10': 'Atherosclerotic heart disease',
  'E11.9': 'Type 2 diabetes without complications',
  'I10': 'Essential hypertension',
  'J45.9': 'Asthma, unspecified',
  'R51': 'Headache',
  'N39.0': 'Urinary tract infection',
  'K21.9': 'GERD without esophagitis',
  'M54.5': 'Low back pain'
};
```

### **Supported CPT Procedure Codes**
```javascript
const commonCPTCodes = {
  '99213': 'Office visit, established patient, low complexity',
  '99214': 'Office visit, established patient, moderate complexity',
  '85025': 'Complete blood count (CBC)',
  '80053': 'Comprehensive metabolic panel',
  '93000': 'Electrocardiogram, routine ECG',
  '36415': 'Venous blood collection',
  '99396': 'Preventive medicine, established, 40-64 years',
  '76700': 'Abdominal ultrasound'
};
```

### **Code Validation Helper**
```javascript
function validateMedicalCodes(diagnosisCode, procedureCode) {
  const errors = [];
  
  // Basic ICD-10 format validation (simplified)
  if (!/^[A-Z]\d{2}(\.\d{1,2})?$/.test(diagnosisCode)) {
    errors.push('Invalid ICD-10 format for diagnosis code');
  }
  
  // Basic CPT format validation (simplified)
  if (!/^\d{5}$/.test(procedureCode)) {
    errors.push('Invalid CPT format for procedure code');
  }
  
  return {
    isValid: errors.length === 0,
    errors: errors
  };
}
```

## 🛠️ **Error Handling Best Practices**

### **Comprehensive Error Handler**
```javascript
class ClaimSubmissionError extends Error {
  constructor(message, code, claimData = null) {
    super(message);
    this.name = 'ClaimSubmissionError';
    this.code = code;
    this.claimData = claimData;
  }
}

async function submitClaimWithRetry(claimData, maxRetries = 3) {
  let lastError;
  
  for (let attempt = 1; attempt <= maxRetries; attempt++) {
    try {
      const result = await payorAPI.submitClaim(claimData);
      return result;
    } catch (error) {
      lastError = error;
      
      // Don't retry on client errors (4xx)
      if (error.status >= 400 && error.status < 500) {
        throw new ClaimSubmissionError(
          error.message,
          'CLIENT_ERROR',
          claimData
        );
      }
      
      // Wait before retry (exponential backoff)
      if (attempt < maxRetries) {
        const delay = Math.pow(2, attempt) * 1000; // 2s, 4s, 8s
        await new Promise(resolve => setTimeout(resolve, delay));
      }
    }
  }
  
  throw new ClaimSubmissionError(
    `Failed after ${maxRetries} attempts: ${lastError.message}`,
    'MAX_RETRIES_EXCEEDED',
    claimData
  );
}
```

## 🧪 **Testing Webhook Integration**

### **Test Webhook Server**
Use the provided test webhook server to verify integration:

```bash
# Install Flask (if not already installed)
pip install flask

# Start the test webhook server
python test_provider_webhook_server.py

# Server will run on http://localhost:3000
# Webhook endpoint: http://localhost:3000/webhooks/payor-claims
```

### **Webhook Testing Steps**
1. **Start webhook server**: `python test_provider_webhook_server.py`
2. **Submit test claim** through the payor API
3. **View real-time webhook** notifications in the server console
4. **Check webhook history** at `http://localhost:3000/webhooks/history`

### **Expected Webhook Flow**
```
Submit Claim → Immediate Webhook (submitted) → Processing → Final Webhook (approved/rejected)
```

## 📊 **Integration Testing**

### **Test Cases to Implement**
```javascript
describe('Payor Claims API Integration', () => {
  test('should auto-approve covered claim', async () => {
    const claimData = {
      patient_name: "Test Patient",
      insurance_id: "BC-789-456",
      diagnosis_code: "J20.9",
      procedure_code: "99213",
      amount: "150.00"
    };
    
    const result = await payorAPI.submitClaim(claimData);
    
    expect(result.success).toBe(true);
    expect(result.status).toBe('approved');
    expect(result.auto_approved).toBe(true);
  });

  test('should handle invalid insurance ID', async () => {
    const claimData = {
      patient_name: "Test Patient",
      insurance_id: "INVALID-123",
      diagnosis_code: "J20.9",
      amount: "150.00"
    };
    
    await expect(payorAPI.submitClaim(claimData))
      .rejects.toThrow('Insurance ID INVALID-123 not found');
  });

  test('should require manual review for excluded codes', async () => {
    const claimData = {
      patient_name: "Test Patient",
      insurance_id: "BC-789-456",
      diagnosis_code: "Z51.12", // Excluded cosmetic procedure
      procedure_code: "15776",  // Excluded cosmetic surgery
      amount: "5000.00"
    };
    
    const result = await payorAPI.submitClaim(claimData);
    
    expect(result.status).toBe('under_review');
    expect(result.auto_approved).toBe(false);
  });
});
```

## 🚀 **Sample Implementation (React/Node.js)**

### **Frontend Integration (React)**
```jsx
import React, { useState } from 'react';

const ClaimSubmissionForm = () => {
  const [formData, setFormData] = useState({
    patient_name: '',
    insurance_id: '',
    diagnosis_code: '',
    procedure_code: '',
    amount: ''
  });
  const [submitStatus, setSubmitStatus] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSubmitStatus({ type: 'loading', message: 'Submitting claim...' });

    try {
      const response = await fetch('/api/submit-claim', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData)
      });

      const result = await response.json();

      if (result.success) {
        setSubmitStatus({
          type: 'success',
          message: result.auto_approved 
            ? 'Claim approved instantly!' 
            : 'Claim submitted for review',
          claim: result.claim
        });
      } else {
        setSubmitStatus({
          type: 'error',
          message: result.error
        });
      }
    } catch (error) {
      setSubmitStatus({
        type: 'error',
        message: 'Failed to submit claim'
      });
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <input
        type="text"
        placeholder="Patient Name"
        value={formData.patient_name}
        onChange={(e) => setFormData({...formData, patient_name: e.target.value})}
        required
      />
      <input
        type="text"
        placeholder="Insurance ID"
        value={formData.insurance_id}
        onChange={(e) => setFormData({...formData, insurance_id: e.target.value})}
        required
      />
      {/* Add other fields... */}
      
      <button type="submit" disabled={submitStatus?.type === 'loading'}>
        Submit Claim
      </button>

      {submitStatus && (
        <div className={`status ${submitStatus.type}`}>
          {submitStatus.message}
          {submitStatus.claim && (
            <div>Claim ID: {submitStatus.claim.claim_id}</div>
          )}
        </div>
      )}
    </form>
  );
};
```

### **Backend Integration (Node.js/Express)**
```javascript
const express = require('express');
const app = express();

app.use(express.json());

// Proxy endpoint to payor API
app.post('/api/submit-claim', async (req, res) => {
  try {
    const claimData = {
      ...req.body,
      provider_id: 'PROV-001',
      provider_name: 'Your Medical Center',
      date_of_service: new Date().toISOString().split('T')[0]
    };

    const payorResponse = await fetch('http://localhost:8000/api/claims/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-Provider-ID': 'PROV-001'
      },
      body: JSON.stringify(claimData)
    });

    const result = await payorResponse.json();
    
    // Log the submission for your records
    console.log('Claim submitted:', result);
    
    res.json(result);
  } catch (error) {
    console.error('Claim submission error:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

app.listen(3000, () => {
  console.log('Provider API server running on port 3000');
});
```

## ⚙️ **Webhook Registration**

### **Register Your Webhook URL**
To receive automatic notifications, register your webhook endpoint with the payor:

```javascript
// Contact payor support to register your webhook
const webhookRegistration = {
  provider_id: "PROV-001",
  webhook_url: "https://your-domain.com/webhooks/payor-claims",
  secret_key: "your-webhook-secret",
  events: ["claim_status_update", "payment_processed"],
  active: true
};
```

### **Webhook Security**
- All webhooks include **HMAC SHA-256 signatures** for verification
- Use **HTTPS endpoints** in production
- **Verify signatures** to ensure authenticity
- **Respond with 200 status** to acknowledge receipt

### **Webhook Retry Logic**
- Payor retries failed webhooks **3 times** with exponential backoff
- Failed webhooks are logged for manual review
- Providers can request webhook replay for specific time periods

## 📋 **Integration Checklist**

- [ ] **Set up API endpoints** for claim submission
- [ ] **Implement authentication** (API keys or tokens)  
- [ ] **Add medical code validation** on your side
- [ ] **Handle all response types** (approved, under_review, rejected)
- [ ] **Set up webhook endpoint** for status updates
- [ ] **Register webhook URL** with payor support
- [ ] **Implement webhook signature verification**
- [ ] **Test webhook integration** with provided test server
- [ ] **Implement error handling** and retry logic
- [ ] **Add comprehensive logging** for audit trails
- [ ] **Test with all claim scenarios** (covered, excluded, invalid)
- [ ] **Set up monitoring** for API health and response times
- [ ] **Document your integration** for your team

## 🔗 **Support and Resources**

- **API Documentation**: Full technical specs at `/api/docs/`
- **Test Environment**: http://localhost:8000/api for development
- **Webhook Testing**: Use ngrok or similar for local webhook testing
- **Medical Codes Reference**: Built-in cheatsheet in payor dashboard
- **Support Contact**: claims-api-support@payor.com

---

This integration guide provides everything needed to connect your provider system with the HCMS Payor Backend. The API is designed for easy integration with immediate feedback and comprehensive error handling. 🚀