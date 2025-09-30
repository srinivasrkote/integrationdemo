@echo off
echo ==========================================
echo    Provider App - MongoDB Atlas Ready
echo ==========================================
echo.

REM Check if .env exists
if not exist .env (
    echo ⚠️  WARNING: .env file not found!
    echo.
    echo To use MongoDB Atlas, please:
    echo 1. Copy .env.example to .env
    echo 2. Update MongoDB Atlas credentials in .env
    echo 3. Run this script again
    echo.
    echo For now, the app will use SQLite fallback.
    echo.
    pause
)

echo 🚀 Starting Provider Django Application...
echo.
echo Available endpoints:
echo   📊 Django Admin:        http://localhost:8000/admin/
echo   🔗 Original API:        http://localhost:8000/api/claims/
echo   🌐 MongoDB API:         http://localhost:8000/api/mongo/claims/
echo   📈 Dashboard Stats:     http://localhost:8000/api/mongo/dashboard/stats/
echo   🎯 Frontend:            http://localhost:5173/ (if running)
echo.
echo Press Ctrl+C to stop the server
echo.

python manage.py runserver

echo.
echo Server stopped.
pause