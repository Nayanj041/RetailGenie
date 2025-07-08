#!/bin/bash

# Production deployment script for RetailGenie Backend
# This script prepares and deploys the application to production

set -e

echo "🚀 Starting RetailGenie Backend Production Deployment"

# Check if .env exists
if [ ! -f .env ]; then
    echo "❌ Error: .env file not found!"
    echo "Please create .env file with production configuration"
    exit 1
fi

# Check if firebase credentials exist
if [ ! -f firebase-credentials.json ]; then
    echo "❌ Error: firebase-credentials.json not found!"
    echo "Please add Firebase credentials file"
    exit 1
fi

# Install/update dependencies
echo "📦 Installing production dependencies..."
pip install -r requirements.txt

# Run tests
echo "🧪 Running tests..."
if [ -f "run_tests.sh" ]; then
    chmod +x run_tests.sh
    ./run_tests.sh --no-coverage
else
    python -m pytest tests/ -v
fi

# Check if tests passed
if [ $? -ne 0 ]; then
    echo "❌ Tests failed! Deployment aborted."
    exit 1
fi

echo "✅ Tests passed!"

# Validate environment configuration
echo "🔧 Validating production configuration..."
python3 -c "
import os
from dotenv import load_dotenv
load_dotenv()

required_vars = ['SECRET_KEY', 'FIREBASE_PROJECT_ID', 'FIREBASE_PRIVATE_KEY_ID']
missing_vars = []

for var in required_vars:
    if not os.getenv(var):
        missing_vars.append(var)

if missing_vars:
    print(f'❌ Missing required environment variables: {missing_vars}')
    exit(1)
else:
    print('✅ Environment configuration valid')
"

# Build Docker image (if using Docker deployment)
if [ "$1" = "docker" ]; then
    echo "🐳 Building Docker image..."
    docker build -t retailgenie-backend:latest .
    echo "✅ Docker image built successfully"
fi

# Production server options
echo "🎯 Production deployment options:"
echo "1. Render: Use render.yaml configuration"
echo "2. Heroku: git push heroku main"
echo "3. Google Cloud: gcloud app deploy"
echo "4. Docker: docker run -p 5000:5000 --env-file .env retailgenie-backend:latest"
echo "5. Manual: gunicorn --bind 0.0.0.0:5000 --workers 4 app:app"

echo ""
echo "✅ RetailGenie Backend is ready for production deployment!"
echo "📚 API Documentation:"
echo "   - V1 API: /api/v1/info"
echo "   - V2 API: /api/v2/info"
echo "   - Health Check: /health"

# Optional: Start local production server for testing
if [ "$1" = "test" ]; then
    echo "🔥 Starting local production server for testing..."
    export FLASK_ENV=production
    export FLASK_DEBUG=False
    gunicorn --bind 0.0.0.0:5000 --workers 2 app:app
fi
