# Troubleshooting: Medical Codes Cheatsheet Not Visible

## ✅ Checklist - Do This First

### 1. Start Django Backend
```bash
cd c:\Users\sagar\integrationdemo\Provider
python manage.py runserver 0.0.0.0:8001
```

**Expected output:**
```
Starting development server at http://0.0.0.0:8001/
```

### 2. Start Frontend (Already Running)
Your Vite server is already running on port 3001 ✅

### 3. Open Browser
Navigate to: **http://localhost:8001** (not 3001!)

### 4. Login to Dashboard
- Use your provider credentials
- Should see the Provider Dashboard

### 5. Click "Submit New Claim"
- Look for the blue button that says "+ Submit New Claim"
- Click it to open the claim form dialog

### 6. Look for the Button
**In the dialog header**, you should see:
```
Submit New Claim                    [Medical Codes Reference]
                                     ↑ This button should be here
```

## 🔍 Where Exactly Is It?

The button appears **inside the claim submission dialog**, not on the main dashboard.

**Visual Guide:**
```
Dashboard → Submit New Claim Button → Dialog Opens
                                          ↓
                            ┌─────────────────────────────┐
                            │ Submit New Claim      [📖] │ ← HERE!
                            │ Create a new insurance...  │
                            ├─────────────────────────────┤
                            │ [Patient Name field]        │
                            │ [Insurance ID field]        │
                            │ ...                         │
                            └─────────────────────────────┘
```

## 🐛 Common Issues

### Issue 1: Backend Not Running
**Symptom:** Can't access http://localhost:8001

**Solution:**
```bash
cd c:\Users\sagar\integrationdemo\Provider
python manage.py runserver 0.0.0.0:8001
```

### Issue 2: Not Logged In
**Symptom:** See login page, not dashboard

**Solution:**
- Login with your provider credentials
- Check that you're registered as a provider (not patient)

### Issue 3: Wrong URL
**Symptom:** Page loads but looks broken

**Solution:**
- Use http://localhost:8001 (backend)
- NOT http://localhost:3001 (frontend dev server)
- The Vite proxy forwards requests to port 8001

### Issue 4: Dialog Not Opening
**Symptom:** Can't find "Submit New Claim" button

**Solution:**
- Make sure you're on the Provider Dashboard
- Look for the blue button with a "+" icon
- Should be in the top section of the dashboard

### Issue 5: Button Not Visible in Dialog
**Symptom:** Dialog opens but no Medical Codes button

**Check Browser Console:**
1. Press **F12** to open DevTools
2. Go to **Console** tab
3. Look for any errors (red text)
4. Check **Elements** tab and search for "MedicalCodesCheatsheet"

**If you see errors:**
- Share them with me
- Might be an import issue or component error

### Issue 6: Styling Issue
**Symptom:** Button exists but invisible (white on white)

**Quick Test:**
1. Open dialog
2. Press **F12**
3. Go to **Elements** tab
4. Look for: `<button>Medical Codes Reference</button>`
5. If you find it, it's a styling issue

**Solution:**
- Hard refresh: `Ctrl + Shift + R`
- Clear cache and hard reload

## 🧪 Quick Debug Test

Open Browser Console (F12) and paste this:
```javascript
// Check if component exists
console.log('Checking for Medical Codes button...');
const buttons = document.querySelectorAll('button');
const foundButton = Array.from(buttons).find(btn => 
  btn.textContent.includes('Medical Codes') || 
  btn.textContent.includes('Reference')
);
if (foundButton) {
  console.log('✅ FOUND:', foundButton);
  foundButton.style.border = '3px solid red';
  foundButton.scrollIntoView();
} else {
  console.log('❌ NOT FOUND - Button not rendered');
}
```

This will:
- Search for the button
- Add a red border if found
- Tell you if it's not rendering

## 📸 What You Should See

### Step 1: Main Dashboard
![Should show "Submit New Claim" button]

### Step 2: Click Submit New Claim
Dialog opens with form fields

### Step 3: Look at Top Right
Should see "Medical Codes Reference" button with book icon 📖

### Step 4: Click That Button
Another dialog opens showing the cheatsheet

## 🎯 Still Not Visible?

### Action 1: Check File Exists
```bash
# In Provider/frontend folder:
dir src\components\MedicalCodesCheatsheet.jsx
```

Should show the file exists.

### Action 2: Check Import in Dashboard
```bash
# Search for the import:
findstr /C:"MedicalCodesCheatsheet" src\components\dashboards\ProviderDashboard.jsx
```

Should show:
```
import MedicalCodesCheatsheet from '../MedicalCodesCheatsheet';
<MedicalCodesCheatsheet onCodeSelect={handleCodeSelect} />
```

### Action 3: Restart Everything
```bash
# Stop Vite (Ctrl+C in frontend terminal)
# Stop Django (Ctrl+C in backend terminal)

# Start Django:
cd c:\Users\sagar\integrationdemo\Provider
python manage.py runserver 0.0.0.0:8001

# Start Vite (in another terminal):
cd c:\Users\sagar\integrationdemo\Provider\frontend
npm run dev
```

### Action 4: Clear Everything
```bash
# In frontend folder:
rm -rf node_modules/.vite
# Or Windows:
rmdir /s /q node_modules\.vite

# Restart:
npm run dev
```

## 📞 Need More Help?

Share:
1. **Screenshot** of the claim submission dialog
2. **Browser console errors** (F12 → Console tab)
3. **Django terminal output** (any errors?)
4. **Result** of the debug JavaScript test above

---

## TL;DR

1. ✅ Django running on 8001?
2. ✅ Browser at http://localhost:8001?
3. ✅ Logged in to dashboard?
4. ✅ Clicked "Submit New Claim"?
5. ✅ Dialog opened?
6. 👀 Look for "Medical Codes Reference" button in dialog header!

The button is **INSIDE the claim dialog**, not on the main dashboard!
