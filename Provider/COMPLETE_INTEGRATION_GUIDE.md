# Complete Provider-Payor Integration Guide

## Table of Contents
1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Quick Start](#quick-start)
4. [Provider Dashboard Usage](#provider-dashboard-usage)
5. [Insurance ID Mappings](#insurance-id-mappings)
6. [API Integration](#api-integration)
7. [Troubleshooting](#troubleshooting)
8. [Production Deployment](#production-deployment)

## Overview

This system provides seamless integration between healthcare providers and payor systems for claim submission and processing. When a provider creates a claim, it is automatically saved locally and submitted to the appropriate payor system based on the patient's insurance ID.

### Key Features
- ✅ **Dual Storage**: Claims saved locally and in payor system
- ✅ **Automatic Routing**: Insurance ID-based payor routing
- ✅ **Real-time Processing**: Immediate claim submission via ngrok
- ✅ **Status Synchronization**: Claim status updates across systems
- ✅ **HIPAA Compliance**: Encrypted PII data handling

## Architecture

```
Provider System ──────────────────────────────────────────┐
     (Local)                                               │
      │                                                    │
      ├─ MongoDB (Local Claims)                           │
      │                                                    │
      └─ Auto-Submit via ngrok ──┐                        │
                                 │                        │
                                 ▼                        │
                            Payor Router ──────────────────┤
                            (Insurance ID                  │
                             Mapping)                      │
                                 │                        │
                                 ▼                        │
                            Payor System ──────────────────┤
                            (Remote Claims)                │
                                 │                        │
                                 ▼                        │
                            Payor Dashboard ───────────────┘
                            (Web Interface)
```

## Quick Start

### 1. Start All Systems

**Terminal 1 - Payor System:**
```bash
cd c:\Users\sagar\HCMS_payor_backed
python manage.py runserver 8000
```

**Terminal 2 - Provider System:**
```bash
cd c:\Users\sagar\HCMS_payor_backed\Pro\Provider
python manage.py runserver 8001
```

**Terminal 3 - ngrok Tunnel:**
```bash
ngrok http 8000
```
Copy the HTTPS ngrok URL (e.g., `https://abc123.ngrok-free.app`)

### 2. Setup Insurance Mappings

```bash
cd c:\Users\sagar\HCMS_payor_backed
python setup_insurance_mappings.py
```

### 3. Update Provider Configuration

Edit `Pro/Provider/claims/mongo_views.py` and update the ngrok URL:
```python
PAYOR_BASE_URL = "https://your-ngrok-url.ngrok-free.app"  # Replace with your ngrok URL
```

### 4. Test Integration

1. Go to `http://localhost:8001` (Provider Dashboard)
2. Register/Login as a provider
3. Create a test claim with insurance ID "INS001"
4. Verify claim appears in both systems

## Provider Dashboard Usage

### Accessing the Dashboard

1. **Navigate to**: `http://localhost:8001`
2. **Register** a new provider account or **Login**
3. **Access Dashboard** to manage claims

### Creating a New Claim

#### Step 1: Click "Create New Claim"
![Create Claim Button](button would be here)

#### Step 2: Fill Required Fields

| Field | Description | Example |
|-------|-------------|---------|
| **Patient Name** | Full name of the patient | John Doe |
| **Insurance ID** | Insurance policy identifier | INS001 |
| **Diagnosis Code** | ICD-10 diagnostic code | M79.3 |
| **Diagnosis Description** | Description of the diagnosis | Panniculitis, unspecified |
| **Procedure Code** | CPT procedure code | 99213 |
| **Procedure Description** | Description of the procedure | Office visit, established patient |
| **Amount Requested** | Claim amount in USD | 150.00 |
| **Notes** | Additional information | Follow-up appointment |

#### Step 3: Submit Claim

1. Click **"Submit Claim"**
2. System saves claim locally
3. System automatically submits to payor
4. You'll see success confirmation
5. Claim appears in Claims list

### Example Claim Data

```json
{
  "patient_name": "John Doe",
  "insurance_id": "INS001",
  "diagnosis_code": "M79.3",
  "diagnosis_description": "Panniculitis, unspecified",
  "procedure_code": "99213",
  "procedure_description": "Office visit, established patient",
  "amount_requested": 150.00,
  "notes": "Follow-up appointment for ongoing treatment"
}
```

### Claim Submission Flow

```
Provider Creates Claim
         │
         ▼
Save to Local MongoDB ──────────────── ✅ Local Backup
         │
         ▼
Auto-Submit to Payor ──────────────── ✅ Remote Processing
         │
         ▼
Update Local Claim ────────────────── ✅ Status Sync
         │
         ▼
Display in Dashboard ─────────────── ✅ User Feedback
```

## Insurance ID Mappings

### Default Mappings

| Insurance ID | Payor Name | Status |
|-------------|------------|--------|
| INS001 | BlueCross BlueShield | ✅ Active |
| INS002 | Aetna Health | ✅ Active |
| INS003 | United Healthcare | ✅ Active |
| HI12345 | Health Insurance Premium | ✅ Active |

### Adding New Mappings

**Via API:**
```bash
curl -X POST https://your-ngrok-url.ngrok-free.app/api/mappings/insurance-payor/ \
  -H "Content-Type: application/json" \
  -d '{
    "insurance_id": "NEW_INS_ID",
    "payor_name": "New Insurance Company",
    "payor_url": "https://your-ngrok-url.ngrok-free.app",
    "payor_email": "admin@payor.com",
    "payor_password": "admin123",
    "is_active": true
  }'
```

**Via Python Script:**
```python
from payor_api.models import InsurancePayorMappingModel

mapping_model = InsurancePayorMappingModel()
success = mapping_model.create_or_update_mapping("NEW_INS_ID", {
    'payor_name': 'New Insurance Company',
    'payor_url': 'https://your-ngrok-url.ngrok-free.app',
    'payor_email': 'admin@payor.com',
    'payor_password': 'admin123',
    'is_active': True
})
```

## API Integration

### Provider System APIs

#### 1. List Claims
```http
GET /api/mongo/claims/
Authorization: Basic <credentials>
```

#### 2. Create Claim (with Auto-Submit)
```http
POST /api/mongo/claims/
Authorization: Basic <credentials>
Content-Type: application/json

{
  "patient_name": "John Doe",
  "insurance_id": "INS001",
  "diagnosis_description": "Panniculitis, unspecified",
  "amount_requested": 150.00
}
```

#### 3. Get Claim Details
```http
GET /api/mongo/claims/{claim_id}/
Authorization: Basic <credentials>
```

### Payor System APIs

#### 1. Route Claim to Payor
```http
POST /api/route-claim/
Content-Type: application/json

{
  "insurance_id": "INS001",
  "claim_data": {
    "patient_name": "John Doe",
    "amount_requested": 150.00
  }
}
```

#### 2. Get Claim Status Updates
```http
GET /api/provider/claim-updates/?provider_id=PROV001
```

#### 3. Manage Insurance Mappings
```http
GET /api/mappings/insurance-payor/
POST /api/mappings/insurance-payor/
GET /api/mappings/insurance-payor/{insurance_id}/
DELETE /api/mappings/insurance-payor/{insurance_id}/
```

### Code Examples

#### Python Integration

```python
import requests
import json

class PayorIntegration:
    def __init__(self, ngrok_url):
        self.base_url = f"{ngrok_url}/api"
        
    def submit_claim_to_payor(self, claim_data):
        """Submit claim to payor system via ngrok"""
        try:
            route_url = f"{self.base_url}/route-claim/"
            
            routing_data = {
                'insurance_id': claim_data.get('insurance_id', ''),
                'claim_data': claim_data
            }
            
            response = requests.post(
                route_url,
                json=routing_data,
                headers={
                    'Content-Type': 'application/json',
                    'ngrok-skip-browser-warning': 'true'
                },
                timeout=30
            )
            
            if response.status_code == 200:
                return {
                    'success': True,
                    'payor_response': response.json()
                }
            else:
                return {
                    'success': False,
                    'error': f"HTTP {response.status_code}: {response.text}"
                }
        
        except Exception as e:
            return {
                'success': False,
                'error': f"Network error: {str(e)}"
            }
    
    def get_claim_updates(self, provider_id, last_sync=None):
        """Get claim status updates from payor"""
        try:
            params = {'provider_id': provider_id}
            if last_sync:
                params['last_sync_time'] = last_sync
                
            response = requests.get(
                f"{self.base_url}/provider/claim-updates/",
                params=params,
                timeout=30
            )
            
            return response.json() if response.status_code == 200 else None
        
        except Exception as e:
            print(f"Failed to get updates: {e}")
            return None

# Usage Example
payor = PayorIntegration("https://your-ngrok-url.ngrok-free.app")

# Submit claim
claim_data = {
    "patient_name": "John Doe",
    "insurance_id": "INS001",
    "diagnosis_description": "Panniculitis, unspecified",
    "amount_requested": 150.00
}

result = payor.submit_claim_to_payor(claim_data)
print("Submission result:", result)

# Get updates
updates = payor.get_claim_updates("PROV001")
print("Status updates:", updates)
```

#### JavaScript Integration

```javascript
class PayorAPIClient {
    constructor(ngrokUrl) {
        this.baseUrl = `${ngrokUrl}/api`;
    }
    
    async submitClaim(claimData) {
        try {
            const response = await fetch(`${this.baseUrl}/route-claim/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'ngrok-skip-browser-warning': 'true'
                },
                body: JSON.stringify({
                    insurance_id: claimData.insurance_id,
                    claim_data: claimData
                })
            });
            
            const result = await response.json();
            
            return {
                success: response.ok,
                data: result
            };
        } catch (error) {
            return {
                success: false,
                error: error.message
            };
        }
    }
    
    async getClaimUpdates(providerId, lastSync = null) {
        try {
            const params = new URLSearchParams({
                provider_id: providerId
            });
            
            if (lastSync) {
                params.append('last_sync_time', lastSync);
            }
            
            const response = await fetch(
                `${this.baseUrl}/provider/claim-updates/?${params}`
            );
            
            return response.ok ? await response.json() : null;
        } catch (error) {
            console.error('Failed to get updates:', error);
            return null;
        }
    }
}

// Usage in React Component
const PayorClient = new PayorAPIClient('https://your-ngrok-url.ngrok-free.app');

const handleSubmitClaim = async (claimData) => {
    const result = await PayorClient.submitClaim(claimData);
    
    if (result.success) {
        console.log('Claim submitted successfully:', result.data);
        // Update UI with success message
    } else {
        console.error('Claim submission failed:', result.error);
        // Show error message to user
    }
};
```

## Troubleshooting

### Common Issues and Solutions

#### 1. Claim Not Appearing in Payor Dashboard

**Symptoms:**
- Claim created in provider dashboard
- No corresponding claim in payor dashboard
- Provider logs show submission attempt

**Diagnosis:**
```bash
# Check ngrok status
curl https://your-ngrok-url.ngrok-free.app/api/mappings/insurance-payor/

# Test insurance mapping
curl https://your-ngrok-url.ngrok-free.app/api/mappings/insurance-payor/INS001/

# Check provider logs
tail -f Pro/Provider/logs/django.log
```

**Solutions:**
1. Verify ngrok URL is correct and accessible
2. Check insurance ID mapping exists
3. Restart provider system after ngrok URL change
4. Check network connectivity

#### 2. Provider Submission Fails

**Symptoms:**
- Claims save locally but don't submit to payor
- Error messages in provider console
- Network timeout errors

**Diagnosis:**
```bash
# Test direct API call
curl -X POST https://your-ngrok-url.ngrok-free.app/api/route-claim/ \
  -H "Content-Type: application/json" \
  -H "ngrok-skip-browser-warning: true" \
  -d '{"insurance_id": "INS001", "claim_data": {"patient_name": "Test"}}'
```

**Solutions:**
1. Ensure ngrok is running and accessible
2. Update `PAYOR_BASE_URL` in provider code
3. Check firewall/network restrictions
4. Verify payor system is running

#### 3. Insurance ID Not Found

**Symptoms:**
- Error: "No payor mapping found for insurance_id"
- Claims rejected at routing stage

**Solutions:**
```bash
# Create missing mapping
python setup_insurance_mappings.py

# Or manually add mapping
curl -X POST https://your-ngrok-url.ngrok-free.app/api/mappings/insurance-payor/ \
  -H "Content-Type: application/json" \
  -d '{"insurance_id": "YOUR_ID", "payor_name": "Payor Name", ...}'
```

#### 4. Status Sync Issues

**Symptoms:**
- Claims submitted but status not updating
- Provider claims stuck in "pending" status

**Solutions:**
1. Check provider_id is being set correctly
2. Verify payor system is updating claim statuses
3. Test status sync API manually:
```bash
curl "https://your-ngrok-url.ngrok-free.app/api/provider/claim-updates/?provider_id=PROV001"
```

### Debug Checklist

**Provider System:**
- [ ] MongoDB running and accessible
- [ ] Django server running on port 8001
- [ ] ngrok URL updated in code
- [ ] Authentication working
- [ ] Claims saving locally

**Payor System:**
- [ ] MongoDB running and accessible
- [ ] Django server running on port 8000
- [ ] Insurance mappings created
- [ ] APIs responding correctly
- [ ] Claims appearing in dashboard

**ngrok:**
- [ ] Running and accessible
- [ ] HTTPS URL working
- [ ] No browser warnings
- [ ] API endpoints reachable

### Log Files

**Provider System Logs:**
```bash
# Django logs
tail -f Pro/Provider/logs/django.log

# MongoDB logs
tail -f /var/log/mongodb/mongod.log

# Application logs (console output)
# Check the terminal where you ran the provider server
```

**Payor System Logs:**
```bash
# Django logs
tail -f logs/django.log

# Application logs (console output)
# Check the terminal where you ran the payor server
```

## Production Deployment

### Security Considerations

1. **Replace ngrok with proper infrastructure:**
   - Use load balancer (AWS ALB, nginx)
   - Implement proper SSL certificates
   - Set up proper domain names

2. **Authentication & Authorization:**
   - Implement OAuth 2.0 or JWT tokens
   - Add API rate limiting
   - Use proper user management

3. **Data Security:**
   - Encrypt all PII data at rest
   - Use encrypted connections (HTTPS/TLS)
   - Implement proper audit logging
   - Follow HIPAA compliance requirements

4. **Database Security:**
   - Use MongoDB authentication
   - Implement proper backup strategies
   - Set up monitoring and alerting

### Production Environment Variables

```bash
# Payor System (.env)
DJANGO_SECRET_KEY=your-secret-key
MONGODB_HOST=mongodb://localhost:27017/
MONGODB_DATABASE=hcms_payor_production
PAYOR_API_URL=https://api.yourcompany.com
HIPAA_ENCRYPTION_KEY=your-encryption-key
DEBUG=False
ALLOWED_HOSTS=api.yourcompany.com,www.yourcompany.com

# Provider System (.env)
DJANGO_SECRET_KEY=your-secret-key
MONGODB_HOST=mongodb://localhost:27017/
MONGODB_DATABASE=hcms_provider_production
PAYOR_API_URL=https://api.yourcompany.com
DEBUG=False
ALLOWED_HOSTS=provider.yourcompany.com
```

### Deployment Steps

1. **Set up production servers:**
   ```bash
   # Install dependencies
   sudo apt update
   sudo apt install python3 python3-pip mongodb nginx
   
   # Create virtual environments
   python3 -m venv /opt/hcms/payor/venv
   python3 -m venv /opt/hcms/provider/venv
   ```

2. **Configure nginx:**
   ```nginx
   # /etc/nginx/sites-available/hcms
   server {
       listen 80;
       server_name api.yourcompany.com;
       
       location / {
           proxy_pass http://127.0.0.1:8000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }
   }
   
   server {
       listen 80;
       server_name provider.yourcompany.com;
       
       location / {
           proxy_pass http://127.0.0.1:8001;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }
   }
   ```

3. **Set up systemd services:**
   ```ini
   # /etc/systemd/system/hcms-payor.service
   [Unit]
   Description=HCMS Payor System
   After=network.target
   
   [Service]
   User=www-data
   WorkingDirectory=/opt/hcms/payor
   ExecStart=/opt/hcms/payor/venv/bin/python manage.py runserver 8000
   Restart=always
   
   [Install]
   WantedBy=multi-user.target
   ```

4. **Enable and start services:**
   ```bash
   sudo systemctl enable hcms-payor
   sudo systemctl start hcms-payor
   sudo systemctl enable hcms-provider
   sudo systemctl start hcms-provider
   ```

### Monitoring and Maintenance

1. **Set up monitoring:**
   - Use tools like Prometheus, Grafana
   - Monitor API response times
   - Track claim submission success rates
   - Set up alerts for failures

2. **Regular maintenance:**
   - Database backups
   - Log rotation
   - Security updates
   - Performance optimization

## Support and Resources

### Documentation Links
- [Django Documentation](https://docs.djangoproject.com/)
- [MongoDB Documentation](https://docs.mongodb.com/)
- [React Documentation](https://reactjs.org/docs/)

### Getting Help

1. **Check the logs** for error messages
2. **Test API endpoints** individually
3. **Verify configuration** settings
4. **Review this documentation** for troubleshooting steps

### Contact Information

For technical support:
- System Administrator: [your-email@company.com]
- Development Team: [dev-team@company.com]
- Emergency Support: [emergency@company.com]

---

*This integration guide is maintained by the HCMS Development Team*  
*Last updated: December 2024*  
*Version: 2.0*