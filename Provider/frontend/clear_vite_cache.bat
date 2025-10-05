@echo off
echo Clearing Vite cache...
cd /d C:\Users\sagar\integrationdemo\Provider\frontend
if exist node_modules\.vite (
    rmdir /s /q node_modules\.vite
    echo Vite cache cleared successfully!
) else (
    echo No Vite cache found (already clean)
)
echo.
echo Now restart Vite with: npm run dev
pause
