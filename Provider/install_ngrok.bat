@echo off
echo ==========================================
echo    NGROK INSTALLATION SCRIPT
echo ==========================================
echo.

echo Step 1: Downloading ngrok...
echo.

REM Create ngrok directory
if not exist "C:\ngrok" mkdir "C:\ngrok"

echo Please follow these steps:
echo.
echo 1. Go to: https://ngrok.com/download
echo 2. Download "ngrok for Windows"
echo 3. Extract ngrok.exe to C:\ngrok\
echo 4. Run this script again to complete setup
echo.

REM Check if ngrok.exe exists
if exist "C:\ngrok\ngrok.exe" (
    echo ✅ ngrok.exe found in C:\ngrok\
    echo.
    echo Step 2: Adding to PATH...
    
    REM Add to PATH (current session)
    set PATH=%PATH%;C:\ngrok
    
    echo Step 3: Testing installation...
    C:\ngrok\ngrok.exe version
    
    echo.
    echo ✅ ngrok installed successfully!
    echo.
    echo Next steps:
    echo 1. Create account at: https://ngrok.com/signup
    echo 2. Get authtoken from: https://dashboard.ngrok.com/auth
    echo 3. Run: ngrok authtoken YOUR_TOKEN
    echo 4. Run: ngrok http 8000
    echo.
) else (
    echo ❌ ngrok.exe not found in C:\ngrok\
    echo.
    echo Please:
    echo 1. Download from https://ngrok.com/download
    echo 2. Extract ngrok.exe to C:\ngrok\
    echo 3. Run this script again
    echo.
)

pause