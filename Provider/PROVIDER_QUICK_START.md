# Healthcare Provider Integration - Quick Start

## 🏥 For Healthcare Providers

This guide helps you connect your provider system to the payor backend for real-time claim submission and processing.

## Quick Setup (5 minutes)

### Step 1: Get Payor's ngrok URL
Contact your payor administrator and get the ngrok URL (e.g., `https://abc123.ngrok-free.app`)

### Step 2: Download Provider System
```bash
# Download the provider system files
git clone https://github.com/your-repo/HCMS_payor_backed.git
cd HCMS_payor_backed/Pro/Provider
```

### Step 3: Run Setup Script
```bash
python provider_setup.py
```
The script will ask for:
- Payor's ngrok URL
- Your provider information
- Database settings

### Step 4: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 5: Start Systems
```bash
# Terminal 1: Django backend
python manage.py runserver 8001

# Terminal 2: React frontend (if using)
cd frontend
npm install
npm start
```

### Step 6: Test Integration
```bash
python test_integration.py
```

## What This Does

✅ **Dual Storage**: Claims save locally AND submit to payor  
✅ **Automatic Routing**: Insurance ID determines which payor receives claim  
✅ **Real-time Processing**: Immediate claim submission and response  
✅ **Status Updates**: Claim status syncs between systems  

## Usage

1. **Login** to provider dashboard at `http://localhost:8001`
2. **Create Claim** with patient and insurance information
3. **Submit** - claim automatically goes to both systems
4. **Track Status** - updates appear in real-time

## Example Claim
```json
{
  "patient_name": "John Doe",
  "insurance_id": "INS001",
  "diagnosis_description": "Annual checkup",
  "amount_requested": 150.00
}
```

## Support

- **Integration Issues**: Check `test_integration.py` output
- **Connection Problems**: Verify ngrok URL is accessible
- **Technical Support**: Contact payor system administrator

---

*For detailed documentation, see `CROSS_SYSTEM_INTEGRATION_GUIDE.md`*