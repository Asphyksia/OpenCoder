#!/bin/bash
# OpenCoder - Unified Start Script
# Starts both backend and frontend services

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}Starting OpenCoder...${NC}"

# Check if we're in the right directory
if [ ! -f "opencoder/api/main.py" ]; then
    echo -e "${RED}Error: Run this script from the OpenCoder root directory${NC}"
    exit 1
fi

# Load environment variables
if [ -f ".env" ]; then
    export $(cat .env | grep -v '^#' | xargs)
    echo -e "${GREEN}✓ Environment loaded${NC}"
else
    echo -e "${YELLOW}Warning: .env file not found${NC}"
fi

# Check for required variables
if [ -z "$OPENGPU_API_KEY" ]; then
    echo -e "${RED}Error: OPENGPU_API_KEY not set in .env${NC}"
    echo "Please create .env file with your API key:"
    echo "  cp .env.example .env"
    echo "  nano .env"
    exit 1
fi

# Parse arguments
MODE="${1:-all}"

start_backend() {
    echo -e "${GREEN}Starting backend on port 8001...${NC}"
    source venv/bin/activate
    uvicorn opencoder.api.main:app --port 8001 --reload &
    BACKEND_PID=$!
    echo "Backend PID: $BACKEND_PID"
}

start_frontend() {
    echo -e "${GREEN}Starting frontend on port 3000...${NC}"
    cd frontend
    npm run dev &
    FRONTEND_PID=$!
    echo "Frontend PID: $FRONTEND_PID"
    cd ..
}

case "$MODE" in
    --backend|-b)
        start_backend
        ;;
    --frontend|-f)
        start_frontend
        ;;
    --all|-a|"")
        start_backend
        sleep 2
        start_frontend
        ;;
    *)
        echo "Usage: $0 [--backend|--frontend|--all]"
        echo "  -b, --backend    Start only backend"
        echo "  -f, --frontend   Start only frontend"
        echo "  -a, --all       Start both (default)"
        exit 1
        ;;
esac

echo -e "${GREEN}OpenCoder started successfully!${NC}"
echo "Backend: http://localhost:8001"
echo "Frontend: http://localhost:3000"
echo ""
echo "Press Ctrl+C to stop all services"

# Wait for interrupt
trap "echo -e '${YELLOW}Stopping OpenCoder...${NC}'; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit" INT TERM

wait
