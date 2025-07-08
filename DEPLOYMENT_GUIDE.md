# 🚀 RetailGenie Complete Deployment Guide

## 📋 Quick Start Deployment

### Step 1: Prepare for Deployment

1. **Update Backend for Production Security**:
   ```bash
   cd /workspaces/RetailGenie/backend
   
   # Update Procfile to use production WSGI
   echo "web: gunicorn wsgi_production:app" > Procfile
   ```

2. **Create Environment Variables File**:
   ```bash
   # Save these environment variables for Render deployment
   cat > .env.render << EOF
   FLASK_ENV=production
   FLASK_DEBUG=false
   SECRET_KEY=your-super-secure-secret-key-$(openssl rand -hex 32)
   JWT_SECRET=your-jwt-secret-key-$(openssl rand -hex 32)
   
   # Firebase Configuration (from your Firebase console)
   FIREBASE_PROJECT_ID=retailgenie-production
   FIREBASE_PRIVATE_KEY_ID=your-private-key-id
   FIREBASE_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----\nYour-Private-Key-Here\n-----END PRIVATE KEY-----"
   FIREBASE_CLIENT_EMAIL=firebase-adminsdk-xxxxx@retailgenie-production.iam.gserviceaccount.com
   FIREBASE_CLIENT_ID=your-client-id
   
   # CORS Origins (update with your frontend URL after deployment)
   CORS_ORIGINS=https://your-frontend-domain.com,https://www.your-frontend-domain.com
   
   # Optional: Gemini API for AI features
   GEMINI_API_KEY=your-gemini-api-key
   EOF
   ```

### Step 2: Deploy Backend to Render

1. **Push to GitHub** (if not already done):
   ```bash
   git add .
   git commit -m "Production ready deployment"
   git push origin main
   ```

2. **Deploy on Render**:
   - Go to [Render Dashboard](https://dashboard.render.com)
   - Click "New +" → "Web Service"
   - Connect your GitHub repository: `RetailGenie`
   - Configure:
     ```
     Name: retailgenie-backend
     Environment: Python 3
     Build Command: pip install -r requirements.txt
     Start Command: gunicorn wsgi_production:app
     ```

3. **Set Environment Variables** in Render:
   - Copy all variables from `.env.render` file
   - Add them one by one in Render's Environment Variables section

4. **Deploy and Test**:
   - Click "Create Web Service"
   - Wait for deployment to complete
   - Test: `https://your-app-name.onrender.com/api/v1/health`

### Step 3: Deploy Frontend

#### Option A: Deploy to Render (Static Site)

1. **Update Frontend Configuration**:
   ```bash
   cd /workspaces/RetailGenie/frontend
   
   # Create production environment file
   echo "REACT_APP_API_URL=https://your-backend-url.onrender.com" > .env.production
   ```

2. **Deploy on Render**:
   - New → "Static Site"
   - Connect same GitHub repository
   - Configure:
     ```
     Name: retailgenie-frontend
     Build Command: cd frontend && npm install && npm run build
     Publish Directory: frontend/build
     ```

#### Option B: Deploy to Netlify

1. **Build locally**:
   ```bash
   cd frontend
   echo "REACT_APP_API_URL=https://your-backend-url.onrender.com" > .env.production
   npm run build
   ```

2. **Deploy**:
   - Go to [Netlify](https://netlify.com)
   - Drag and drop the `build/` folder

### Step 4: Update CORS Configuration

1. **Get your frontend URL** (from Render/Netlify)
2. **Update Backend Environment Variables** in Render:
   ```
   CORS_ORIGINS=https://your-frontend-url.netlify.app,https://your-frontend-url.onrender.com
   ```
3. **Redeploy backend** if needed

### Step 5: Final Testing

1. **Test Backend**:
   ```bash
   curl https://your-backend.onrender.com/api/v1/health
   ```

2. **Test Frontend**:
   - Visit your frontend URL
   - Try demo login: `demo@retailgenie.com` / `demo123456`
   - Verify dashboard access

---

## 🔧 Detailed Configuration

### Environment Variables Reference

#### Required for Production:
- `SECRET_KEY`: Flask session secret (generate with `openssl rand -hex 32`)
- `JWT_SECRET`: JWT signing key (generate with `openssl rand -hex 32`)
- `FIREBASE_PROJECT_ID`: Your Firebase project ID
- `FIREBASE_PRIVATE_KEY_ID`: From Firebase service account JSON
- `FIREBASE_PRIVATE_KEY`: From Firebase service account JSON (keep quotes and newlines)
- `FIREBASE_CLIENT_EMAIL`: From Firebase service account JSON
- `FIREBASE_CLIENT_ID`: From Firebase service account JSON

#### Optional:
- `CORS_ORIGINS`: Comma-separated list of allowed origins
- `GEMINI_API_KEY`: For AI features
- `PORT`: Server port (default: 5000)

### Firebase Setup

1. **Download Service Account Key**:
   - Go to Firebase Console → Project Settings → Service Accounts
   - Generate new private key
   - Download JSON file

2. **Extract Environment Variables**:
   ```bash
   # From the downloaded JSON file, extract:
   FIREBASE_PROJECT_ID=project_id
   FIREBASE_PRIVATE_KEY_ID=private_key_id
   FIREBASE_PRIVATE_KEY=private_key (with \n preserved)
   FIREBASE_CLIENT_EMAIL=client_email
   FIREBASE_CLIENT_ID=client_id
   ```

---

## 🎯 Production Checklist

### Pre-Deployment:
- [ ] Environment variables configured securely
- [ ] Firebase service account properly set up
- [ ] CORS origins updated for production domains
- [ ] Secret keys generated (not using defaults)
- [ ] Frontend built with production API URL

### Post-Deployment:
- [ ] Health endpoint responding: `/api/v1/health`
- [ ] Authentication working: login/register
- [ ] Products endpoint working: `/api/v1/products`
- [ ] Frontend-backend communication working
- [ ] Demo login working end-to-end

### Security Verification:
- [ ] No hard-coded secrets in code
- [ ] HTTPS enabled (automatic on Render)
- [ ] CORS properly configured
- [ ] JWT tokens working
- [ ] Password hashing verified

---

## 🚨 Troubleshooting

### Common Issues:

1. **"Firebase not initialized"**:
   - Check `FIREBASE_*` environment variables
   - Verify private key format (keep \n characters)

2. **CORS errors**:
   - Update `CORS_ORIGINS` with your frontend URL
   - Redeploy backend after CORS changes

3. **Build failures**:
   - Check requirements.txt has all dependencies
   - Verify Python version in runtime.txt

4. **Authentication not working**:
   - Check JWT_SECRET is set
   - Verify frontend API URL points to backend

### Debug Commands:

```bash
# Test backend health
curl https://your-backend.onrender.com/api/v1/health

# Test authentication
curl -X POST -H "Content-Type: application/json" \
     -d '{"email":"demo@retailgenie.com","password":"demo123456"}' \
     https://your-backend.onrender.com/api/v1/auth/login

# Check environment variables (on Render)
echo $SECRET_KEY  # Should not be empty
```

---

## 📊 Expected Results

### Successful Deployment Indicators:

1. **Backend Health Check**:
   ```json
   {
     "status": "healthy",
     "firebase_connected": true,
     "message": "RetailGenie Authentication Service"
   }
   ```

2. **Frontend Build Success**:
   ```
   File sizes after gzip:
     192.56 kB  build/static/js/main.*.js
     7.96 kB    build/static/css/main.*.css
   
   The build folder is ready to be deployed.
   ```

3. **Authentication Flow**:
   - Demo login works
   - Dashboard loads
   - All pages accessible

---

## 🔄 Continuous Deployment

### GitHub Actions (Optional):

```yaml
# .github/workflows/deploy.yml
name: Deploy to Render
on:
  push:
    branches: [main]
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Deploy to Render
        run: |
          curl -X POST \
            -H "Authorization: Bearer ${{ secrets.RENDER_API_KEY }}" \
            "https://api.render.com/v1/services/${{ secrets.RENDER_SERVICE_ID }}/deploys"
```

---

## 📞 Support

### Render Deployment URLs:
- Backend: `https://your-app-name.onrender.com`
- Frontend: `https://your-frontend-name.onrender.com` or custom domain

### Key Files for Deployment:
- `backend/wsgi_production.py` - Production WSGI entry point
- `backend/Procfile` - Process configuration
- `backend/requirements.txt` - Python dependencies
- `backend/runtime.txt` - Python version
- `frontend/.env.production` - Frontend production config

**Total Deployment Time:** 15-30 minutes for both frontend and backend

---

*Last Updated: July 8, 2025 - RetailGenie v1.0.0*
