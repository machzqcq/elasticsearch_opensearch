#!/bin/bash

# Search-as-you-Type Application Startup Script
# This script starts all components of the application

set -e

echo "🚀 Starting Search-as-you-Type Application"
echo "=========================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if OpenSearch is running
echo -e "${BLUE}Checking OpenSearch...${NC}"
if curl -k -s -u admin:Developer@123 https://localhost:9200 > /dev/null 2>&1; then
    echo -e "${GREEN}✓ OpenSearch is running${NC}"
else
    echo -e "${YELLOW}⚠ OpenSearch is not running. Starting with Docker...${NC}"
    cd ..
    docker-compose -f "opensearch_server/1. docker-compose-load-ecommerce.yml" up -d
    cd search_as_you_type
    echo "Waiting for OpenSearch to be ready..."
    sleep 10
fi

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo -e "${YELLOW}Creating virtual environment...${NC}"
    uv venv
fi

# Activate virtual environment
echo -e "${BLUE}Activating virtual environment...${NC}"
source .venv/bin/activate

# Install dependencies if needed
if ! python -c "import fastapi" 2>/dev/null; then
    echo -e "${YELLOW}Installing dependencies...${NC}"
    uv pip install -e .
fi

# Create .env if it doesn't exist
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}Creating .env file from template...${NC}"
    cp .env.example .env
fi

# Check Node.js version and install/use Node 18 if needed
echo -e "${BLUE}Checking Node.js version...${NC}"
if command -v node &> /dev/null; then
    NODE_VERSION=$(node -v | cut -d'v' -f2 | cut -d'.' -f1)
    if [ "$NODE_VERSION" -lt 18 ]; then
        echo -e "${YELLOW}Node.js version $NODE_VERSION detected. React requires Node.js 18+${NC}"
        echo -e "${YELLOW}Installing nvm and Node.js 18...${NC}"
        
        # Install nvm if not already installed
        if [ ! -d "$HOME/.nvm" ]; then
            curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash
        fi
        
        # Load nvm
        export NVM_DIR="$HOME/.nvm"
        [ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"
        
        # Install and use Node 18
        nvm install 18
        nvm use 18
        echo -e "${GREEN}✓ Node.js 18 installed and activated${NC}"
    else
        echo -e "${GREEN}✓ Node.js version $(node -v) is compatible${NC}"
    fi
else
    echo -e "${YELLOW}Node.js not found. Installing nvm and Node.js 18...${NC}"
    
    # Install nvm
    curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash
    
    # Load nvm
    export NVM_DIR="$HOME/.nvm"
    [ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"

    # Install and use Node 16
    nvm install 16
    nvm use 16
    echo -e "${GREEN}✓ Node.js 16 installed and activated${NC}"
fi

# Check and install React dependencies if needed
if [ -d "react-frontend" ]; then
    if [ ! -d "react-frontend/node_modules" ]; then
        echo -e "${YELLOW}Installing React dependencies...${NC}"
        cd react-frontend
        npm install
        cd ..
        echo -e "${GREEN}✓ React dependencies installed${NC}"
    fi
fi

echo ""
echo -e "${GREEN}✓ Setup complete!${NC}"
echo ""
echo "Starting services..."
echo "===================="
echo ""

# Start backend in background
echo -e "${BLUE}Starting FastAPI backend on port 8000...${NC}"
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 > logs/backend.log 2>&1 &
BACKEND_PID=$!
echo -e "${GREEN}✓ Backend started (PID: $BACKEND_PID)${NC}"

# Wait for backend to be ready
echo "Waiting for backend to be ready..."
sleep 3

echo ""
echo -e "${GREEN}=========================================${NC}"
echo -e "${GREEN}All services started successfully!${NC}"
echo -e "${GREEN}=========================================${NC}"
echo ""
echo "Available frontends:"
echo "-------------------"
echo ""
echo "1. Streamlit (Python-based):"
echo "   streamlit run streamlit_app.py --server.address 0.0.0.0 --server.port 8501"
echo "   Access at: http://0.0.0.0:8501"
echo ""
echo "2. Gradio (ML-friendly):"
echo "   python gradio_app.py"
echo "   Access at: http://0.0.0.0:7860"
echo ""
echo "3. React (Modern web):"
echo "   cd react-frontend && HOST=0.0.0.0 npm start"
echo "   Access at: http://0.0.0.0:3000"
echo ""
echo "Backend API:"
echo "   Docs: http://localhost:8000/docs"
echo "   Health: http://localhost:8000/api/health"
echo ""
echo "To stop all services:"
echo "   ./stop.sh"
echo ""
echo "To stop the backend only:"
echo "   kill $BACKEND_PID"
echo ""
echo "Logs are in: logs/backend.log"
