# Test the Medical Codes Cheatsheet

## ✅ Quick Test Instructions

### Step 1: Ensure Frontend is Running

```bash
cd c:\Users\sagar\integrationdemo\Provider\frontend
npm run dev
```

Should see:
```
VITE v5.x.x  ready in xxx ms

➜  Local:   http://localhost:3001/
```

### Step 2: Check Backend is Running

```bash
cd c:\Users\sagar\integrationdemo\Provider
python manage.py runserver 0.0.0.0:8001
```

Should see:
```
Starting development server at http://0.0.0.0:8001/
```

### Step 3: Open Browser

Navigate to: **http://localhost:8001**

### Step 4: Login to Dashboard

Use your provider credentials to login.

### Step 5: Test the Cheatsheet

1. **Click "Submit New Claim"** (blue button with Plus icon)
   
2. **Look at the dialog header** - You should see:
   ```
   Submit New Claim         [Medical Codes Reference] ← This button!
   ```

3. **Click "Medical Codes Reference"** button

4. **Verify Modal Opens** with:
   - 🩺 Title: "Medical Codes Cheatsheet"
   - 🔍 Search bar at top
   - Two tabs: "ICD-10 Diagnosis (25)" and "CPT Procedures (25)"
   - List of medical codes

5. **Test Search**:
   - Type "diabetes" → Should show E11.9
   - Type "99214" → Should jump to that CPT code
   - Type "respiratory" → Should filter to respiratory codes

6. **Test Code Selection**:
   - Click on "E11.9" card
   - Modal should stay open
   - Check claim form - these fields should auto-fill:
     - ✅ Diagnosis Code: `E11.9`
     - ✅ Diagnosis Description: `Type 2 diabetes mellitus without complications`

7. **Test CPT Tab**:
   - Click "CPT Procedures" tab
   - Search "office visit"
   - Click "99214" card
   - Check claim form - these fields should auto-fill:
     - ✅ Procedure Code: `99214`
     - ✅ Procedure Description: `Office/outpatient visit, established patient, moderate complexity`

8. **Complete and Submit Claim**:
   - Fill in remaining fields:
     - Patient Name: `Test Patient`
     - Insurance ID: `BC-789-456`
     - Amount: `450`
   - Click "Submit Claim"
   - Should see success message

## 🐛 Troubleshooting

### Issue: Button Not Showing

**Solution**: Clear browser cache and refresh
```bash
# In browser: Ctrl+Shift+R (hard refresh)
```

### Issue: Modal Not Opening

**Check Console** (F12):
- Look for any JavaScript errors
- Ensure no import errors

**Fix**:
```bash
# Reinstall dependencies
cd frontend
npm install
npm run dev
```

### Issue: Codes Not Auto-Filling

**Verify**:
1. Click on a code card (should highlight on hover)
2. Check form fields update immediately
3. If not working, check browser console for errors

**Debug**:
```javascript
// Open console (F12) and type:
console.log('Test code selection');
// Then click a code
```

### Issue: Search Not Working

**Verify**:
1. Type in search box
2. Codes should filter in real-time
3. Count in tab headers should update

**Clear Search**:
- Delete text in search box
- Should show all codes again

### Issue: Tabs Not Switching

**Check**:
- Radix UI tabs package installed: `@radix-ui/react-tabs`
- Run: `npm list @radix-ui/react-tabs`
- Should show version ^1.1.3

**Fix**:
```bash
cd frontend
npm install @radix-ui/react-tabs@latest
```

### Issue: Styling Issues

**Verify Tailwind** is working:
1. Check other UI elements have styling
2. If not, restart Vite dev server

```bash
# Stop server (Ctrl+C)
npm run dev
```

## 📋 Test Checklist

Use this checklist to verify everything works:

- [ ] Frontend server running on port 3001
- [ ] Backend server running on port 8001
- [ ] Can login to provider dashboard
- [ ] "Submit New Claim" button visible
- [ ] Claim form dialog opens
- [ ] "Medical Codes Reference" button in dialog header
- [ ] Cheatsheet modal opens
- [ ] Search bar present
- [ ] ICD-10 tab shows 25 codes
- [ ] CPT tab shows 25 codes
- [ ] Search filters codes correctly
- [ ] Clicking ICD-10 code fills diagnosis fields
- [ ] Clicking CPT code fills procedure fields
- [ ] Category badges display with colors
- [ ] CPT codes show pricing (~$XXX)
- [ ] Modal is scrollable
- [ ] Can close modal with X or Esc
- [ ] Form retains selected codes after closing modal
- [ ] Can submit claim with selected codes

## 🎯 Test Scenarios

### Scenario 1: Diabetes Office Visit
```
Goal: Create claim for diabetes follow-up

Steps:
1. Open cheatsheet
2. ICD-10 tab → Search "diabetes" → Click E11.9
3. CPT tab → Search "office" → Click 99214
4. Verify form has:
   - Diagnosis Code: E11.9
   - Diagnosis: Type 2 diabetes...
   - Procedure Code: 99214
   - Procedure: Office/outpatient visit...
5. Add: Patient name, Insurance ID, Amount ($250)
6. Submit claim

Expected: Success ✅
```

### Scenario 2: Blood Work
```
Goal: Create lab work claim

Steps:
1. Open cheatsheet
2. CPT tab → Search "blood" or "CBC"
3. Click "85025 - Blood count; complete (CBC)"
4. ICD-10 tab → Select reason (e.g., R50.9 - Fever)
5. Complete form with patient details
6. Submit

Expected: Success ✅
```

### Scenario 3: Multiple Searches
```
Goal: Test search functionality

Steps:
1. Search "respiratory" → See J codes
2. Clear search
3. Search "99" → See office visit CPT codes
4. Clear search
5. Search "diabetes" → See E11.9
6. Search "gibberish" → See "No codes found"

Expected: All searches work correctly ✅
```

## 📊 Expected Results

### Visual Check
When you open the cheatsheet, you should see:

```
┌─────────────────────────────────────────┐
│ 🩺 Medical Codes Cheatsheet        [X] │
│ Quick reference for ICD-10...           │
├─────────────────────────────────────────┤
│ 🔍 [Search box here]                    │
│                                          │
│ [ICD-10 Diagnosis (25)] [CPT Procs]    │
│                                          │
│ ┌─────────────────────────────────────┐ │
│ │ E11.9         [Endocrine: Pink]     │ │
│ │ Type 2 diabetes mellitus...         │ │
│ └─────────────────────────────────────┘ │
│                                          │
│ ┌─────────────────────────────────────┐ │
│ │ I10           [Cardiovascular: Red] │ │
│ │ Essential hypertension              │ │
│ └─────────────────────────────────────┘ │
│                                          │
│ [More codes scrollable...]              │
│                                          │
│ 💡 Tip: Click any code to auto-fill     │
└─────────────────────────────────────────┘
```

### Behavior Check
- ✅ Hover over code card → Background changes to light blue/green
- ✅ Click code → No page reload, form updates instantly
- ✅ Modal stays open → Can select multiple codes
- ✅ ESC key → Closes modal
- ✅ X button → Closes modal
- ✅ Responsive → Works on smaller screens

## 🔧 Development Notes

### File Locations
```
frontend/src/
├── components/
│   ├── MedicalCodesCheatsheet.jsx  ← Main component
│   ├── dashboards/
│   │   └── ProviderDashboard.jsx   ← Integration point
│   └── ui/
│       ├── tabs.jsx                ← New UI component
│       ├── dialog.jsx              ← Existing
│       ├── button.jsx              ← Existing
│       ├── input.jsx               ← Existing
│       ├── badge.jsx               ← Existing
│       └── card.jsx                ← Existing
```

### Dependencies Used
```json
{
  "@radix-ui/react-tabs": "^1.1.3",
  "@radix-ui/react-dialog": "^1.1.6",
  "lucide-react": "^0.487.0",
  "react": "^18.2.0"
}
```

### Key Functions
```javascript
// In ProviderDashboard.jsx
const handleCodeSelect = (codeData) => {
  // Auto-fills form based on code type
}

// In MedicalCodesCheatsheet.jsx
const filterCodes = (codes, searchTerm) => {
  // Real-time search filtering
}

const getCategoryColor = (category) => {
  // Returns Tailwind classes for badges
}
```

## 🎉 Success Criteria

The feature is working correctly if:

1. ✅ Button appears in claim form
2. ✅ Modal opens with 50 codes
3. ✅ Search filters in real-time
4. ✅ Clicking codes fills form fields
5. ✅ No console errors
6. ✅ Responsive design works
7. ✅ Can submit claims with selected codes

## 🚀 Next Steps

After verifying it works:

1. **Use it in production**: Create real claims faster
2. **Gather feedback**: Ask providers what codes to add
3. **Monitor usage**: Track which codes are most used
4. **Consider enhancements**: See MEDICAL_CODES_QUICK_START.md for ideas

## 📞 Support

If issues persist:
1. Check browser console (F12) for errors
2. Verify all dependencies installed
3. Restart both frontend and backend servers
4. Clear browser cache
5. Try incognito mode

---

**Ready to Test?** Follow the steps above and enjoy faster claim submission! 🎯
