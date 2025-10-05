@echo off
echo ==========================================
echo    Provider System Startup (Local Only)
echo ==========================================
echo.

echo Starting Django Backend...
cd /d "D:\Provider\integrationdemo\Provider"
start "Django Backend" cmd /k "python manage.py runserver"

echo.
echo Waiting 5 seconds for backend to start...
timeout /t 5 /nobreak > nul

echo Starting React Frontend...
cd /d "D:\Provider\integrationdemo\Provider\frontend"
start "React Frontend" cmd /k "npm run dev"

echo.
echo ==========================================
echo    System Started Successfully!
echo ==========================================
echo.
echo Available URLs:
echo   Backend:  http://127.0.0.1:8000
echo   Frontend: http://localhost:3001 or http://localhost:3002
echo.
echo Note: No external access (ngrok not installed)
echo For external access, install ngrok using the guide in:
echo   NGROK_INSTALL_GUIDE.md
echo.
echo Press any key to test webhook connectivity...
pause > nul

echo.
echo Testing backend connectivity...
curl -X GET http://127.0.0.1:8000/api/webhooks/health/

echo.
echo Setup complete! Both services should be running in separate windows.
pause