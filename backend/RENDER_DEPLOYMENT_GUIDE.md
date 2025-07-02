# Render Deployment Guide for RetailGenie Backend

## Step-by-Step Deployment Process

### 1. Fix Gunicorn Import Error ✅ COMPLETED
- **Issue**: `Failed to find attribute 'app' in 'wsgi'`
- **Solution**: Added `app = create_app()` at module level in `wsgi.py`
- **Status**: Fixed in the current code

### 2. Firebase Configuration Options

You have three options for Firebase in production:

#### Option A: Use Mock Database (Simplest)
- No additional configuration needed
- The app will automatically fall back to mock database
- Good for testing deployment without Firebase setup

#### Option B: Environment Variables (Recommended)
Set these environment variables in Render:

```bash
FIREBASE_PROJECT_ID=your-project-id
FIREBASE_PRIVATE_KEY_ID=your-private-key-id
FIREBASE_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----\nYour-Private-Key-Here\n-----END PRIVATE KEY-----\n"
FIREBASE_CLIENT_EMAIL=your-service-account@your-project.iam.gserviceaccount.com
FIREBASE_CLIENT_ID=your-client-id
FIREBASE_CLIENT_CERT_URL=https://www.googleapis.com/robot/v1/metadata/x509/your-service-account%40your-project.iam.gserviceaccount.com
```

#### Option C: Service Account File
1. Upload your Firebase service account JSON file to Render
2. Set environment variable: `FIREBASE_CREDENTIALS_PATH=/path/to/service-account.json`

### 3. Environment Variables to Set in Render

#### Required:
```bash
FLASK_ENV=production
FLASK_DEBUG=False
SECRET_KEY=your-very-secure-secret-key
```

#### Optional (with defaults):
```bash
PORT=5000
HOST=0.0.0.0
CORS_ORIGINS=https://yourdomain.com
```

### 4. Deploy Commands

Your `render.yaml` is already configured correctly:
```yaml
services:
  - type: web
    name: retailgenie-backend
    env: python
    buildCommand: "pip install -r requirements.txt"
    startCommand: "gunicorn wsgi:app"
```

### 5. Verification Steps

After deployment, test these endpoints:
1. `https://your-app.onrender.com/health` - Should return health status
2. `https://your-app.onrender.com/api/info` - Should return API information

### 6. Common Troubleshooting

#### Import Errors:
- Check that all dependencies are in `requirements.txt`
- Verify Python path configuration in `wsgi.py`

#### Firebase Errors:
- If using Option B, ensure all Firebase environment variables are set correctly
- If using Option C, verify the file path is correct
- Option A (mock) should work without any Firebase configuration

#### Port/Host Issues:
- Render automatically sets `PORT` environment variable
- Make sure your app listens on `0.0.0.0` not `127.0.0.1`

### 7. Current Status

✅ **Fixed Issues:**
- Gunicorn can now find the `app` object in `wsgi.py`
- Python path configuration corrected
- Firebase fallback to mock database implemented

🔄 **Next Steps:**
1. Choose Firebase configuration option (A, B, or C)
2. Set required environment variables in Render
3. Deploy and test

### 8. Quick Test Commands

Test locally before deploying:
```bash
# Test wsgi import
cd /workspaces/RetailGenie/backend
python3 -c "import wsgi; print('✅ WSGI import successful')"

# Test gunicorn config
python3 -m gunicorn --check-config wsgi:app

# Test app creation
python3 -c "from wsgi import app; print(f'✅ App: {app.name}')"
```

All tests should pass before deploying to Render.
