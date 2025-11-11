#!/bin/bash

# Startup script for OpenSearch MCP Server Educational App

set -e

echo "🚀 OpenSearch MCP Server - Educational Demo"
echo "==========================================="
echo ""

# Check if .env file exists
if [ ! -f .env ]; then
    echo "⚠️  .env file not found. Creating from .env.example..."
    cp .env.example .env
    echo "✅ Created .env file. Please edit it with your configuration."
    echo ""
    read -p "Press Enter to continue after editing .env file..."
fi

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo "❌ uv is not installed. Installing..."
    pip install uv
fi

# Install dependencies
echo "📦 Installing dependencies..."
uv sync

# Check if MCP server is running
echo ""
echo "🔍 Checking MCP server status..."
MCP_PORT=${MCP_SERVER_PORT:-9900}

if curl -s -o /dev/null -w "%{http_code}" http://localhost:$MCP_PORT/health | grep -q "200"; then
    echo "✅ MCP server is running on port $MCP_PORT"
else
    echo "⚠️  MCP server not detected on port $MCP_PORT"
    echo ""
    echo "Please start the MCP server in a separate terminal:"
    echo "  python start_mcp_server.py"
    echo ""
    echo "Or manually with config file:"
    echo "  python -m mcp_server_opensearch --transport stream --port $MCP_PORT --config mcp_server_config.yaml"
    echo ""
    read -p "Press Enter when MCP server is running..."
fi

# Check OpenSearch connection
echo ""
echo "🔍 Checking OpenSearch connection..."
OPENSEARCH_URL=${OPENSEARCH_URL:-https://localhost:9200}

if curl -k -s -o /dev/null -w "%{http_code}" $OPENSEARCH_URL | grep -q "200\|401"; then
    echo "✅ OpenSearch is accessible at $OPENSEARCH_URL"
else
    echo "⚠️  Cannot connect to OpenSearch at $OPENSEARCH_URL"
    echo "Please ensure OpenSearch is running."
fi

# Start the application
echo ""
echo "🎉 Starting Gradio application..."
echo "📍 Application will be available at: http://localhost:${APP_PORT:-7860}"
echo ""

python app.py
