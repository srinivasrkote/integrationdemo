@echo off
echo ================================
echo MongoDB Atlas Setup for Provider
echo ================================
echo.

echo Installing Python packages...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo Error installing packages!
    pause
    exit /b 1
)

echo.
echo Checking environment configuration...
if not exist .env (
    echo .env file not found!
    echo Please create a .env file with your MongoDB Atlas credentials.
    echo See MONGODB_SETUP.md for detailed instructions.
    pause
    exit /b 1
)

echo.
echo Running automated setup...
python setup_mongodb.py

if %errorlevel% equ 0 (
    echo.
    echo ====================================
    echo Setup completed successfully! 🎉
    echo ====================================
    echo.
    echo You can now start the server with:
    echo python manage.py runserver
    echo.
) else (
    echo.
    echo Setup failed. Please check the error messages above.
    echo See MONGODB_SETUP.md for troubleshooting guide.
)

pause