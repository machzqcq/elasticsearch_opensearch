#!/bin/bash

# Search-as-you-Type Application Stop Script
# This script stops all components of the application

set -e

echo "🛑 Stopping Search-as-you-Type Application"
echo "==========================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

STOPPED=0

# Function to kill process by port
kill_by_port() {
    local port=$1
    local name=$2
    
    # Find process using the port
    local pid=$(lsof -ti:$port 2>/dev/null)
    
    if [ -n "$pid" ]; then
        echo -e "${BLUE}Stopping $name (PID: $pid) on port $port...${NC}"
        kill -9 $pid 2>/dev/null || true
        echo -e "${GREEN}✓ $name stopped${NC}"
        STOPPED=$((STOPPED + 1))
    else
        echo -e "${YELLOW}⚠ No process found for $name on port $port${NC}"
    fi
}

# Function to kill process by name
kill_by_name() {
    local process_name=$1
    local display_name=$2
    
    # Find PIDs matching the process name, excluding VS Code server
    local pids=$(pgrep -f "$process_name" 2>/dev/null | while read pid; do
        # Check if this is a VS Code server process
        if ! ps -p $pid -o args= | grep -q "vscode-server\|code-server\|\.vscode-server"; then
            echo $pid
        fi
    done)
    
    if [ -n "$pids" ]; then
        echo -e "${BLUE}Stopping $display_name...${NC}"
        echo "$pids" | while read pid; do
            if [ -n "$pid" ]; then
                kill -9 $pid 2>/dev/null || true
                echo -e "${GREEN}✓ Stopped process $pid${NC}"
                STOPPED=$((STOPPED + 1))
            fi
        done
    else
        echo -e "${YELLOW}⚠ No $display_name process found${NC}"
    fi
}

echo "Checking for running services..."
echo ""

# Stop FastAPI Backend (port 8000)
kill_by_port 8000 "FastAPI Backend"

# Stop Streamlit (port 8501)
kill_by_port 8501 "Streamlit"

# Stop Gradio (port 7860)
kill_by_port 7860 "Gradio"

# Stop React (port 3000)
kill_by_port 3000 "React"

# Additional cleanup - kill by process name
echo ""
echo "Performing additional cleanup..."
echo ""

# Kill any remaining Streamlit processes
kill_by_name "streamlit" "Streamlit (by name)"

# Kill any remaining Gradio processes
kill_by_name "gradio_app.py" "Gradio (by name)"

# Kill any remaining uvicorn processes
kill_by_name "uvicorn.*backend.main" "Uvicorn Backend (by name)"

# Kill any remaining node processes running react-scripts
kill_by_name "react-scripts" "React (by name)"

# Kill any npm processes in react-frontend directory
kill_by_name "npm.*react-frontend" "React npm (by name)"

echo ""
echo -e "${GREEN}==========================================${NC}"
if [ $STOPPED -gt 0 ]; then
    echo -e "${GREEN}✓ Stopped $STOPPED process(es)${NC}"
else
    echo -e "${YELLOW}No processes were running${NC}"
fi
echo -e "${GREEN}==========================================${NC}"
echo ""
echo "All services have been stopped."
echo ""
echo "To start the services again, run:"
echo "  ./start.sh"
echo ""
