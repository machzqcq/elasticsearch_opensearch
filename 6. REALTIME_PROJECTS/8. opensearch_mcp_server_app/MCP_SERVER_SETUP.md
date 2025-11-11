# MCP Server Startup Guide

## Quick Start

### Option 1: Using the Helper Script (Recommended)
```bash
python start_mcp_server.py
```

This will:
- Load environment variables from `.env`
- Use `mcp_server_config.yaml` for OpenSearch connection
- Start the server on port 9900
- Wait for server to be ready

### Option 2: Manual Start with Config File
```bash
python -m mcp_server_opensearch --transport stream --port 9900 --config mcp_server_config.yaml
```

### Option 3: Using Environment Variables
```bash
# Load .env first
export $(cat .env | grep -v '^#' | xargs)

# Start server
python -m mcp_server_opensearch --transport stream --port 9900
```

## Configuration

### mcp_server_config.yaml
The MCP server reads OpenSearch connection details from this file:

```yaml
opensearch:
  url: https://localhost:9200
  username: admin
  password: Developer@123
  ssl_verify: false
```

**Important**: The `mcp_server_config.yaml` file has been created with values from your `.env` file.

### Environment Variables (Alternative)
If you don't use the config file, the MCP server will read from environment variables:
- `OPENSEARCH_URL`
- `OPENSEARCH_USERNAME`
- `OPENSEARCH_PASSWORD`
- `OPENSEARCH_SSL_VERIFY`

## Troubleshooting

### Server Not Finding OpenSearch
If you see errors like "OpenSearch URL must be provided", make sure:

1. **Using config file** (recommended):
   ```bash
   python -m mcp_server_opensearch --transport stream --port 9900 --config mcp_server_config.yaml
   ```

2. **Or set environment variables**:
   ```bash
   export OPENSEARCH_URL=https://localhost:9200
   export OPENSEARCH_USERNAME=admin
   export OPENSEARCH_PASSWORD=Developer@123
   export OPENSEARCH_SSL_VERIFY=false
   python -m mcp_server_opensearch --transport stream --port 9900
   ```

### Port Already in Use
```bash
# Find process using port 9900
lsof -ti:9900

# Kill it
lsof -ti:9900 | xargs kill -9
```

### Check Server Health
```bash
curl http://localhost:9900/health
```

## Complete Startup Flow

### Terminal 1: Start MCP Server
```bash
cd opensearch_mcp_server_app
python start_mcp_server.py
```

Wait for: `✅ MCP Server is ready!`

### Terminal 2: Start Gradio App
```bash
cd opensearch_mcp_server_app
python app.py
```

Then open: http://localhost:7860

## Configuration Files

- `.env` - Environment variables for the Gradio app
- `mcp_server_config.yaml` - OpenSearch connection for MCP server
- Both files use the same OpenSearch credentials

## Notes

- The MCP server runs independently of the Gradio app
- You must start the MCP server BEFORE the Gradio app
- The config file approach is more reliable than environment variables
- Keep the MCP server terminal open while using the app
