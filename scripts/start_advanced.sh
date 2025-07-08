#!/bin/bash
"""
RetailGenie Advanced Features Startup Script
Starts all advanced services: API, WebSocket, Celery Worker, Swagger Docs
"""

set -e

echo "🚀 Starting RetailGenie Advanced Features"
echo "=========================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check Python environment
echo -e "${BLUE}📋 Checking environment...${NC}"
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
elif command -v python &> /dev/null; then
    PYTHON_CMD="python"
else
    echo -e "${RED}❌ Python not found. Please install Python 3.8+${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Python: $($PYTHON_CMD --version)${NC}"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}📦 Creating virtual environment...${NC}"
    $PYTHON_CMD -m venv venv
fi

# Activate virtual environment
echo -e "${BLUE}🔧 Activating virtual environment...${NC}"
source venv/bin/activate || {
    echo -e "${RED}❌ Failed to activate virtual environment${NC}"
    exit 1
}

# Install dependencies
echo -e "${BLUE}📚 Installing advanced dependencies...${NC}"
pip install --upgrade pip -q
pip install -q \
    flask>=3.0.0 \
    flask-cors>=4.0.0 \
    flask-caching>=2.0.0 \
    Flask-Limiter>=3.0.0 \
    flask-socketio>=5.0.0 \
    flask-restx>=1.0.0 \
    celery[redis]>=5.0.0 \
    redis>=5.0.0 \
    psutil>=5.9.0 \
    firebase-admin>=6.0.0 \
    python-dotenv>=1.0.0 \
    requests>=2.28.0 \
    gunicorn>=20.1.0

echo -e "${GREEN}✅ Dependencies installed${NC}"

# Check Redis availability
echo -e "${BLUE}🔧 Checking Redis availability...${NC}"
if command -v redis-server &> /dev/null; then
    echo -e "${GREEN}✅ Redis available${NC}"
    # Start Redis if not running
    if ! pgrep -x "redis-server" > /dev/null; then
        echo -e "${YELLOW}🔄 Starting Redis server...${NC}"
        redis-server --daemonize yes --port 6379 2>/dev/null || echo -e "${YELLOW}⚠️  Could not start Redis. Using memory backend.${NC}"
    else
        echo -e "${GREEN}✅ Redis already running${NC}"
    fi
else
    echo -e "${YELLOW}⚠️  Redis not found. Celery will use memory backend.${NC}"
fi

# Create necessary directories
mkdir -p logs
mkdir -p reports
mkdir -p temp

# Set environment variables
export FLASK_ENV=${FLASK_ENV:-development}
export FLASK_DEBUG=${FLASK_DEBUG:-True}
export PYTHONPATH=${PYTHONPATH:-.}
export PYTHONDONTWRITEBYTECODE=1
export PYTHONUNBUFFERED=1

# Advanced feature configuration
export CELERY_BROKER_URL=${CELERY_BROKER_URL:-redis://localhost:6379/0}
export CELERY_RESULT_BACKEND=${CELERY_RESULT_BACKEND:-redis://localhost:6379/0}

echo ""
echo -e "${BLUE}🎯 Advanced Features Configuration:${NC}"
echo -e "   Environment: $FLASK_ENV"
echo -e "   Debug Mode: $FLASK_DEBUG"
echo -e "   Celery Broker: ${CELERY_BROKER_URL}"
echo -e "   WebSocket Support: Enabled"
echo -e "   API Documentation: Enabled"

echo ""
echo -e "${GREEN}🌟 Advanced Features Available:${NC}"
echo -e "   ✅ Background Tasks (Celery)"
echo -e "   ✅ Real-time WebSocket Communication"
echo -e "   ✅ Interactive API Documentation (Swagger)"
echo -e "   ✅ Performance Monitoring"
echo -e "   ✅ Caching & Rate Limiting"

echo ""
echo -e "${BLUE}📡 Service URLs:${NC}"
echo -e "   • Main API: http://localhost:5000"
echo -e "   • WebSocket: http://localhost:5001"
echo -e "   • API Docs: http://localhost:5002/docs/"
echo -e "   • Celery Monitoring: Check terminal output"

echo ""
echo -e "${YELLOW}🔄 Starting services in 3 seconds...${NC}"
sleep 3

# Function to kill background processes on exit
cleanup() {
    echo -e "\n${YELLOW}🛑 Shutting down services...${NC}"
    jobs -p | xargs -r kill
    exit 0
}
trap cleanup SIGINT SIGTERM

# Start services in background
echo -e "${GREEN}🚀 Starting Main API Server (Port 5000)...${NC}"
$PYTHON_CMD app.py > logs/api.log 2>&1 &
API_PID=$!

sleep 2

echo -e "${GREEN}🚀 Starting WebSocket Server (Port 5001)...${NC}"
$PYTHON_CMD websocket_app.py > logs/websocket.log 2>&1 &
WS_PID=$!

sleep 2

echo -e "${GREEN}🚀 Starting Swagger Documentation Server (Port 5002)...${NC}"
$PYTHON_CMD swagger_docs.py > logs/swagger.log 2>&1 &
SWAGGER_PID=$!

sleep 2

echo -e "${GREEN}🚀 Starting Celery Worker...${NC}"
celery -A celery_app worker --loglevel=info --concurrency=2 > logs/celery.log 2>&1 &
CELERY_PID=$!

sleep 3

# Health checks
echo ""
echo -e "${BLUE}🏥 Performing health checks...${NC}"

# Check Main API
if curl -s http://localhost:5000/health > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Main API: Running${NC}"
else
    echo -e "${RED}❌ Main API: Failed${NC}"
fi

# Check WebSocket
if curl -s http://localhost:5001/ > /dev/null 2>&1; then
    echo -e "${GREEN}✅ WebSocket: Running${NC}"
else
    echo -e "${RED}❌ WebSocket: Failed${NC}"
fi

# Check Swagger
if curl -s http://localhost:5002/api/health/ > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Swagger Docs: Running${NC}"
else
    echo -e "${RED}❌ Swagger Docs: Failed${NC}"
fi

echo ""
echo -e "${GREEN}🎉 All services started successfully!${NC}"
echo ""
echo -e "${BLUE}📋 Usage Examples:${NC}"
echo -e "   # Test Main API"
echo -e "   curl http://localhost:5000/health"
echo -e ""
echo -e "   # View API Documentation"
echo -e "   open http://localhost:5002/docs/"
echo -e ""
echo -e "   # Test WebSocket (using a WebSocket client)"
echo -e "   ws://localhost:5001/socket.io"
echo -e ""
echo -e "   # Send background task"
echo -e "   curl -X POST http://localhost:5000/api/tasks/email \\"
echo -e "        -H 'Content-Type: application/json' \\"
echo -e "        -d '{\"recipient\":\"test@example.com\",\"subject\":\"Test\"}'"

echo ""
echo -e "${YELLOW}📊 Monitor logs:${NC}"
echo -e "   tail -f logs/api.log      # Main API logs"
echo -e "   tail -f logs/websocket.log # WebSocket logs"
echo -e "   tail -f logs/swagger.log   # Swagger logs"
echo -e "   tail -f logs/celery.log    # Celery worker logs"

echo ""
echo -e "${GREEN}🔄 Services running... Press Ctrl+C to stop all services${NC}"

# Wait for all background processes
wait
