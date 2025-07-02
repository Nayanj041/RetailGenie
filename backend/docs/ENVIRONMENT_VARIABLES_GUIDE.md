# Environment Variables Setup Guide

This guide provides detailed instructions on how to obtain and configure all required environment variables for the RetailGenie backend.

## Table of Contents
1. [Flask Configuration](#flask-configuration)
2. [Firebase Configuration](#firebase-configuration)
3. [Google Gemini Configuration](#google-gemini-configuration)
4. [Email Configuration (SMTP)](#email-configuration-smtp)
5. [Redis Configuration](#redis-configuration)
6. [JWT Configuration](#jwt-configuration)
7. [Development vs Production Values](#development-vs-production-values)
8. [Quick Setup Checklist](#quick-setup-checklist)

---

## Flask Configuration

### `SECRET_KEY`
**Purpose**: Used for session security and CSRF protection.

**How to generate**:
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

**Example**: `SECRET_KEY=a1b2c3d4e5f6789012345678901234567890abcdef1234567890abcdef123456`

### `FLASK_ENV` and `FLASK_DEBUG`
**Values**:
- Development: `FLASK_ENV=development`, `FLASK_DEBUG=True`
- Production: `FLASK_ENV=production`, `FLASK_DEBUG=False`

---

## Firebase Configuration

### Step 1: Create a Firebase Project
1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Click "Add project"
3. Enter project name (e.g., "retailgenie-app")
4. Choose whether to enable Google Analytics
5. Click "Create project"

### Step 2: Enable Required Services
1. **Firestore Database**:
   - Go to "Firestore Database" in the left sidebar
   - Click "Create database"
   - Choose "Start in test mode" for development
   - Select a location (choose closest to your users)

2. **Authentication**:
   - Go to "Authentication" in the left sidebar
   - Click "Get started"
   - Go to "Sign-in method" tab
   - Enable "Email/Password" provider

### Step 3: Create Service Account
1. Go to Project Settings (gear icon)
2. Click "Service accounts" tab
3. Click "Generate new private key"
4. Download the JSON file

### Step 4: Extract Firebase Environment Variables
From the downloaded JSON file, extract these values:

```env
FIREBASE_PROJECT_ID=your-project-id-here
FIREBASE_PRIVATE_KEY_ID=the-private-key-id-from-json
FIREBASE_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----\nthe-private-key-from-json\n-----END PRIVATE KEY-----\n"
FIREBASE_CLIENT_EMAIL=firebase-adminsdk-xxxxx@your-project.iam.gserviceaccount.com
FIREBASE_CLIENT_ID=the-client-id-from-json
FIREBASE_AUTH_URI=https://accounts.google.com/o/oauth2/auth
FIREBASE_TOKEN_URI=https://oauth2.googleapis.com/token
```

**Important**: The private key must include the `\n` characters and be wrapped in quotes.

---

## Google Gemini Configuration

### Step 1: Get Gemini API Key
1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with your Google account
3. Click "Create API Key"
4. Choose "Create API key in new project" or select existing project
5. Copy the generated API key

### Step 2: Configure Gemini Variables
```env
GEMINI_API_KEY=AIzaSyC_your_actual_api_key_here
GEMINI_MODEL=gemini-pro
```

**Available Models**:
- `gemini-pro` - Best for text generation and reasoning
- `gemini-pro-vision` - For multimodal (text + images)
- `gemini-1.5-pro` - Latest version with larger context

**Cost Considerations**:
- Gemini Pro has a generous free tier
- Check current pricing at [Google AI Pricing](https://ai.google.dev/pricing)

---

## Email Configuration (SMTP)

### Option 1: Gmail (Recommended for Development)

#### Step 1: Enable 2-Factor Authentication
1. Go to [Google Account Settings](https://myaccount.google.com/)
2. Click "Security"
3. Enable "2-Step Verification"

#### Step 2: Generate App Password
1. In Google Account Security settings
2. Click "App passwords"
3. Select "Mail" and "Other (custom name)"
4. Enter "RetailGenie Backend"
5. Copy the generated 16-character password

#### Step 3: Configure Email Variables
```env
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SENDER_EMAIL=nayanj041@gmail.com
SENDER_PASSWORD=your-16-character-app-password
ADMIN_EMAIL=admin@yourdomain.com
```

### Option 2: SendGrid (Recommended for Production)

#### Step 1: Create SendGrid Account
1. Go to [SendGrid](https://sendgrid.com/)
2. Sign up for free account (100 emails/day free)
3. Verify your email address

#### Step 2: Create API Key
1. Go to Settings → API Keys
2. Click "Create API Key"
3. Choose "Restricted Access"
4. Give permissions for "Mail Send" and "Template Engine"
5. Copy the API key

#### Step 3: Configure for SendGrid
```env
SMTP_SERVER=smtp.sendgrid.net
SMTP_PORT=587
SENDER_EMAIL=noreply@yourdomain.com
SENDER_PASSWORD=your-sendgrid-api-key
ADMIN_EMAIL=admin@yourdomain.com
```

### Option 3: Other Providers

**Mailgun**:
```env
SMTP_SERVER=smtp.mailgun.org
SMTP_PORT=587
SENDER_EMAIL=noreply@yourdomain.com
SENDER_PASSWORD=your-mailgun-smtp-password
```

**AWS SES**:
```env
SMTP_SERVER=email-smtp.us-east-1.amazonaws.com
SMTP_PORT=587
SENDER_EMAIL=noreply@yourdomain.com
SENDER_PASSWORD=your-ses-smtp-password
```

---

## Redis Configuration

### Option 1: Local Redis (Development)

#### Install Redis
**Ubuntu/Debian**:
```bash
sudo apt update
sudo apt install redis-server
sudo systemctl start redis-server
sudo systemctl enable redis-server
```

**macOS**:
```bash
brew install redis
brew services start redis
```

**Configuration**:
```env
REDIS_URL=redis://localhost:6379/0
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0
```

### Option 2: Redis Cloud (Production)

#### Step 1: Create Redis Cloud Account
1. Go to [Redis Cloud](https://redis.com/redis-enterprise-cloud/)
2. Sign up for free account
3. Create new database

#### Step 2: Get Connection Details
1. Go to database details
2. Copy the connection string
3. Note the host, port, and password

#### Step 3: Configure
```env
REDIS_URL=redis://username:password@host:port/0
CELERY_BROKER_URL=redis://username:password@host:port/0
CELERY_RESULT_BACKEND=redis://username:password@host:port/0
```

### Option 3: Heroku Redis (if deploying to Heroku)
```env
REDIS_URL=${REDIS_URL}  # Automatically provided by Heroku
CELERY_BROKER_URL=${REDIS_URL}
CELERY_RESULT_BACKEND=${REDIS_URL}
```

---

## JWT Configuration

### Generate JWT Secret
```bash
python -c "import secrets; print(secrets.token_urlsafe(64))"
```

```env
JWT_SECRET=your-generated-jwt-secret-here
```

**Important**: Use a different secret than your Flask SECRET_KEY.

---

## Development vs Production Values

### Development Environment (.env)
```env
FLASK_ENV=development
FLASK_DEBUG=True
CORS_ORIGINS=http://localhost:3000,http://localhost:3001
CACHE_TYPE=simple
RATELIMIT_STORAGE_URL=memory://
DATABASE_URL=firebase
```

### Production Environment
```env
FLASK_ENV=production
FLASK_DEBUG=False
CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
CACHE_TYPE=redis
RATELIMIT_STORAGE_URL=redis://your-redis-url
DATABASE_URL=firebase
```

---

## Quick Setup Checklist

### Essential for Basic Functionality
- [ ] `SECRET_KEY` - Generate random secret
- [ ] `JWT_SECRET` - Generate random secret  
- [ ] `FIREBASE_PROJECT_ID` - From Firebase console
- [ ] `FIREBASE_PRIVATE_KEY` - From service account JSON
- [ ] `FIREBASE_CLIENT_EMAIL` - From service account JSON
- [ ] `GEMINI_API_KEY` - From Google AI Studio

### Required for Email Features
- [ ] `SMTP_SERVER` - Email provider SMTP server
- [ ] `SMTP_PORT` - Usually 587 for TLS
- [ ] `SENDER_EMAIL` - Your sending email address
- [ ] `SENDER_PASSWORD` - App password or API key
- [ ] `ADMIN_EMAIL` - Where admin notifications go

### Required for Background Tasks
- [ ] `REDIS_URL` - Redis connection string
- [ ] `CELERY_BROKER_URL` - Usually same as Redis URL
- [ ] `CELERY_RESULT_BACKEND` - Usually same as Redis URL

### Optional but Recommended
- [ ] `CORS_ORIGINS` - Frontend domains
- [ ] `RATELIMIT_DEFAULT` - API rate limiting
- [ ] `SLOW_REQUEST_THRESHOLD` - Performance monitoring

---

## Testing Your Configuration

### 1. Test Firebase Connection
```bash
cd /workspaces/RetailGenie/backend
python -c "
from app.utils.firebase_utils import FirebaseManager
fm = FirebaseManager()
print('Firebase connection successful!')
"
```

### 2. Test Gemini API
```bash
python test_gemini.py
```

### 3. Test Email Configuration
```bash
python -c "
from app.utils.email_utils import send_email
send_email('test@example.com', 'Test', 'Email configuration works!')
print('Email configuration successful!')
"
```

### 4. Test Redis Connection
```bash
python -c "
import redis
import os
r = redis.from_url(os.getenv('REDIS_URL', 'redis://localhost:6379/0'))
r.ping()
print('Redis connection successful!')
"
```

---

## Common Issues and Solutions

### Firebase Issues
**Error**: "Invalid private key format"
**Solution**: Ensure private key includes `\n` characters and is wrapped in quotes

**Error**: "Project not found"
**Solution**: Check FIREBASE_PROJECT_ID matches your Firebase project ID

### Gemini Issues
**Error**: "API key not valid"
**Solution**: Regenerate API key and ensure no extra spaces

**Error**: "Quota exceeded"
**Solution**: Check usage in Google AI Studio, upgrade if needed

### Email Issues
**Error**: "Authentication failed"
**Solution**: For Gmail, ensure 2FA is enabled and use app password, not regular password

**Error**: "Connection refused"
**Solution**: Check SMTP_SERVER and SMTP_PORT are correct for your provider

### Redis Issues
**Error**: "Connection refused"
**Solution**: Ensure Redis server is running locally or check cloud Redis credentials

---

## Security Best Practices

1. **Never commit .env files** - Add `.env` to `.gitignore`
2. **Use different secrets** for development and production
3. **Rotate secrets regularly** - Especially for production
4. **Use environment-specific configs** - Different Redis/SMTP for dev/prod
5. **Monitor API usage** - Keep track of Gemini API usage and costs
6. **Use HTTPS in production** - All external services should use HTTPS
7. **Limit CORS origins** - Only allow trusted frontend domains

---

## Getting Help

If you encounter issues:

1. Check the logs: `tail -f logs/app.log`
2. Test individual components using the testing commands above
3. Verify all required environment variables are set
4. Check service status (Firebase, Redis, email provider)
5. Review the specific error messages for clues

For service-specific help:
- [Firebase Documentation](https://firebase.google.com/docs)
- [Google AI Studio Help](https://ai.google.dev/docs)
- [Redis Documentation](https://redis.io/documentation)
- [Flask Configuration](https://flask.palletsprojects.com/en/2.3.x/config/)
