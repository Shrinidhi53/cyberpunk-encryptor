# Deployment Guide for Cyberpunk File Encryptor

## 🚀 Deployment Options

### Option 1: Heroku (Recommended for beginners)

1. **Install Heroku CLI**
   - Download from: https://devcenter.heroku.com/articles/heroku-cli
   - Login: `heroku login`

2. **Prepare your app**
   ```bash
   cd "C:\Users\Shrinidhi Malli\Desktop\encryption"
   git init
   git add .
   git commit -m "Initial commit"
   ```

3. **Create Heroku app**
   ```bash
   heroku create your-app-name
   ```

4. **Set environment variables**
   ```bash
   heroku config:set SECRET_KEY="your-secret-key-here"
   heroku config:set FLASK_DEBUG=False
   ```

5. **Deploy**
   ```bash
   git push heroku main
   ```

### Option 2: Railway

1. **Connect GitHub**
   - Push your code to GitHub
   - Go to https://railway.app
   - Connect your GitHub repository

2. **Deploy**
   - Railway will automatically detect Python
   - Set environment variables in Railway dashboard
   - Deploy with one click

### Option 3: Render

1. **Connect Repository**
   - Push to GitHub
   - Go to https://render.com
   - Create new Web Service

2. **Configure**
   - Connect GitHub repository
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn --bind 0.0.0.0:$PORT app:app`

### Option 4: DigitalOcean App Platform

1. **Create App**
   - Go to https://cloud.digitalocean.com/apps
   - Create new app from GitHub

2. **Configure**
   - Select Python
   - Set build and run commands
   - Add environment variables

### Option 5: VPS Deployment (Advanced)

1. **Set up server**
   ```bash
   # Install Python, nginx, and dependencies
   sudo apt update
   sudo apt install python3 python3-pip nginx
   ```

2. **Deploy application**
   ```bash
   # Clone repository
   git clone your-repo-url
   cd encryption
   
   # Install dependencies
   pip3 install -r requirements.txt
   
   # Run with gunicorn
   gunicorn --bind 0.0.0.0:8000 app:app
   ```

3. **Configure nginx**
   ```nginx
   server {
       listen 80;
       server_name your-domain.com;
       
       location / {
           proxy_pass http://127.0.0.1:8000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }
   }
   ```

## 🔧 Environment Variables

Set these in your deployment platform:

- `SECRET_KEY`: Random secret key for Flask sessions
- `FLASK_DEBUG`: Set to `False` for production
- `PORT`: Usually set automatically by platform

## 📝 Important Notes

1. **File Storage**: Current setup uses local storage (files deleted after 1 hour)
2. **Security**: Change the SECRET_KEY in production
3. **HTTPS**: Enable HTTPS for secure file transfers
4. **Monitoring**: Consider adding logging and monitoring

## 🎯 Quick Start (Heroku)

```bash
# 1. Install Heroku CLI and login
heroku login

# 2. Initialize git and commit
git init
git add .
git commit -m "Ready for deployment"

# 3. Create and deploy
heroku create your-encryptor-app
heroku config:set SECRET_KEY="$(python -c 'import secrets; print(secrets.token_hex(32))')"
git push heroku main

# 4. Open your app
heroku open
```

Your app will be live at: https://your-encryptor-app.herokuapp.com
