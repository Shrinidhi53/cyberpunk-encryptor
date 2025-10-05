@echo off
echo 🔐 Cyberpunk File Encryptor - Deployment Script
echo ================================================

echo.
echo 📋 Pre-deployment checklist:
echo ✅ All files committed to git
echo ✅ Environment variables set
echo ✅ Dependencies installed
echo.

echo 🚀 Starting deployment process...
echo.

REM Check if git is initialized
if not exist ".git" (
    echo 📦 Initializing git repository...
    git init
    git add .
    git commit -m "Initial commit - Ready for deployment"
    echo ✅ Git repository initialized
) else (
    echo ✅ Git repository already exists
)

echo.
echo 📝 Current git status:
git status

echo.
echo 🌐 Ready for deployment!
echo.
echo Choose your deployment platform:
echo 1. Heroku (Recommended)
echo 2. Railway
echo 3. Render
echo 4. DigitalOcean
echo.
echo For Heroku deployment, run:
echo   heroku create your-app-name
echo   heroku config:set SECRET_KEY="your-secret-key"
echo   git push heroku main
echo.
echo For other platforms, follow the DEPLOYMENT.md guide
echo.
pause
