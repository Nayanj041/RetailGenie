#!/bin/bash
"""
RetailGenie Optimized API Startup Script
Features: Performance optimization, caching, rate limiting, monitoring
"""

set -e

echo "🚀 Starting RetailGenie Optimized API Server"
echo "=============================================="

# Check Python environment
echo "📋 Checking environment..."
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
elif command -v python &> /dev/null; then
    PYTHON_CMD="python"
else
    echo "❌ Python not found. Please install Python 3.8+"
    exit 1
fi

echo "✅ Python: $($PYTHON_CMD --version)"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    $PYTHON_CMD -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate || {
    echo "❌ Failed to activate virtual environment"
    exit 1
}

# Install/upgrade dependencies
echo "📚 Installing optimized dependencies..."
pip install --upgrade pip
pip install -r <(cat << EOF
flask>=3.0.0
flask-cors>=4.0.0
flask-caching>=2.0.0
Flask-Limiter>=3.0.0
redis>=4.0.0
psutil>=5.9.0
firebase-admin>=6.0.0
python-dotenv>=1.0.0
requests>=2.28.0
gunicorn>=20.1.0
pytest>=7.0.0
pytest-flask>=1.2.0
pytest-cov>=4.0.0
EOF
)

# Check Firebase credentials
echo "🔐 Checking Firebase configuration..."
if [ ! -f "firebase-credentials.json" ]; then
    echo "⚠️  Firebase credentials not found. Some features may not work."
    echo "   Please add firebase-credentials.json to enable database features."
else
    echo "✅ Firebase credentials found"
fi

# Create logs directory
mkdir -p logs

# Set environment variables for optimization
export FLASK_ENV=${FLASK_ENV:-development}
export FLASK_DEBUG=${FLASK_DEBUG:-True}
export PYTHONPATH=${PYTHONPATH:-.}

# Performance optimizations
export PYTHONDONTWRITEBYTECODE=1  # Don't write .pyc files
export PYTHONUNBUFFERED=1         # Force unbuffered output

echo ""
echo "🎯 Configuration Summary:"
echo "   Environment: $FLASK_ENV"
echo "   Debug Mode: $FLASK_DEBUG"
echo "   Cache: Simple (Redis available for production)"
echo "   Rate Limiting: Active"
echo "   Monitoring: Enabled"
echo "   Performance Tracking: Enabled"

echo ""
echo "🌟 Optimized Features Enabled:"
echo "   ✅ Response Caching (5min default)"
echo "   ✅ Rate Limiting (1000/hour, 100/minute)"
echo "   ✅ Request Performance Monitoring"
echo "   ✅ Structured JSON Logging"
echo "   ✅ System Metrics Endpoint"
echo "   ✅ Enhanced API Versioning"
echo "   ✅ Database Query Optimization"

echo ""
echo "📡 Starting server..."
echo "   Access URLs:"
echo "   • Health Check: http://localhost:5000/health"
echo "   • API v1: http://localhost:5000/api/v1/products"
echo "   • API v2: http://localhost:5000/api/v2/products"
echo "   • Metrics: http://localhost:5000/metrics"
echo "   • Performance Test: python test_performance.py"

echo ""
echo "🔄 Server starting in 3 seconds..."
sleep 3

# Start the optimized server
$PYTHON_CMD app.py
