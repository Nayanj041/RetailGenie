#!/bin/bash

# RetailGenie Environment Setup Script
# This script helps generate secure keys and provides setup guidance

echo "🚀 RetailGenie Environment Setup Helper"
echo "======================================="
echo

# Check if .env exists
if [ -f ".env" ]; then
    echo "⚠️  .env file already exists. Creating backup..."
    cp .env .env.backup.$(date +%Y%m%d_%H%M%S)
    echo "✅ Backup created"
    echo
fi

# Generate secure keys
echo "🔐 Generating secure keys..."
echo

SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_hex(32))")
JWT_SECRET=$(python3 -c "import secrets; print(secrets.token_urlsafe(64))")

echo "Generated SECRET_KEY: $SECRET_KEY"
echo "Generated JWT_SECRET: $JWT_SECRET"
echo

# Create or update .env file
echo "📝 Creating .env file..."

cat > .env << EOF
# Environment Configuration for RetailGenie Backend
# Generated on $(date)

# Flask Configuration
FLASK_ENV=development
FLASK_DEBUG=True
SECRET_KEY=$SECRET_KEY

# JWT Configuration
JWT_SECRET=$JWT_SECRET

# CORS Configuration
CORS_ORIGINS=http://localhost:3000,http://localhost:3001

# Firebase Configuration (REQUIRED - Fill these in)
FIREBASE_PROJECT_ID=your-firebase-project-id
FIREBASE_PRIVATE_KEY_ID=your-private-key-id
FIREBASE_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----\nyour-private-key-here\n-----END PRIVATE KEY-----\n"
FIREBASE_CLIENT_EMAIL=your-service-account@your-project.iam.gserviceaccount.com
FIREBASE_CLIENT_ID=your-client-id
FIREBASE_AUTH_URI=https://accounts.google.com/o/oauth2/auth
FIREBASE_TOKEN_URI=https://oauth2.googleapis.com/token

# Google Gemini Configuration (REQUIRED - Fill these in)
GEMINI_API_KEY=your-gemini-api-key-here
GEMINI_MODEL=gemini-pro

# Email Configuration (SMTP) (REQUIRED for email features)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SENDER_EMAIL=your-email@gmail.com
SENDER_PASSWORD=your-app-password
ADMIN_EMAIL=admin@retailgenie.com

# PDF Report Configuration
PDF_OUTPUT_DIR=reports

# Database Configuration
DATABASE_URL=firebase

# Caching Configuration
CACHE_TYPE=simple
CACHE_DEFAULT_TIMEOUT=300

# Redis Configuration (REQUIRED for background tasks)
REDIS_URL=redis://localhost:6379/0

# Rate Limiting
RATELIMIT_DEFAULT=1000 per hour
RATELIMIT_STORAGE_URL=memory://

# Performance Monitoring
SLOW_REQUEST_THRESHOLD=2.0
ENABLE_METRICS=True

# Background Tasks (Celery)
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

# Security Settings
BCRYPT_LOG_ROUNDS=12

# API Versioning
API_VERSION=1.0.0
DEFAULT_API_VERSION=v1
EOF

echo "✅ .env file created successfully!"
echo

# Check for required services
echo "🔍 Checking for required services..."
echo

# Check Python
if command -v python3 &> /dev/null; then
    echo "✅ Python 3 is installed"
else
    echo "❌ Python 3 is not installed"
fi

# Check Redis
if command -v redis-server &> /dev/null; then
    echo "✅ Redis is installed"
    if pgrep redis-server > /dev/null; then
        echo "✅ Redis is running"
    else
        echo "⚠️  Redis is installed but not running"
        echo "   Start with: sudo systemctl start redis-server"
    fi
else
    echo "❌ Redis is not installed"
    echo "   Install with: sudo apt install redis-server (Ubuntu/Debian)"
    echo "   Or: brew install redis (macOS)"
fi

# Check if pip packages are installed
echo
echo "📦 Checking Python dependencies..."
if [ -f "requirements.txt" ]; then
    echo "✅ requirements.txt found"
    if python3 -c "import google.generativeai" 2>/dev/null; then
        echo "✅ google-generativeai is installed"
    else
        echo "⚠️  google-generativeai not installed"
        echo "   Run: pip install -r requirements.txt"
    fi
else
    echo "❌ requirements.txt not found"
fi

echo
echo "📋 Next Steps:"
echo "=============="
echo
echo "1. 🔥 Set up Firebase:"
echo "   - Go to https://console.firebase.google.com/"
echo "   - Create a new project"
echo "   - Enable Firestore and Authentication"
echo "   - Create a service account and download the JSON"
echo "   - Update Firebase variables in .env"
echo
echo "2. 🤖 Get Gemini API Key:"
echo "   - Go to https://makersuite.google.com/app/apikey"
echo "   - Create an API key"
echo "   - Update GEMINI_API_KEY in .env"
echo
echo "3. 📧 Configure Email (optional but recommended):"
echo "   - For Gmail: Enable 2FA and create an app password"
echo "   - Update SMTP variables in .env"
echo
echo "4. 💾 Set up Redis (for background tasks):"
echo "   - Install Redis if not already installed"
echo "   - Start Redis service"
echo "   - Update REDIS_URL if using remote Redis"
echo
echo "5. 📚 Read the detailed guide:"
echo "   - Check docs/ENVIRONMENT_VARIABLES_GUIDE.md for detailed instructions"
echo
echo "6. 🧪 Test your configuration:"
echo "   - Run: python test_gemini.py"
echo "   - Run: python -m pytest tests/"
echo
echo "7. 🚀 Start the application:"
echo "   - Run: ./start_enhanced.sh"
echo

# Final validation
echo "🔍 Configuration Validation:"
echo "============================="
echo

REQUIRED_VARS=("SECRET_KEY" "JWT_SECRET" "FIREBASE_PROJECT_ID" "GEMINI_API_KEY")
MISSING_VARS=()

for var in "${REQUIRED_VARS[@]}"; do
    if grep -q "^${var}=your-" .env || grep -q "^${var}=$" .env; then
        MISSING_VARS+=("$var")
    fi
done

if [ ${#MISSING_VARS[@]} -eq 0 ]; then
    echo "✅ All critical variables appear to be configured"
else
    echo "⚠️  The following variables still need to be configured:"
    for var in "${MISSING_VARS[@]}"; do
        echo "   - $var"
    done
fi

echo
echo "📖 For detailed setup instructions, see:"
echo "   docs/ENVIRONMENT_VARIABLES_GUIDE.md"
echo
echo "🎉 Setup complete! Happy coding!"
