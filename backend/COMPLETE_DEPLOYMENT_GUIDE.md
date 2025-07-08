# 🚀 RetailGenie Backend - Complete Step-by-Step Deployment Guide

**The Ultimate Guide to Deploy Your AI-Powered Retail Management System**

---

## 📋 Table of Contents

1. [Overview & Prerequisites](#overview--prerequisites)
2. [Pre-Deployment Preparation](#pre-deployment-preparation)
3. [Local Testing & Validation](#local-testing--validation)
4. [Platform-Specific Deployment](#platform-specific-deployment)
   - [Render.com (Recommended)](#rendercom-recommended)
   - [Heroku](#heroku)
   - [Railway](#railway)
   - [Google Cloud Run](#google-cloud-run)
   - [AWS EC2/Elastic Beanstalk](#aws-ec2elastic-beanstalk)
   - [VPS/DigitalOcean](#vpsdigitalocean)
5. [Post-Deployment Configuration](#post-deployment-configuration)
6. [Monitoring & Maintenance](#monitoring--maintenance)
7. [Troubleshooting](#troubleshooting)

---

## 🎯 Overview & Prerequisites

### What You're Deploying
Your RetailGenie backend is a comprehensive AI-powered retail management system featuring:
- 🤖 **AI Assistant** powered by Google Gemini
- 🔥 **Firebase** database and authentication
- 🛍️ **Advanced retail features** (inventory, pricing, analytics)
- 🎮 **Gamification** and loyalty systems
- 📊 **Real-time analytics** and reporting
- 🔐 **Secure authentication** with JWT tokens

### Prerequisites Checklist
- [ ] Python 3.8+ environment
- [ ] Git repository with your code
- [ ] Google Gemini API key
- [ ] Firebase project with service account
- [ ] Domain name (optional but recommended)
- [ ] SSL certificate (handled by most platforms)

---

## 🛠️ Pre-Deployment Preparation

### Step 1: Verify Your Environment Configuration

First, let's ensure your `.env` file is production-ready:

```bash
cd /path/to/RetailGenie/backend
```

**Check your current `.env` file contains:**

```bash
# Production Flask Configuration
FLASK_ENV=production
FLASK_DEBUG=False
SECRET_KEY=your-secure-secret-key
JWT_SECRET=your-jwt-secret-key

# Firebase Configuration
FIREBASE_PROJECT_ID=retailgenie-production
FIREBASE_PRIVATE_KEY_ID=your-private-key-id
FIREBASE_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n"
FIREBASE_CLIENT_EMAIL=firebase-adminsdk-xxx@retailgenie-production.iam.gserviceaccount.com
FIREBASE_CLIENT_ID=your-client-id
FIREBASE_AUTH_URI=https://accounts.google.com/o/oauth2/auth
FIREBASE_TOKEN_URI=https://oauth2.googleapis.com/token

# Google Gemini Configuration
GEMINI_API_KEY=
GEMINI_MODEL=gemini-1.5-flash

# CORS Configuration (update with your domain)
CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com

# Optional: Email Configuration
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SENDER_EMAIL=noreply@yourdomain.com
SENDER_PASSWORD=your-app-password
ADMIN_EMAIL=admin@yourdomain.com
```

### Step 2: Update Production Settings

**Create a production environment file:**

```bash
# Create .env.production
cp .env .env.production
```

**Edit `.env.production` for production:**

```bash
# Production Settings
FLASK_ENV=production
FLASK_DEBUG=False

# Update CORS for your domain
CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com

# Add any production-specific URLs
DATABASE_URL=firebase
REDIS_URL=redis://your-redis-url  # If using cloud Redis
```

### Step 3: Verify Dependencies

**Check `requirements.txt` contains all necessary packages:**

```bash
cat requirements.txt
```

**Should include at minimum:**
```txt
flask==2.3.3
flask-cors==4.0.0
google-generativeai==0.3.0
firebase-admin==6.2.0
python-dotenv==1.0.0
requests==2.31.0
werkzeug==2.3.7
gunicorn==21.2.0
celery==5.3.1
redis==4.6.0
```

**If missing packages, add them:**
```bash
pip freeze > requirements.txt
```

### Step 4: Create Production Startup Files

**Create `wsgi.py` (if not exists):**
```python
from app import create_app

app = create_app()

if __name__ == "__main__":
    app.run()
```

**Create `Procfile` for cloud platforms:**
```bash
echo "web: gunicorn wsgi:app" > Procfile
```

**Create startup script `start_production.sh`:**
```bash
#!/bin/bash
export FLASK_ENV=production
export FLASK_DEBUG=False
gunicorn --bind 0.0.0.0:$PORT wsgi:app
```

```bash
chmod +x start_production.sh
```

---

## 🧪 Local Testing & Validation

### Step 1: Install Dependencies

```bash
# Install all requirements
pip install -r requirements.txt

# Install production server
pip install gunicorn
```

### Step 2: Test Firebase Connection

```bash
python3 test_firebase_config.py
```

**Expected output:**
```
✅ Firebase Admin SDK initialized successfully
✅ Firestore client created successfully
✅ Firestore connection working
```

### Step 3: Test Gemini API

```bash
python3 -c "
import os
from dotenv import load_dotenv
load_dotenv()

import google.generativeai as genai
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))

model = genai.GenerativeModel('gemini-1.5-flash')
response = model.generate_content('Test connection')
print(f'✅ Gemini API working: {response.text[:50]}...')
"
```

### Step 4: Test Application Startup

**⚠️ IMPORTANT: Import Issues Detected & Fixed**

The application had import path issues that have been resolved. Here are the working test methods:

**Test basic Flask functionality:**
```bash
# Test minimal functionality (guaranteed to work)
python3 test_minimal_app.py
```

**Expected output:**
```
🧪 Testing minimal Flask app...
✅ Minimal app created successfully
✅ Health endpoint: 200
✅ Test endpoint: 200
🎉 Minimal app test passed!
```

**Test with production server (recommended for deployment):**
```bash
# Test with gunicorn (production server)
gunicorn --bind 0.0.0.0:5000 wsgi:app --timeout 30
```

**Alternative: Test full application (after fixing Gemini API):**
```bash
# Full application test (requires valid Gemini API key)
python3 test_startup.py
```

### Step 5: Test API Endpoints

**Start the minimal server for testing:**
```bash
# Health check
curl http://localhost:5000/api/v1/health

# Test endpoint
curl http://localhost:5000/api/v1/test
```

**Expected responses:**
```json
// Health endpoint
{
  "status": "healthy",
  "message": "RetailGenie Backend is running",
  "timestamp": "2025-07-02"
}

// Test endpoint  
{
  "message": "Test endpoint working",
  "app_name": "test_minimal_app"
}
```

**🚨 Advanced Features Status:**
- ✅ **Basic Flask**: Working perfectly
- ✅ **Environment**: Configured correctly  
- ✅ **Firebase**: Connection tested and working
- ❌ **Gemini API**: Expired key (needs renewal)
- ⚠️ **AI Routes**: Import issues resolved, needs Gemini key
- ✅ **Production Server**: Gunicorn ready

---

## 🌐 Platform-Specific Deployment

### Render.com (Recommended)

**Why Render?** Easy deployment, automatic HTTPS, good free tier, excellent for Python apps.

#### Step 1: Prepare for Render

**Create `render.yaml`:**
```yaml
services:
  - type: web
    name: retailgenie-backend
    env: python
    buildCommand: "pip install -r requirements.txt"
    startCommand: "gunicorn wsgi:app"
    envVars:
      - key: PYTHON_VERSION
        value: 3.12.1
      - key: FLASK_ENV
        value: production
      - key: FLASK_DEBUG
        value: false
```

#### Step 2: Deploy to Render

1. **Create Render Account:**
   - Go to [render.com](https://render.com)
   - Sign up with GitHub account

2. **Connect Repository:**
   - Click "New +" → "Web Service"
   - Connect your GitHub repository
   - Select the repository containing your backend

3. **Configure Service:**
   ```
   Name: retailgenie-backend
   Environment: Python 3
   Build Command: pip install -r requirements.txt
   Start Command: gunicorn wsgi:app
   ```

4. **Set Environment Variables:**
   - In Render dashboard, go to "Environment"
   - Add all variables from your `.env` file:
   ```
   SECRET_KEY=your-secret-key
   JWT_SECRET=your-jwt-secret
   FIREBASE_PROJECT_ID=retailgenie-production
   FIREBASE_PRIVATE_KEY=your-private-key
   FIREBASE_CLIENT_EMAIL=your-service-account-email
   GEMINI_API_KEY=your-gemini-api-key
   GEMINI_MODEL=gemini-1.5-flash
   CORS_ORIGINS=https://your-render-url.onrender.com
   ```

5. **Deploy:**
   - Click "Create Web Service"
   - Wait for deployment (5-10 minutes)
   - Your app will be available at `https://your-service-name.onrender.com`

#### Step 3: Configure Custom Domain (Optional)

1. **In Render Dashboard:**
   - Go to "Settings" → "Custom Domains"
   - Add your domain: `api.yourdomain.com`

2. **Update DNS:**
   - Add CNAME record: `api` → `your-service-name.onrender.com`

3. **Update CORS:**
   ```
   CORS_ORIGINS=https://yourdomain.com,https://api.yourdomain.com
   ```

---

### Heroku

**Great for quick deployment with add-ons for Redis, databases, etc.**

#### Step 1: Install Heroku CLI

```bash
# macOS
brew install heroku/brew/heroku

# Ubuntu/Debian
curl https://cli-assets.heroku.com/install.sh | sh
```

#### Step 2: Prepare for Heroku

**Create `runtime.txt`:**
```txt
python-3.12.1
```

**Update `Procfile`:**
```
web: gunicorn wsgi:app
worker: celery -A celery_app worker --loglevel=info
```

#### Step 3: Deploy to Heroku

```bash
# Login to Heroku
heroku login

# Create Heroku app
heroku create retailgenie-backend

# Set environment variables
heroku config:set FLASK_ENV=production
heroku config:set FLASK_DEBUG=False
heroku config:set SECRET_KEY="your-secret-key"
heroku config:set JWT_SECRET="your-jwt-secret"
heroku config:set FIREBASE_PROJECT_ID="retailgenie-production"
heroku config:set FIREBASE_PRIVATE_KEY="your-private-key"
heroku config:set FIREBASE_CLIENT_EMAIL="your-service-account-email"
heroku config:set GEMINI_API_KEY="your-gemini-api-key"
heroku config:set GEMINI_MODEL="gemini-1.5-flash"

# Deploy
git add .
git commit -m "Deploy to Heroku"
git push heroku main

# Scale the app
heroku ps:scale web=1
```

#### Step 4: Add Redis (Optional)

```bash
# Add Redis addon
heroku addons:create heroku-redis:mini

# Redis URL will be automatically added to environment
```

---

### Railway

**Modern platform with excellent developer experience.**

#### Step 1: Deploy to Railway

1. **Visit [railway.app](https://railway.app)**
2. **Sign up with GitHub**
3. **Click "Deploy from GitHub repo"**
4. **Select your repository**

#### Step 2: Configure Environment

1. **In Railway dashboard:**
   - Go to "Variables" tab
   - Add all environment variables from your `.env` file

2. **Configure Build:**
   ```bash
   # Railway auto-detects Python
   # Build Command: pip install -r requirements.txt
   # Start Command: gunicorn wsgi:app
   ```

#### Step 3: Custom Domain

1. **In Railway dashboard:**
   - Go to "Settings" → "Domains"
   - Add custom domain
   - Update DNS records as shown

---

### Google Cloud Run

**Serverless container platform, scales to zero, pay-per-use.**

#### Step 1: Create Dockerfile

```dockerfile
FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8080

CMD exec gunicorn --bind :8080 --workers 1 --threads 8 --timeout 0 wsgi:app
```

#### Step 2: Build and Deploy

```bash
# Install Google Cloud CLI
curl https://sdk.cloud.google.com | bash

# Initialize
gcloud init

# Set project
gcloud config set project your-project-id

# Enable Cloud Run API
gcloud services enable run.googleapis.com

# Build and deploy
gcloud run deploy retailgenie-backend \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

#### Step 3: Set Environment Variables

```bash
gcloud run services update retailgenie-backend \
  --set-env-vars="FLASK_ENV=production,FLASK_DEBUG=False,SECRET_KEY=your-secret-key" \
  --region=us-central1
```

---

### AWS EC2/Elastic Beanstalk

#### Option A: Elastic Beanstalk (Easier)

1. **Install EB CLI:**
```bash
pip install awsebcli
```

2. **Initialize and Deploy:**
```bash
eb init -p python-3.9 retailgenie-backend
eb create production
eb setenv FLASK_ENV=production FLASK_DEBUG=False SECRET_KEY=your-secret-key
eb deploy
```

#### Option B: EC2 Instance (More Control)

1. **Launch EC2 Instance:**
   - Choose Ubuntu 20.04 LTS
   - t3.micro for testing (t3.small+ for production)
   - Configure security groups (HTTP/HTTPS)

2. **Connect and Setup:**
```bash
ssh -i your-key.pem ubuntu@your-ec2-ip

# Update system
sudo apt update && sudo apt upgrade -y

# Install Python and dependencies
sudo apt install python3-pip python3-venv nginx supervisor -y

# Clone your repository
git clone https://github.com/yourusername/RetailGenie.git
cd RetailGenie/backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install gunicorn
```

3. **Configure Nginx:**
```bash
sudo nano /etc/nginx/sites-available/retailgenie
```

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

```bash
sudo ln -s /etc/nginx/sites-available/retailgenie /etc/nginx/sites-enabled
sudo nginx -t
sudo systemctl restart nginx
```

4. **Configure Supervisor:**
```bash
sudo nano /etc/supervisor/conf.d/retailgenie.conf
```

```ini
[program:retailgenie]
command=/home/ubuntu/RetailGenie/backend/venv/bin/gunicorn wsgi:app
directory=/home/ubuntu/RetailGenie/backend
user=ubuntu
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/retailgenie.log
environment=FLASK_ENV=production,SECRET_KEY="your-secret-key"
```

```bash
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start retailgenie
```

---

### VPS/DigitalOcean

**Similar to EC2 but often simpler and cheaper.**

#### Step 1: Create Droplet

1. **Create DigitalOcean Account**
2. **Create Droplet:**
   - Ubuntu 20.04 LTS
   - Basic plan ($6/month minimum)
   - Add SSH key

#### Step 2: Setup Server

```bash
# Connect to your droplet
ssh root@your-droplet-ip

# Create user
adduser retailgenie
usermod -aG sudo retailgenie
su - retailgenie

# Install dependencies
sudo apt update && sudo apt upgrade -y
sudo apt install python3-pip python3-venv nginx supervisor git -y

# Clone and setup application
git clone https://github.com/yourusername/RetailGenie.git
cd RetailGenie/backend

python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install gunicorn
```

#### Step 3: Configure Production Environment

```bash
# Create production environment file
cp .env .env.production

# Edit with production values
nano .env.production
```

**Update with your production values:**
```bash
FLASK_ENV=production
FLASK_DEBUG=False
CORS_ORIGINS=https://yourdomain.com
```

#### Step 4: Setup Nginx and Supervisor

**Follow the same Nginx and Supervisor configuration as in the EC2 section above.**

#### Step 5: Setup SSL with Let's Encrypt

```bash
sudo apt install certbot python3-certbot-nginx -y
sudo certbot --nginx -d yourdomain.com
```

---

## 🔧 Post-Deployment Configuration

### Step 1: Test Deployed Application

```bash
# Test health endpoint
curl https://your-deployed-url.com/api/v1/health

# Test AI chat
curl -X POST https://your-deployed-url.com/api/v1/ai/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello from production!"}'

# Test Firebase connection
curl https://your-deployed-url.com/api/v1/products
```

### Step 2: Update Frontend Configuration

**Update your frontend to use the production API:**

```javascript
// In your frontend config
const API_BASE_URL = 'https://your-deployed-url.com/api/v1';
```

### Step 3: Configure Custom Domain DNS

**If using a custom domain, update DNS records:**

```
Type: CNAME
Name: api
Value: your-platform-url.com
TTL: 300
```

### Step 4: Setup Monitoring

#### Basic Monitoring Script

```python
# monitoring/health_check.py
import requests
import time

def check_health():
    try:
        response = requests.get('https://your-deployed-url.com/api/v1/health')
        if response.status_code == 200:
            print(f"✅ Service healthy at {time.strftime('%Y-%m-%d %H:%M:%S')}")
        else:
            print(f"⚠️ Service unhealthy: {response.status_code}")
    except Exception as e:
        print(f"❌ Service down: {e}")

if __name__ == "__main__":
    check_health()
```

#### Setup Cron Job for Monitoring

```bash
# Add to crontab
crontab -e

# Check every 5 minutes
*/5 * * * * /path/to/python /path/to/health_check.py >> /var/log/health_check.log
```

---

## 📊 Monitoring & Maintenance

### Application Monitoring

#### Log Monitoring

**For cloud platforms (Render/Heroku):**
- Use platform-provided logging
- Set up log alerts for errors

**For VPS deployment:**
```bash
# View application logs
tail -f /var/log/retailgenie.log

# View Nginx logs
tail -f /var/log/nginx/access.log
tail -f /var/log/nginx/error.log
```

#### Performance Monitoring

**Add basic metrics to your application:**

```python
# In your Flask app
import time
from flask import request

@app.before_request
def before_request():
    request.start_time = time.time()

@app.after_request
def after_request(response):
    duration = time.time() - request.start_time
    if duration > 2.0:  # Log slow requests
        app.logger.warning(f"Slow request: {request.path} took {duration:.2f}s")
    return response
```

### Database Monitoring

**Monitor Firebase usage:**
- Go to Firebase Console → Usage tab
- Monitor read/write operations
- Set up billing alerts

### API Usage Monitoring

**Monitor Gemini API usage:**
- Go to Google AI Studio → Usage
- Check quota and billing
- Set up usage alerts

### Backup Strategy

#### Code Backup
- Use Git with remote repositories
- Tag releases: `git tag v1.0.0`

#### Environment Variables Backup
```bash
# Create secure backup of environment variables
# (Remove sensitive data before storing)
cp .env .env.backup.$(date +%Y%m%d)
```

### Update Process

#### 1. Test Updates Locally
```bash
# Pull latest changes
git pull origin main

# Test locally
python3 app.py

# Run tests
python3 -m pytest tests/
```

#### 2. Deploy Updates

**For Git-based platforms (Render/Railway/Heroku):**
```bash
git add .
git commit -m "Update: description of changes"
git push origin main
# Platform will auto-deploy
```

**For VPS deployment:**
```bash
# SSH to server
ssh user@your-server

# Pull updates
cd RetailGenie/backend
git pull origin main

# Restart application
sudo supervisorctl restart retailgenie
```

---

## 🚨 Troubleshooting

### Common Issues and Solutions

#### 1. Application Won't Start

**Error:** `ModuleNotFoundError: No module named 'xxx'`

**Solution:**
```bash
# Ensure all dependencies are installed
pip install -r requirements.txt

# Check Python version compatibility
python3 --version
```

#### 2. Firebase Connection Issues

**Error:** `Firebase Admin SDK initialization failed`

**Solution:**
```bash
# Verify environment variables
echo $FIREBASE_PROJECT_ID
echo $FIREBASE_CLIENT_EMAIL

# Check private key format (should have \n characters)
echo $FIREBASE_PRIVATE_KEY | head -c 50
```

#### 3. Gemini API Issues

**Error:** `API key invalid` or `Quota exceeded`

**Solution:**
```bash
# Verify API key
curl -H "x-goog-api-key: $GEMINI_API_KEY" \
  "https://generativelanguage.googleapis.com/v1beta/models"

# Check quota in Google AI Studio
```

#### 4. CORS Issues

**Error:** `Access-Control-Allow-Origin` errors

**Solution:**
```python
# Update CORS_ORIGINS in .env
CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com

# Or allow all origins for testing (NOT for production)
CORS_ORIGINS=*
```

#### 5. 502 Bad Gateway (Nginx)

**Check application is running:**
```bash
sudo supervisorctl status retailgenie
curl http://localhost:5000/api/v1/health
```

**Check Nginx configuration:**
```bash
sudo nginx -t
sudo systemctl restart nginx
```

#### 6. Memory Issues

**For limited memory environments:**
```python
# In wsgi.py, reduce worker memory usage
# Use fewer workers: gunicorn --workers 1 wsgi:app
```

### Emergency Recovery

#### 1. Rollback Deployment

**Git-based platforms:**
```bash
git revert HEAD
git push origin main
```

**VPS deployment:**
```bash
# Rollback to previous commit
git reset --hard HEAD~1
sudo supervisorctl restart retailgenie
```

#### 2. Check Service Status

```bash
# Check if service is running
curl https://your-domain.com/api/v1/health

# Check logs for errors
tail -n 50 /var/log/retailgenie.log
```

#### 3. Restore from Backup

```bash
# Restore environment variables
cp .env.backup.YYYYMMDD .env

# Restart application
sudo supervisorctl restart retailgenie
```

---

## 🎉 Deployment Success Checklist

### Final Verification

- [ ] ✅ Application starts without errors
- [ ] ✅ Health endpoint responds: `/api/v1/health`
- [ ] ✅ AI chat endpoint works: `/api/v1/ai/chat`
- [ ] ✅ Firebase connection established
- [ ] ✅ Gemini API responding
- [ ] ✅ CORS configured for your domain
- [ ] ✅ HTTPS enabled
- [ ] ✅ Custom domain working (if configured)
- [ ] ✅ Monitoring setup
- [ ] ✅ Backup strategy in place
- [ ] ✅ Error logging configured

### Performance Optimization

- [ ] ✅ Production environment variables set
- [ ] ✅ Debug mode disabled
- [ ] ✅ Gunicorn configured with appropriate workers
- [ ] ✅ Static files served efficiently
- [ ] ✅ Database connections optimized
- [ ] ✅ Caching enabled (if using Redis)

### Security Checklist

- [ ] ✅ Strong SECRET_KEY and JWT_SECRET
- [ ] ✅ Environment variables secured
- [ ] ✅ HTTPS enforced
- [ ] ✅ CORS properly configured
- [ ] ✅ Rate limiting enabled
- [ ] ✅ Input validation in place
- [ ] ✅ Error messages don't expose sensitive data

---

## 🚀 Congratulations!

Your **RetailGenie AI-Powered Backend** is now successfully deployed and running in production! 

### What You've Achieved

🎯 **Deployed a full-featured AI retail platform** with:
- Intelligent shopping assistant
- Advanced analytics and reporting
- Real-time inventory management
- Dynamic pricing optimization
- Gamification and loyalty systems
- Secure authentication and authorization

### Next Steps

1. **Connect Your Frontend** - Update frontend configuration to use your production API
2. **Monitor Performance** - Keep an eye on logs and performance metrics
3. **Scale as Needed** - Upgrade server resources as your user base grows
4. **Add Features** - Continue enhancing your platform with new capabilities

### Support Resources

- **Documentation**: Keep this guide for future deployments
- **Monitoring**: Set up alerts for critical issues
- **Backups**: Regular backups of code and configuration
- **Updates**: Plan regular updates and security patches

Your AI-powered retail management system is now live and ready to serve customers! 🎊

---

**Happy Deploying! 🚀**
