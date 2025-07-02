#!/bin/bash

# RetailGenie Backend - Enhanced Startup Script
# This script sets up the enhanced backend with all advanced features

set -e

echo "🚀 Starting RetailGenie Backend Setup with Enhanced Features..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

echo_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

echo_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

echo_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo_error "Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

echo_info "Python version: $(python3 --version)"

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    echo_error "pip3 is not installed. Please install pip."
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo_info "Creating virtual environment..."
    python3 -m venv venv
    echo_success "Virtual environment created"
fi

# Activate virtual environment
echo_info "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo_info "Upgrading pip..."
pip install --upgrade pip

# Install requirements
echo_info "Installing Python dependencies..."
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
    echo_success "Dependencies installed successfully"
else
    echo_error "requirements.txt not found"
    exit 1
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo_warning ".env file not found"
    if [ -f ".env.example" ]; then
        echo_info "Copying .env.example to .env..."
        cp .env.example .env
        echo_warning "Please edit .env file with your actual configuration values"
    else
        echo_error "No .env.example file found either"
    fi
fi

# Create necessary directories
echo_info "Creating necessary directories..."
mkdir -p reports
mkdir -p logs
mkdir -p uploads
echo_success "Directories created"

# Check if Firebase configuration is present
echo_info "Checking Firebase configuration..."
if [ -f "serviceAccountKey.json" ]; then
    echo_success "Firebase service account key found"
else
    echo_warning "Firebase service account key not found"
    echo_info "Please add your Firebase serviceAccountKey.json file to enable database features"
fi

# Set environment variables for this session
export FLASK_APP=app.py
export FLASK_ENV=development

# Check if all required components are working
echo_info "Running health checks..."

# Test basic imports
python3 -c "
import flask
import firebase_admin
import openai
import jwt
print('✅ All required packages imported successfully')
" 2>/dev/null && echo_success "Import test passed" || echo_warning "Some packages may have import issues"

# Display available startup options
echo ""
echo_info "🎯 RetailGenie Backend Setup Complete!"
echo ""
echo_info "Available startup options:"
echo "  1. 🖥️  Basic Flask server:           python3 app.py"
echo "  2. 🚀 Production server:            python3 app_production.py"
echo "  3. ⚡ Optimized server:             python3 app_optimized.py"
echo "  4. 📊 With API documentation:       python3 monitoring/swagger_docs.py (port 5002)"
echo "  5. 🌐 WebSocket support:           python3 websocket_app.py (port 5001)"
echo ""
echo_info "🔧 Advanced features available:"
echo "  • 🤖 AI Assistant (requires Google Gemini API key)"
echo "  • 📊 Analytics & Reporting"
echo "  • 📦 Inventory Management"
echo "  • 💰 Dynamic Pricing"
echo "  • 🌿 Sustainability Scoring"
echo "  • 📧 Email Notifications"
echo "  • 📄 PDF Report Generation"
echo "  • 🔐 JWT Authentication"
echo ""

# Start the server based on argument
case "$1" in
    "production")
        echo_info "Starting production server..."
        python3 app_production.py
        ;;
    "optimized")
        echo_info "Starting optimized server..."
        python3 app_optimized.py
        ;;
    "docs")
        echo_info "Starting API documentation server..."
        python3 monitoring/swagger_docs.py
        ;;
    "websocket")
        echo_info "Starting WebSocket server..."
        python3 websocket_app.py
        ;;
    "basic"|"")
        echo_info "Starting enhanced basic server..."
        python3 app.py
        ;;
    *)
        echo_warning "Unknown option: $1"
        echo_info "Valid options: basic, production, optimized, docs, websocket"
        echo_info "Starting enhanced basic server..."
        python3 app.py
        ;;
esac
