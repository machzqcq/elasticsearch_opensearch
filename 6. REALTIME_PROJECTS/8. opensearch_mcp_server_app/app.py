"""
OpenSearch MCP Server - Educational Demo Application

An interactive Gradio application for learning and exploring OpenSearch
through natural language queries powered by MCP and GPT-4.
"""

import gradio as gr
import asyncio
from typing import Tuple
from config import initialize_settings
from mcp_client import get_mcp_client, execute_query


# Initialize settings
settings = initialize_settings()

# Educational content and examples
WELCOME_TEXT = """
# 🎓 Welcome to OpenSearch MCP Server Educational Demo

This interactive application teaches you how to work with OpenSearch using **natural language**!

## What is this?

Instead of writing complex JSON queries, you can simply ask questions like:
- "Show me all indices in the cluster"
- "Find customers named John"
- "What's the cluster health status?"

## How it works

```mermaid
graph LR
    A[Your Question] --> B[AI Agent]
    B --> C[MCP Server]
    C --> D[OpenSearch]
    D --> E[Results]
    E --> B
    B --> F[Natural Language Answer]
```

## Getting Started

1. **Choose a tab** based on what you want to learn
2. **Read the concept** explanation
3. **Try the examples** provided
4. **Experiment** with your own queries!

### Available Tabs

- 🗂️ **Index Management** - Create, list, and manage indices
- 📄 **Document Operations** - Add, retrieve, and delete documents
- 🔍 **Search & Query** - Search data with filters and aggregations
- 🏥 **Cluster Management** - Monitor cluster health and statistics
- 🔧 **Advanced Features** - Aliases, data streams, and custom APIs

## Prerequisites

✅ OpenSearch cluster running  
✅ MCP server started (`python -m mcp_server_opensearch --transport stream`)  
✅ OpenAI API key configured  

Ready to start learning? Choose a tab above! 👆
"""


async def initialize_app():
    """Initialize MCP client on app startup."""
    try:
        client = await get_mcp_client()
        tools = client.get_tools_info()
        return f"✅ Connected! Found {len(tools)} tools available."
    except Exception as e:
        return f"❌ Connection failed: {e}"


async def process_query(question: str, show_details: bool = True) -> Tuple[str, str]:
    """
    Process a natural language query.
    
    Args:
        question: Natural language query
        show_details: Show execution details
        
    Returns:
        Tuple of (result, details)
    """
    if not question.strip():
        return "⚠️ Please enter a question.", ""
    
    try:
        result = await execute_query(question, verbose=show_details)
        
        if result["success"]:
            output = f"""## ✅ Success

{result['result']}
"""
            details = ""
            if show_details and result["metadata"]:
                details = f"""### 🔍 Execution Details

**Tool Calls**: {result['metadata'].get('tool_calls', 0)}

**Process**:
1. Question analyzed by GPT-4
2. Appropriate MCP tool(s) selected
3. Query executed against OpenSearch
4. Results formatted as natural language
"""
            return output, details
        else:
            error_msg = f"""## ❌ Error

{result['error']}

### 💡 Tips:
- Check if your OpenSearch cluster is running
- Verify the MCP server is active
- Ensure your query is clear and specific
"""
            return error_msg, ""
            
    except Exception as e:
        return f"❌ Unexpected error: {e}", ""


# Tab 1: Index Management
def create_index_management_tab():
    """Create the Index Management tab."""
    
    with gr.Tab("🗂️ Index Management"):
        gr.Markdown("""
## Index Management

### What is an Index?

An **index** in OpenSearch is like a database table - it stores documents with a specific structure.

```mermaid
graph TD
    A[Index] --> B[Mappings]
    A --> C[Settings]
    A --> D[Documents]
    
    B --> B1[Field Types]
    B --> B2[Analyzers]
    
    C --> C1[Shards]
    C --> C2[Replicas]
    
    D --> D1[Document 1]
    D --> D2[Document 2]
    D --> D3[Document N]
    
    style A fill:#4CAF50,color:#fff
    style B fill:#2196F3,color:#fff
    style C fill:#FF9800,color:#fff
    style D fill:#9C27B0,color:#fff
```

### Key Concepts

- **Mappings**: Define field types (text, keyword, date, number)
- **Settings**: Configure shards, replicas, and analyzers
- **Documents**: Individual records stored in the index

### Available Operations

1. **List Indices** - See all indices in your cluster
2. **Get Index Details** - View mappings and settings
3. **Create Index** - Set up a new index with custom configuration
4. **Delete Index** - Remove an index (use carefully!)
""")
        
        with gr.Row():
            with gr.Column():
                query_input = gr.Textbox(
                    label="Your Question",
                    placeholder="e.g., 'List all indices in the cluster'",
                    lines=3
                )
                show_details = gr.Checkbox(
                    label="Show execution details",
                    value=True
                )
                submit_btn = gr.Button("🚀 Execute Query", variant="primary")
                
                gr.Markdown("### 💡 Example Queries")
                examples = gr.Examples(
                    examples=[
                        ["List all indices in the OpenSearch cluster"],
                        ["Show me detailed information about the ecommerce index"],
                        ["Create a new index called 'products' with fields: name (text), price (float), category (keyword)"],
                        ["How many documents are in the ecommerce index?"],
                    ],
                    inputs=query_input
                )
            
            with gr.Column():
                result_output = gr.Markdown(label="Result")
                details_output = gr.Markdown(label="Details")
        
        submit_btn.click(
            fn=process_query,
            inputs=[query_input, show_details],
            outputs=[result_output, details_output]
        )


# Tab 2: Document Operations
def create_document_operations_tab():
    """Create the Document Operations tab."""
    
    with gr.Tab("📄 Document Operations"):
        gr.Markdown("""
## Document Operations (CRUD)

### What is a Document?

A **document** is a JSON object containing data - like a row in a database table.

```mermaid
graph LR
    A[Document Operations] --> B[Create]
    A --> C[Read]
    A --> D[Update]
    A --> E[Delete]
    
    B --> F[Index Document<br/>PUT /index/_doc/id]
    C --> G[Get Document<br/>GET /index/_doc/id]
    D --> H[Update Document<br/>POST /index/_update/id]
    E --> I[Delete Document<br/>DELETE /index/_doc/id]
    
    style A fill:#4CAF50,color:#fff
    style B fill:#2196F3,color:#fff
    style C fill:#FF9800,color:#fff
    style D fill:#9C27B0,color:#fff
    style E fill:#F44336,color:#fff
```

### Operations Explained

**CREATE (Index)**
- Add a new document with a specific ID
- If ID exists, document is updated

**READ (Get)**
- Retrieve a document by its ID
- Fast O(1) lookup

**UPDATE**
- Modify an existing document
- Can be partial (only changed fields)

**DELETE**
- Remove document by ID
- Or delete multiple documents matching a query
""")
        
        with gr.Row():
            with gr.Column():
                query_input = gr.Textbox(
                    label="Your Question",
                    placeholder="e.g., 'Add a product with name=Laptop, price=999'",
                    lines=3
                )
                show_details = gr.Checkbox(
                    label="Show execution details",
                    value=True
                )
                submit_btn = gr.Button("🚀 Execute Query", variant="primary")
                
                gr.Markdown("### 💡 Example Queries")
                examples = gr.Examples(
                    examples=[
                        ["Add a document to ecommerce index with ID 'test_001': customer_name='John Doe', total=150.00"],
                        ["Retrieve the document with ID 'test_001' from ecommerce index"],
                        ["Add 3 sample products to test_products index with auto-generated IDs"],
                        ["Delete all documents from test_products where category is 'Electronics'"],
                        ["Get the first 5 documents from the ecommerce index"],
                    ],
                    inputs=query_input
                )
            
            with gr.Column():
                result_output = gr.Markdown(label="Result")
                details_output = gr.Markdown(label="Details")
        
        submit_btn.click(
            fn=process_query,
            inputs=[query_input, show_details],
            outputs=[result_output, details_output]
        )


# Tab 3: Search & Query
def create_search_query_tab():
    """Create the Search & Query tab."""
    
    with gr.Tab("🔍 Search & Query"):
        gr.Markdown("""
## Search & Query Operations

### Query Types

OpenSearch provides powerful search capabilities beyond simple lookups.

```mermaid
graph TB
    A[Query Types] --> B[Match Query]
    A --> C[Term Query]
    A --> D[Range Query]
    A --> E[Bool Query]
    A --> F[Aggregations]
    
    B --> G[Full-text search<br/>Analyzed fields]
    C --> H[Exact match<br/>Keywords]
    D --> I[Numeric/Date ranges<br/>gte, lte, gt, lt]
    E --> J[Combine queries<br/>must, should, must_not]
    F --> K[Analytics<br/>Group, sum, avg]
    
    style A fill:#4CAF50,color:#fff
    style B fill:#2196F3,color:#fff
    style C fill:#FF9800,color:#fff
    style D fill:#9C27B0,color:#fff
    style E fill:#00BCD4,color:#fff
    style F fill:#F44336,color:#fff
```

### Search Concepts

**Match Query**
- Full-text search with analysis
- Finds relevant documents
- Best for text fields

**Term Query**
- Exact match (case-sensitive)
- Best for keywords, IDs

**Range Query**
- Numeric or date ranges
- Operators: gte, gt, lte, lt

**Bool Query**
- Combine multiple conditions
- must (AND), should (OR), must_not (NOT)

**Aggregations**
- Group by field values
- Calculate metrics (sum, avg, max, min)
- Like SQL GROUP BY
""")
        
        with gr.Row():
            with gr.Column():
                query_input = gr.Textbox(
                    label="Your Question",
                    placeholder="e.g., 'Find all orders over $100'",
                    lines=3
                )
                show_details = gr.Checkbox(
                    label="Show execution details",
                    value=True
                )
                submit_btn = gr.Button("🚀 Execute Query", variant="primary")
                
                gr.Markdown("### 💡 Example Queries")
                examples = gr.Examples(
                    examples=[
                        ["Find all customers with first name 'Mary' in the ecommerce index"],
                        ["Search for orders where gender is FEMALE and total > 100, return 5 results"],
                        ["Find orders between 2024-06-01 and 2024-12-31 with total between 50 and 200"],
                        ["Show me the top 5 categories by order count with average order value"],
                        ["Find all products where name starts with 'Shirt'"],
                        ["Group ecommerce orders by gender and show count and average total for each"],
                    ],
                    inputs=query_input
                )
            
            with gr.Column():
                result_output = gr.Markdown(label="Result")
                details_output = gr.Markdown(label="Details")
        
        submit_btn.click(
            fn=process_query,
            inputs=[query_input, show_details],
            outputs=[result_output, details_output]
        )


# Tab 4: Cluster Management
def create_cluster_management_tab():
    """Create the Cluster Management tab."""
    
    with gr.Tab("🏥 Cluster Management"):
        gr.Markdown("""
## Cluster Health & Statistics

### Cluster Architecture

```mermaid
graph TB
    A[Master Node]
    B[Data Node 1]
    C[Data Node 2]
    D[Data Node 3]
    E[Shard 0 Primary]
    F[Shard 0 Replica]
    G[Shard 1 Primary]
    H[Shard 1 Replica]
    
    A -->|Manages| B
    A -->|Manages| C
    A -->|Manages| D
    
    B -->|Hosts| E
    C -->|Hosts| F
    B -->|Hosts| G
    D -->|Hosts| H
    
    style A fill:#F44336,color:#fff
    style B fill:#4CAF50,color:#fff
    style C fill:#4CAF50,color:#fff
    style D fill:#4CAF50,color:#fff
    style E fill:#2196F3,color:#fff
    style F fill:#2196F3,color:#fff
    style G fill:#2196F3,color:#fff
    style H fill:#2196F3,color:#fff
```

### Health Status Colors

🟢 **GREEN**: All good!
- All primary and replica shards allocated
- Cluster is fully operational

🟡 **YELLOW**: Caution
- All primary shards allocated
- Some replica shards missing
- Data is safe but no redundancy

🔴 **RED**: Critical
- Some primary shards unallocated
- Data loss possible
- Immediate action required

### Key Metrics

- **Nodes**: Number of servers in cluster
- **Shards**: Data partitions (primary + replicas)
- **Documents**: Total indexed documents
- **Storage**: Disk space used
""")
        
        with gr.Row():
            with gr.Column():
                query_input = gr.Textbox(
                    label="Your Question",
                    placeholder="e.g., 'What is the cluster health?'",
                    lines=3
                )
                show_details = gr.Checkbox(
                    label="Show execution details",
                    value=True
                )
                submit_btn = gr.Button("🚀 Execute Query", variant="primary")
                
                gr.Markdown("### 💡 Example Queries")
                examples = gr.Examples(
                    examples=[
                        ["What is the health status of the OpenSearch cluster?"],
                        ["Show me cluster statistics: nodes, documents, storage size"],
                        ["How many indices are in the cluster?"],
                        ["What is the status of each node in the cluster?"],
                        ["Show disk usage across all nodes"],
                    ],
                    inputs=query_input
                )
            
            with gr.Column():
                result_output = gr.Markdown(label="Result")
                details_output = gr.Markdown(label="Details")
        
        submit_btn.click(
            fn=process_query,
            inputs=[query_input, show_details],
            outputs=[result_output, details_output]
        )


# Tab 5: Advanced Features
def create_advanced_features_tab():
    """Create the Advanced Features tab."""
    
    with gr.Tab("🔧 Advanced Features"):
        gr.Markdown("""
## Advanced Features

### Aliases

**What are aliases?**

Aliases are alternative names for indices, enabling zero-downtime operations.

```mermaid
graph LR
    A[Application] --> B[Alias: 'products']
    B --> C[Index: products_v1]
    B -.Switch.-> D[Index: products_v2]
    
    style B fill:#4CAF50,color:#fff
    style C fill:#2196F3,color:#fff
    style D fill:#FF9800,color:#fff
```

**Use Cases:**
- Blue-green deployments
- Index versioning
- Multi-tenant applications

### Data Streams

**What are data streams?**

Specialized indices for time-series data (logs, metrics, events).

```mermaid
graph TD
    A[Data Stream: logs-app] --> B[Backing Index 1<br/>2024-01]
    A --> C[Backing Index 2<br/>2024-02]
    A --> D[Backing Index 3<br/>2024-03]
    
    B --> E[Rollover Policy]
    E --> F[30 days old]
    E --> G[50GB size]
    E --> H[Delete after 90 days]
    
    style A fill:#4CAF50,color:#fff
    style B fill:#2196F3,color:#fff
    style C fill:#2196F3,color:#fff
    style D fill:#2196F3,color:#fff
```

**Features:**
- Automatic rollover
- Lifecycle management
- Optimized for append-only data

### Custom API Calls

The `general_api_request` tool allows any OpenSearch API call not covered by specific tools.
""")
        
        with gr.Row():
            with gr.Column():
                query_input = gr.Textbox(
                    label="Your Question",
                    placeholder="e.g., 'Create an alias called orders pointing to ecommerce'",
                    lines=3
                )
                show_details = gr.Checkbox(
                    label="Show execution details",
                    value=True
                )
                submit_btn = gr.Button("🚀 Execute Query", variant="primary")
                
                gr.Markdown("### 💡 Example Queries")
                examples = gr.Examples(
                    examples=[
                        ["Create an alias 'orders' that points to the 'ecommerce' index"],
                        ["List all aliases in the cluster and which indices they point to"],
                        ["Delete the alias 'orders' from the ecommerce index"],
                        ["List all data streams in the cluster"],
                        ["Use cat API to show all indices with document count, sorted by count"],
                        ["Update ecommerce index settings: set refresh_interval to 30s"],
                    ],
                    inputs=query_input
                )
            
            with gr.Column():
                result_output = gr.Markdown(label="Result")
                details_output = gr.Markdown(label="Details")
        
        submit_btn.click(
            fn=process_query,
            inputs=[query_input, show_details],
            outputs=[result_output, details_output]
        )


# Create main application
def create_app():
    """Create the main Gradio application."""
    
    with gr.Blocks(
        title=settings.app_title,
        theme=gr.themes.Soft(
            primary_hue="blue",
            secondary_hue="green",
        ),
        css="""
        .gradio-container {
            max-width: 1400px !important;
        }
        .tab-nav button {
            font-size: 16px !important;
            font-weight: 600 !important;
        }
        """
    ) as app:
        
        # Header
        gr.Markdown(f"# {settings.app_title}")
        
        # Status indicator
        status = gr.Textbox(
            label="Connection Status",
            value="⏳ Initializing...",
            interactive=False,
            max_lines=1
        )
        
        # Welcome tab
        with gr.Tab("🏠 Welcome"):
            gr.Markdown(WELCOME_TEXT)
            
            with gr.Accordion("📋 Available Tools", open=False):
                gr.Markdown("""
### MCP Tools Available

| Tool | Category | Description |
|------|----------|-------------|
| list_indices | Index Management | List all indices |
| get_index | Index Management | Get index details |
| create_index | Index Management | Create new index |
| delete_index | Index Management | Delete index |
| index_document | Document Operations | Add/update document |
| get_document | Document Operations | Retrieve by ID |
| delete_document | Document Operations | Remove by ID |
| delete_by_query | Document Operations | Bulk delete |
| search_documents | Search & Query | Query documents |
| get_cluster_health | Cluster Management | Check health |
| get_cluster_stats | Cluster Management | Get statistics |
| list_aliases | Advanced | List aliases |
| get_alias | Advanced | Get index aliases |
| put_alias | Advanced | Create alias |
| delete_alias | Advanced | Remove alias |
| create_data_stream | Advanced | Create data stream |
| get_data_stream | Advanced | Get stream info |
| delete_data_stream | Advanced | Delete stream |
| general_api_request | Advanced | Custom API call |
""")
        
        # Create all tabs
        create_index_management_tab()
        create_document_operations_tab()
        create_search_query_tab()
        create_cluster_management_tab()
        create_advanced_features_tab()
        
        # Footer
        gr.Markdown("""
---
### 📚 Resources

- [OpenSearch Documentation](https://opensearch.org/docs/)
- [MCP Server GitHub](https://github.com/opensearch-project/opensearch-mcp-server-py)
- [LangChain Documentation](https://python.langchain.com/)

### 💡 Tips

- Start with simple queries and build up complexity
- Read the concept explanations in each tab
- Experiment with the example queries
- Check "Show execution details" to see how queries work

**Made with ❤️ using Gradio, LangChain, and OpenSearch MCP Server**
""")
        
        # Initialize on load
        app.load(
            fn=initialize_app,
            inputs=None,
            outputs=status
        )
    
    return app


# Main entry point
if __name__ == "__main__":
    print("🚀 Starting OpenSearch MCP Server Educational Demo...")
    print(f"📍 Application will be available at: http://localhost:{settings.app_port}")
    print(f"🔗 MCP Server URL: {settings.mcp_server_url}")
    print(f"🗄️ OpenSearch URL: {settings.opensearch_url}")
    print()
    
    app = create_app()
    app.launch(
        server_name="0.0.0.0",
        server_port=settings.app_port,
        share=settings.app_share,
        show_api=False
    )
