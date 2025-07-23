#!/bin/bash

# MinhOS v3 Startup Script
# ========================

set -e  # Exit on any error

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "🚀 Starting MinhOS v3 Trading Platform"
echo "======================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check Python version
python_version=$(python3 -c "import sys; print('.'.join(map(str, sys.version_info[:2])))")
required_version="3.9"

if ! python3 -c "import sys; exit(0 if sys.version_info >= (3, 9) else 1)" 2>/dev/null; then
    echo -e "${RED}❌ Error: Python 3.9+ required, found $python_version${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Python version: $python_version${NC}"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}⚠️  Creating Python virtual environment...${NC}"
    python3 -m venv venv
fi

# Activate virtual environment
echo -e "${BLUE}📦 Activating virtual environment...${NC}"
source venv/bin/activate

# Install/update dependencies
echo -e "${BLUE}📦 Installing dependencies...${NC}"
pip install -q -r requirements.txt

# Create necessary directories
echo -e "${BLUE}📁 Creating directories...${NC}"
mkdir -p data logs ml_models

# Check if Redis is running (optional)
if command -v redis-cli &> /dev/null; then
    if redis-cli ping &> /dev/null; then
        echo -e "${GREEN}✅ Redis is running${NC}"
    else
        echo -e "${YELLOW}⚠️  Redis not running - some features may be limited${NC}"
    fi
else
    echo -e "${YELLOW}⚠️  Redis not installed - some features may be limited${NC}"
fi

# Test bridge connection (optional)
if [ -n "$SIERRA_HOST" ]; then
    echo -e "${BLUE}🌉 Testing bridge connection to $SIERRA_HOST...${NC}"
    if curl -s --connect-timeout 5 "http://$SIERRA_HOST:${SIERRA_PORT:-8765}/health" > /dev/null; then
        echo -e "${GREEN}✅ Bridge connection successful${NC}"
    else
        echo -e "${YELLOW}⚠️  Bridge not available - running in demo mode${NC}"
    fi
else
    echo -e "${YELLOW}⚠️  SIERRA_HOST not set - running in demo mode${NC}"
fi

# Set environment
export MINHOS_ENV="${MINHOS_ENV:-dev}"
export PYTHONPATH="${SCRIPT_DIR}:${PYTHONPATH}"

echo -e "${BLUE}🎯 Environment: $MINHOS_ENV${NC}"
echo -e "${BLUE}🏠 Working directory: $SCRIPT_DIR${NC}"

# Check for .env file
if [ -f ".env" ]; then
    echo -e "${GREEN}✅ Loading .env configuration${NC}"
    set -a  # automatically export all variables
    source .env
    set +a
else
    echo -e "${YELLOW}⚠️  No .env file found - using defaults${NC}"
    echo -e "${BLUE}💡 Copy .env.example to .env for custom configuration${NC}"
fi

echo ""
echo -e "${GREEN}🚀 Starting MinhOS v3...${NC}"
echo -e "${BLUE}📊 Dashboard will be available at: http://localhost:8888${NC}"
echo -e "${BLUE}🔌 API will be available at: http://localhost:8000${NC}"
echo -e "${BLUE}📡 WebSocket will be available at: ws://localhost:9001${NC}"
echo ""
echo -e "${YELLOW}Press Ctrl+C to shutdown gracefully${NC}"
echo ""

# Add signal handlers
cleanup() {
    echo ""
    echo -e "${YELLOW}🛑 Shutting down MinhOS v3...${NC}"
    # Kill any background processes
    jobs -p | xargs -r kill
    echo -e "${GREEN}✅ Shutdown complete${NC}"
    exit 0
}

trap cleanup SIGINT SIGTERM

# Start MinhOS v3
python -m minhos.main &
MAIN_PID=$!

# Wait for main process
wait $MAIN_PID