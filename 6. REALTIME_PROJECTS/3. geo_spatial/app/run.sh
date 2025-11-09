#!/bin/bash

# Quick start script for the Geospatial Learning App

echo "🌍 OpenSearch Geospatial Learning App"
echo "====================================="
echo ""

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo "❌ uv is not installed. Please install it first:"
    echo "   curl -LsSf https://astral.sh/uv/install.sh | sh"
    exit 1
fi

echo "✓ uv is installed"
echo ""

# Sync dependencies
echo "📦 Installing dependencies..."
uv sync
echo ""

# Run the app
echo "🚀 Starting Gradio app..."
echo "   Access the app at: http://localhost:7860"
echo ""
uv run python app.py
