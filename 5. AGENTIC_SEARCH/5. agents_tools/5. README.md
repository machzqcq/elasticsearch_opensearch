# 🤖 OpenSearch Agent Tools - Complete Guide

## 📚 Overview

This directory contains comprehensive Jupyter notebooks demonstrating all **17 OpenSearch Agent Tools** using **OpenAI GPT models**. Each notebook includes:
- 🎨 Colorful Mermaid diagrams illustrating workflows
- 📖 Step-by-step explanations for students
- 💻 Working code examples with OpenAI integration
- 🎯 Practical use cases and best practices

## 🗂️ Notebook Structure

All notebooks follow a consistent structure:
1. **Mermaid Diagram** - Visual workflow representation
2. **Learning Objectives** - What you'll learn
3. **Tool Introduction** - What the tool does and why it matters
4. **Setup Steps** - Client initialization and configuration
5. **Agent Creation** - Building flow agents with OpenAI
6. **Demonstrations** - Multiple test cases and examples
7. **Key Takeaways** - Summary and best practices
8. **Cleanup** - Resource management

## 🚀 Quick Start

### Prerequisites

```bash
# Install required packages
pip install opensearch-py python-dotenv

# Create .env file in the parent directory (5. AGENTIC_SEARCH/)
echo "OPENAI_API_KEY=your_openai_key_here" > ../.env
```

### Running Notebooks

```python
# All notebooks use the shared helper functions
from agent_helpers import (
    get_os_client,
    configure_cluster_for_openai,
    create_openai_connector,
    register_and_deploy_openai_model,
    create_flow_agent,
    execute_agent
)
```

## 📋 Complete Tool List

### ✅ Complete Notebooks (Fully Implemented)

| Tool | Notebook | Description | Complexity |
|------|----------|-------------|------------|
| **ListIndexTool** | `list_index_tool.ipynb` | List all indices in the cluster with health status | ⭐ Easy |
| **VectorDBTool** | `vector_db_tool.ipynb` | Dense vector semantic search using embeddings | ⭐⭐⭐ Advanced |

### 🔨 To Be Created (Templates Below)

| Tool | Filename | Description | Complexity |
|------|----------|-------------|------------|
| **AgentTool** | `agent_tool.ipynb` | Run one agent from another agent | ⭐⭐ Medium |
| **DataDistributionTool** | `data_distribution_tool.ipynb` | Analyze data distributions and anomalies | ⭐⭐⭐ Advanced |
| **IndexMappingTool** | `index_mapping_tool.ipynb` | Retrieve index mappings and settings | ⭐ Easy |
| **LogPatternTool** | `log_pattern_tool.ipynb` | Extract log patterns from data | ⭐⭐ Medium |
| **LogPatternAnalysisTool** | `log_pattern_analysis_tool.ipynb` | Advanced log sequence analysis | ⭐⭐⭐ Advanced |
| **MLModelTool** | `ml_model_tool.ipynb` | Run ML model inference | ⭐⭐ Medium |
| **NeuralSparseSearchTool** | `neural_sparse_search_tool.ipynb` | Sparse vector retrieval | ⭐⭐⭐ Advanced |
| **QueryPlanningTool** | `query_planning_tool.ipynb` | Generate DSL from natural language | ⭐⭐⭐ Advanced |
| **PPLTool** | `ppl_tool.ipynb` | Translate natural language to PPL queries | ⭐⭐⭐ Advanced |
| **ScratchpadTools** | `scratchpad_tools.ipynb` | Agent memory with read/write | ⭐⭐ Medium |
| **RAGTool** | `rag_tool.ipynb` | Retrieval-Augmented Generation | ⭐⭐⭐ Advanced |
| **SearchIndexTool** | `search_index_tool.ipynb` | Execute DSL queries on indices | ⭐⭐ Medium |
| **VisualizationTool** | `visualization_tool.ipynb` | Find relevant visualizations | ⭐ Easy |
| **WebSearchTool** | `web_search_tool.ipynb` | Search the web using DuckDuckGo/Google | ⭐⭐ Medium |

## 🎨 Mermaid Diagram Color Scheme

All notebooks use a consistent color scheme for visual clarity:

```mermaid
%%{init: {'theme':'base', 'themeVariables': {
  'primaryColor':'#4A90E2',      // Blue - Start/Input
  'primaryTextColor':'#fff',
  'primaryBorderColor':'#2E5C8A',
  'lineColor':'#F39C12',          // Orange - Connections
  'secondaryColor':'#E74C3C',     // Red - Processing
  'tertiaryColor':'#27AE60'       // Green - Results
}}}%%
```

## 📝 Notebook Templates

### Template 1: Simple Tool (No LLM Required)

Tools like ListIndexTool, IndexMappingTool, SearchIndexTool don't require LLM integration.

```python
# Structure for simple tools
1. Import helpers
2. Initialize client
3. Configure cluster (optional)
4. Create flow agent with tool
5. Execute agent
6. Display results
7. Cleanup
```

### Template 2: Semantic Search Tool

Tools like VectorDBTool, NeuralSparseSearchTool, RAGTool require embedding models.

```python
# Structure for semantic search tools
1. Import helpers
2. Initialize client
3. Register embedding model
4. Create ingest pipeline
5. Create vector index
6. Index sample data
7. Create flow agent with tool
8. Execute semantic queries
9. Cleanup
```

### Template 3: LLM-Powered Tool

Tools like MLModelTool, QueryPlanningTool, PPLTool require LLM integration.

```python
# Structure for LLM-powered tools
1. Import helpers
2. Initialize client
3. Create OpenAI connector
4. Register and deploy OpenAI model
5. Create flow agent with tool and model_id
6. Execute agent with natural language
7. Parse LLM responses
8. Cleanup
```

## 🔧 Helper Functions Reference

### `agent_helpers.py` Functions

| Function | Purpose | Returns |
|----------|---------|---------|
| `get_os_client()` | Create OpenSearch client | `OpenSearch` client |
| `configure_cluster_for_openai()` | Configure cluster settings | None |
| `create_openai_connector()` | Create OpenAI API connector | `connector_id` |
| `register_and_deploy_openai_model()` | Deploy OpenAI model | `model_id` |
| `create_flow_agent()` | Create flow agent with tools | `agent_id` |
| `execute_agent()` | Execute agent with parameters | `response` dict |
| `print_agent_response()` | Pretty-print agent output | None |
| `cleanup_resources()` | Delete models/agents/indices | None |
| `wait_for_model_deployment()` | Wait for model deployment | `bool` |

## 📖 Quick Reference: Tool Parameters

### Common Parameters Across Tools

```python
# Flow agent structure
agent_body = {
    "name": "Agent_Name",
    "type": "flow",
    "description": "Agent description",
    "tools": [
        {
            "type": "ToolType",
            "parameters": {
                # Tool-specific parameters
            }
        }
    ]
}
```

### Tool-Specific Parameters

#### VectorDBTool
```python
{
    "type": "VectorDBTool",
    "parameters": {
        "model_id": "<embedding_model_id>",
        "index": "<index_name>",
        "embedding_field": "<vector_field>",
        "source_field": ["<field1>", "<field2>"],
        "input": "${parameters.question}",
        "doc_size": 2,          # Number of results
        "k": 10                 # k-NN parameter
    }
}
```

#### RAGTool
```python
{
    "type": "RAGTool",
    "parameters": {
        "embedding_model_id": "<embedding_model_id>",
        "inference_model_id": "<llm_model_id>",
        "index": "<index_name>",
        "embedding_field": "<vector_field>",
        "source_field": ["<field>"],
        "input": "${parameters.question}",
        "prompt": "System prompt with ${parameters.output_field}"
    }
}
```

#### WebSearchTool
```python
{
    "type": "WebSearchTool",
    "parameters": {
        "engine": "duckduckgo",  # or "google", "bing", "custom"
        "input": "${parameters.question}"
    }
}
```

#### SearchIndexTool
```python
{
    "type": "SearchIndexTool",
    "parameters": {
        "input": "{\"index\": \"${parameters.index}\", \"query\": ${parameters.query}}"
    }
}
```

## 🎯 Learning Path

### Beginner (⭐)
Start with these tools to understand basics:
1. **ListIndexTool** - Simple index discovery
2. **IndexMappingTool** - Understanding index structures
3. **VisualizationTool** - Finding visualizations

### Intermediate (⭐⭐)
Build on fundamentals:
1. **SearchIndexTool** - Execute DSL queries
2. **MLModelTool** - ML model integration
3. **WebSearchTool** - External data sources
4. **AgentTool** - Agent composition

### Advanced (⭐⭐⭐)
Master complex workflows:
1. **VectorDBTool** - Dense vector search
2. **NeuralSparseSearchTool** - Sparse vector search
3. **RAGTool** - RAG pipelines
4. **QueryPlanningTool** - Natural language to DSL
5. **PPLTool** - PPL query generation
6. **LogPatternAnalysisTool** - Advanced log analysis
7. **DataDistributionTool** - Data analysis

## 🌟 Best Practices

### 1. Resource Management
```python
# Always clean up after demos
cleanup_resources(
    client=client,
    model_ids=[model_id],
    agent_ids=[agent_id],
    index_names=[index_name]
)
```

### 2. Error Handling
```python
try:
    response = execute_agent(client, agent_id, parameters)
except Exception as e:
    print(f"Error: {e}")
```

### 3. Model Deployment
```python
# Always wait for model deployment before using
wait_for_model_deployment(client, model_id)
```

### 4. Environment Variables
```bash
# Never commit API keys
# Use .env files
OPENAI_API_KEY=sk-...
```

## 🔍 Troubleshooting

### Common Issues

**Issue**: "Model not deployed"
```python
# Solution: Wait for deployment
wait_for_model_deployment(client, model_id, timeout=600)
```

**Issue**: "Connector endpoint not trusted"
```python
# Solution: Configure cluster settings
configure_cluster_for_openai(client)
```

**Issue**: "Agent returns empty results"
```python
# Solution: Check index has data and embeddings are generated
client.indices.refresh(index=index_name)
```

## 📚 Additional Resources

- [OpenSearch ML Commons Documentation](https://docs.opensearch.org/latest/ml-commons-plugin/)
- [OpenSearch Agent Tools Reference](https://docs.opensearch.org/latest/ml-commons-plugin/agents-tools/tools/)
- [OpenAI API Documentation](https://platform.openai.com/docs/)
- [Vector Search Guide](https://docs.opensearch.org/latest/search-plugins/neural-search/)

## 🤝 Contributing

When creating new notebooks:
1. Follow the established structure
2. Use consistent color schemes in Mermaid diagrams
3. Include comprehensive comments
4. Test all code cells
5. Add cleanup section
6. Update this README

## 📄 License

These notebooks are part of the OpenSearch educational materials.

## 🎓 Course Context

These notebooks are designed for students learning:
- OpenSearch fundamentals
- Agent-based AI systems
- Semantic search and RAG
- ML model integration
- Natural language processing

Each notebook builds on concepts from previous lessons while introducing new capabilities.

---

**Created by**: OpenSearch Course Team  
**Last Updated**: November 2025  
**Version**: 1.0

For questions or issues, please refer to the course materials or OpenSearch community forums.
