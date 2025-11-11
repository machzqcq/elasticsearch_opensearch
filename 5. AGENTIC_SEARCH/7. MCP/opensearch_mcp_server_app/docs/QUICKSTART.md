# Quick Start Guide

Get the OpenSearch MCP Server Educational Demo running in 5 minutes!

## Prerequisites Checklist

- [ ] Python 3.10 or higher installed
- [ ] OpenSearch cluster running (or Docker)
- [ ] OpenAI API key

## Step-by-Step Setup

### 1. Install Dependencies

```bash
# Navigate to the app directory
cd opensearch_mcp_server_app

# Install using uv (recommended)
pip install uv
uv sync

# Or using pip
pip install -e .
```

### 2. Configure Environment

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env file with your settings
nano .env  # or use your favorite editor
```

Required settings:
```env
OPENAI_API_KEY=sk-your-key-here
OPENSEARCH_URL=https://localhost:9200
OPENSEARCH_USERNAME=admin
OPENSEARCH_PASSWORD=your-password
```

### 3. Start OpenSearch (if not running)

**Option A: Using Docker**
```bash
# From the parent directory
cd ../..
docker compose -f docker-compose-opensearch-single.yml up -d
```

**Option B: Already running**
Skip to next step!

### 4. Start MCP Server

Open a **new terminal** and run:

```bash
cd opensearch_mcp_server_app
python start_mcp_server.py
```

Keep this terminal open! You should see:
```
✅ MCP Server started (PID: 12345)
✅ MCP Server is ready!
```

### 5. Start the Gradio App

In your **original terminal**:

```bash
python app.py
```

You should see:
```
🚀 Starting OpenSearch MCP Server Educational Demo...
📍 Application will be available at: http://localhost:7860
Running on local URL:  http://0.0.0.0:7860
```

### 6. Open in Browser

Open your browser and navigate to:
```
http://localhost:7860
```

🎉 **Success!** You should see the welcome screen.

## Using the One-Line Startup (Linux/Mac)

```bash
chmod +x start.sh
./start.sh
```

This script will:
1. Check prerequisites
2. Install dependencies
3. Verify MCP server is running
4. Start the Gradio app

## First Steps in the App

1. **Check Connection Status**
   - Look for "✅ Connected!" message at the top
   - Shows number of available tools

2. **Try the Welcome Tab**
   - Read the introduction
   - Understand the architecture

3. **Navigate to Index Management Tab**
   - Try: "List all indices in the cluster"
   - See the natural language response

4. **Experiment with Examples**
   - Each tab has example queries
   - Click to populate the input field
   - Press "Execute Query"

## Troubleshooting

### "MCP server not responding"

```bash
# Check if MCP server is running
curl http://localhost:9900/health

# If not, restart it
python start_mcp_server.py
```

### "Cannot connect to OpenSearch"

```bash
# Check if OpenSearch is accessible
curl -k https://localhost:9200

# Check credentials in .env file
```

### "OpenAI API Error"

```bash
# Verify API key
echo $OPENAI_API_KEY

# Check API key is valid
curl https://api.openai.com/v1/models \
  -H "Authorization: Bearer $OPENAI_API_KEY"
```

### Port Already in Use

```bash
# Change APP_PORT in .env
APP_PORT=7861

# Or kill existing process
lsof -ti:7860 | xargs kill -9
```

## Architecture at a Glance

```
┌─────────────┐
│   Browser   │  ← You interact here
└──────┬──────┘
       │
┌──────▼──────┐
│ Gradio App  │  ← Port 7860
│  (app.py)   │
└──────┬──────┘
       │
┌──────▼──────┐
│ MCP Client  │  ← Translates questions
└──────┬──────┘
       │
┌──────▼──────┐
│ MCP Server  │  ← Port 9900
└──────┬──────┘
       │
┌──────▼──────┐
│ OpenSearch  │  ← Port 9200
└─────────────┘
```

## Next Steps

### Learn the Basics
1. Read "Index Management" tab
2. Try creating an index
3. Add some documents
4. Search the data

### Explore Features
1. Try different query types
2. Use aggregations
3. Check cluster health
4. Create aliases

### Advanced
1. Read the documentation in `docs/`
2. Customize queries
3. Explore all 18+ tools
4. Build your own workflows

## Getting Help

### Documentation
- `README.md` - Project overview
- `docs/BUSINESS_ARCHITECTURE.md` - Business concepts
- `docs/TECHNICAL_ARCHITECTURE.md` - Technical details

### Check Logs
```bash
# App logs (in terminal running app.py)
# MCP server logs (in terminal running start_mcp_server.py)
```

### Common Questions

**Q: Do I need to restart the app to apply .env changes?**
A: Yes, both MCP server and Gradio app.

**Q: Can I use a different LLM?**
A: The app currently uses GPT-4o. To use other models, modify `config.py`.

**Q: Is my data sent to OpenAI?**
A: Only query results (not raw data) are sent for formatting into natural language.

**Q: Can I add custom queries?**
A: Yes! Use the query input box to ask any question.

## Development Mode

### Enable Debug Mode

```python
# In app.py, add at the top:
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Test Individual Components

```bash
# Test MCP client
python -c "import asyncio; from mcp_client import get_mcp_client; asyncio.run(get_mcp_client())"

# Test configuration
python -c "from config import get_settings; print(get_settings())"
```

## Production Deployment

For production use, consider:

1. **Use a reverse proxy** (nginx, Apache)
2. **Enable authentication** in Gradio
3. **Set up monitoring** (Prometheus, Grafana)
4. **Configure SSL/TLS** for all connections
5. **Use environment-specific configs**
6. **Set up logging** to files
7. **Run as a systemd service**

See `docs/TECHNICAL_ARCHITECTURE.md` for deployment details.

## Success Checklist

- [ ] App loads without errors
- [ ] Connection status shows "✅ Connected!"
- [ ] Can list indices
- [ ] Queries return results
- [ ] Examples work correctly
- [ ] All tabs are accessible

✅ **All checked?** You're ready to explore! 🎉

## Useful Commands

```bash
# Start everything (Linux/Mac)
./start.sh

# Start MCP server only
python start_mcp_server.py

# Start Gradio app only
python app.py

# Run with custom port
APP_PORT=8080 python app.py

# Check MCP server health
curl http://localhost:9900/health

# View available tools
python -c "import asyncio; from mcp_client import get_mcp_client; client = asyncio.run(get_mcp_client()); print(client.get_tools_info())"
```

## Resources

- 📚 [OpenSearch Docs](https://opensearch.org/docs/)
- 🔧 [MCP Server GitHub](https://github.com/opensearch-project/opensearch-mcp-server-py)
- 🤖 [LangChain Docs](https://python.langchain.com/)
- 🎨 [Gradio Docs](https://gradio.app/docs/)

---

**Ready to learn OpenSearch the natural language way? Let's go! 🚀**
