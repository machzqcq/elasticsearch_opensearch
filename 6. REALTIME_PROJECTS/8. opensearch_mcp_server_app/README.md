# OpenSearch MCP Server - Educational Demo App

An interactive Gradio application demonstrating all features of the OpenSearch MCP Server with natural language querying capabilities.

## Quick Start

### 1. Prerequisites

- Python 3.10+
- OpenSearch cluster running (default: https://localhost:9200)
- OpenAI API key
- UV package manager

### 2. Installation

```bash
# Install dependencies using uv
uv sync

# Or if you don't have uv
pip install -e .
```

### 3. Configuration

Create a `.env` file:

```env
OPENSEARCH_URL=https://localhost:9200
OPENSEARCH_USERNAME=admin
OPENSEARCH_PASSWORD=Developer@123
OPENSEARCH_SSL_VERIFY=false
OPENAI_API_KEY=your_openai_api_key_here
MCP_SERVER_PORT=9900
```

### 4. Run the Application

```bash
# Start the MCP server (in a separate terminal)
python -m mcp_server_opensearch --transport stream --port 9900

# Run the Gradio app
python app.py
```

The app will be available at http://localhost:7860

## Features

- 🎓 **Educational Interface**: Learn OpenSearch MCP concepts through interactive examples
- 🔍 **Natural Language Queries**: Ask questions in plain English
- 📊 **Organized Tabs**: Queries grouped by category (Index Management, Documents, Search, etc.)
- 📈 **Visual Explanations**: Mermaid diagrams showing request flow
- 💡 **Code Examples**: See the queries being generated
- 🎨 **Beautiful UI**: Modern Gradio interface with syntax highlighting

## Documentation

See the `docs/` folder for:
- Business Architecture Guide
- Technical Architecture Guide
- API Reference
- Query Examples

## Tab Organization

1. **Index Management** - Create, list, and manage indices
2. **Document Operations** - CRUD operations on documents
3. **Search & Query** - Full-text search, aggregations, filters
4. **Cluster Management** - Health checks, statistics
5. **Advanced Features** - Aliases, data streams, custom APIs

## Educational Features

Each tab includes:
- Concept explanations
- Parameter descriptions
- Interactive examples
- Visual workflow diagrams
- Best practices
