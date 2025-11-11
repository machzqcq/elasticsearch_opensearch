# OpenSearch MCP Server - Technical Architecture

## System Overview

The OpenSearch MCP Server Educational App is a Python-based web application that bridges natural language processing with OpenSearch operations through the Model Context Protocol (MCP).

## Architecture Diagram

```mermaid
graph TB
    subgraph "Presentation Layer"
        A[Gradio Web UI<br/>Port 7860]
        B[HTML/CSS/JS<br/>Auto-generated]
    end
    
    subgraph "Application Layer"
        C[app.py<br/>Main Application]
        D[mcp_client.py<br/>MCP Client Wrapper]
        E[config.py<br/>Configuration Manager]
    end
    
    subgraph "AI Integration Layer"
        F[LangChain Agent<br/>Orchestration]
        G[OpenAI GPT-4o<br/>LLM]
        H[Tool Registry<br/>18+ Tools]
    end
    
    subgraph "MCP Protocol Layer"
        I[MCP Client<br/>langchain-mcp-adapters]
        J[SSE Transport<br/>HTTP Streaming]
        K[MCP Server<br/>opensearch-mcp-server-py<br/>Port 9900]
    end
    
    subgraph "Data Layer"
        L[OpenSearch Client<br/>opensearch-py]
        M[OpenSearch Cluster<br/>Port 9200]
        N[(Indices & Documents)]
    end
    
    A -->|User Input| C
    C -->|Query Request| D
    D -->|Natural Language| F
    F <-->|Function Calling| G
    G -->|Tool Selection| H
    H -->|Tool Call| I
    I <-->|SSE Stream| J
    J <-->|HTTP| K
    K -->|REST API| L
    L <-->|CRUD| M
    M <-->|Data| N
    N -->|Results| M
    M -->|Response| L
    L -->|JSON| K
    K -->|Tool Result| J
    J -->|SSE| I
    I -->|Data| H
    H -->|Answer| G
    G -->|NL Response| F
    F -->|Output| D
    D -->|Formatted| C
    C -->|Display| A
    
    style A fill:#e1f5ff,stroke:#0066cc,stroke-width:3px
    style G fill:#fff9e6,stroke:#ff9900,stroke-width:3px
    style K fill:#e8f5e9,stroke:#2e7d32,stroke-width:3px
    style M fill:#fce4ec,stroke:#c2185b,stroke-width:3px
```

## Component Details

### 1. Presentation Layer

#### Gradio Web UI
```python
# Technology: Gradio 4.44+
# Features:
- Tab-based interface
- Markdown rendering
- Code syntax highlighting
- Interactive examples
- Real-time updates
```

**Capabilities:**
- Responsive design
- WebSocket support
- File upload/download
- Custom CSS themes

### 2. Application Layer

#### Main Application (app.py)
```mermaid
flowchart LR
    A[app.py] --> B[UI Layout]
    A --> C[Event Handlers]
    A --> D[State Management]
    
    B --> B1[Tab Definitions]
    B --> B2[Component Layouts]
    B --> B3[Styling]
    
    C --> C1[Query Submission]
    C --> C2[Result Display]
    C --> C3[Error Handling]
    
    D --> D1[Session State]
    D --> D2[Query History]
    D --> D3[Settings]
    
    style A fill:#4CAF50,color:#fff
    style B fill:#2196F3,color:#fff
    style C fill:#FF9800,color:#fff
    style D fill:#9C27B0,color:#fff
```

#### MCP Client Wrapper (mcp_client.py)
```python
class MCPClient:
    """
    Singleton pattern for MCP server communication
    """
    def __init__(self):
        self.client = None
        self.llm = None
        self.tools = None
    
    async def initialize(self):
        """Connect to MCP server and load tools"""
        
    async def query(self, question: str, verbose: bool = False):
        """Execute natural language query"""
        
    def get_tools_info(self):
        """Return metadata about available tools"""
```

#### Configuration Manager (config.py)
```python
class Settings(BaseSettings):
    """Pydantic settings with environment variable support"""
    opensearch_url: str
    opensearch_username: str
    opensearch_password: str
    openai_api_key: str
    mcp_server_port: int = 9900
```

### 3. AI Integration Layer

#### LangChain Agent Flow
```mermaid
sequenceDiagram
    participant U as User
    participant A as Agent
    participant L as LLM (GPT-4o)
    participant T as Tools
    participant M as MCP Server
    
    U->>A: Natural Language Query
    A->>L: Process Query
    L->>L: Understand Intent
    L->>T: Select Tool(s)
    T->>M: Execute Tool
    M-->>T: Return Result
    T-->>L: Tool Output
    L->>L: Generate Response
    L-->>A: Natural Language Answer
    A-->>U: Display Result
    
    Note over L,T: Function Calling API
    Note over T,M: MCP Protocol
```

#### Tool Registry
| Tool Name | Category | Function | API Call |
|-----------|----------|----------|----------|
| list_indices | Index Mgmt | List all indices | GET _cat/indices |
| get_index | Index Mgmt | Get index details | GET /index |
| create_index | Index Mgmt | Create new index | PUT /index |
| delete_index | Index Mgmt | Delete index | DELETE /index |
| index_document | Documents | Add/update doc | PUT /index/_doc/id |
| get_document | Documents | Retrieve doc | GET /index/_doc/id |
| delete_document | Documents | Remove doc | DELETE /index/_doc/id |
| delete_by_query | Documents | Bulk delete | POST /index/_delete_by_query |
| search_documents | Search | Query docs | POST /index/_search |
| get_cluster_health | Cluster | Health status | GET _cluster/health |
| get_cluster_stats | Cluster | Statistics | GET _cluster/stats |
| list_aliases | Aliases | List aliases | GET _cat/aliases |
| get_alias | Aliases | Get index aliases | GET /index/_alias |
| put_alias | Aliases | Create alias | PUT /index/_alias/name |
| delete_alias | Aliases | Remove alias | DELETE /index/_alias/name |
| create_data_stream | Data Streams | Create stream | PUT _data_stream/name |
| get_data_stream | Data Streams | Get stream info | GET _data_stream/name |
| delete_data_stream | Data Streams | Delete stream | DELETE _data_stream/name |
| general_api_request | Advanced | Custom API | ANY /path |

### 4. MCP Protocol Layer

#### Communication Flow
```mermaid
sequenceDiagram
    participant C as MCP Client
    participant S as SSE Stream
    participant M as MCP Server
    participant O as OpenSearch
    
    C->>S: Connect (SSE)
    S-->>C: Connection Established
    
    loop Query Execution
        C->>S: Tool Call Request
        S->>M: Forward Request
        M->>O: Execute OpenSearch API
        O-->>M: API Response
        M-->>S: Tool Result
        S-->>C: Stream Response
    end
    
    Note over C,S: HTTP Server-Sent Events
    Note over M,O: REST API over HTTPS
```

#### Protocol Specification
```json
{
  "protocol": "MCP",
  "version": "1.0",
  "transport": "sse",
  "endpoint": "http://localhost:9900/sse",
  "methods": [
    "tools/list",
    "tools/call",
    "resources/list",
    "resources/read"
  ]
}
```

### 5. Data Layer

#### OpenSearch Client Configuration
```python
client = OpenSearch(
    hosts=[{'host': 'localhost', 'port': 9200}],
    http_auth=('admin', 'password'),
    use_ssl=True,
    verify_certs=False,
    ssl_show_warn=False,
    timeout=30,
    max_retries=3,
    retry_on_timeout=True
)
```

#### Connection Pool
```mermaid
graph LR
    A[Application] --> B[Connection Pool]
    B --> C1[Connection 1]
    B --> C2[Connection 2]
    B --> C3[Connection 3]
    B --> C4[Connection N]
    
    C1 --> D[OpenSearch Node 1]
    C2 --> D
    C3 --> E[OpenSearch Node 2]
    C4 --> E
    
    style B fill:#4CAF50,color:#fff
    style D fill:#2196F3,color:#fff
    style E fill:#2196F3,color:#fff
```

## Data Flow

### Request Flow
```mermaid
graph TD
    A[User Input:<br/>'List all indices'] --> B{Parse Intent}
    B -->|Success| C[Agent Planning]
    B -->|Failure| Z[Error Handler]
    
    C --> D[Select Tools]
    D --> E[list_indices]
    
    E --> F[MCP Server]
    F --> G[OpenSearch API:<br/>GET _cat/indices]
    
    G --> H{API Response}
    H -->|Success| I[Format Data]
    H -->|Error| Z
    
    I --> J[LLM Processing]
    J --> K[Natural Language Response]
    K --> L[Display in UI]
    
    Z --> M[User-Friendly Error]
    M --> L
    
    style A fill:#e1f5ff
    style E fill:#e8f5e9
    style G fill:#fce4ec
    style K fill:#fff9e6
    style Z fill:#ffebee
```

### Response Flow
```mermaid
graph LR
    A[OpenSearch Response] --> B[JSON Parsing]
    B --> C[Data Validation]
    C --> D[Result Formatting]
    D --> E[LLM Enhancement]
    E --> F[Markdown Rendering]
    F --> G[UI Display]
    
    style A fill:#fce4ec
    style D fill:#e8f5e9
    style E fill:#fff9e6
    style G fill:#e1f5ff
```

## Technology Stack

### Core Dependencies
```toml
gradio = "^4.44.0"              # Web UI framework
opensearch-mcp-server-py = "^0.4.0"  # MCP server
langchain = "^0.3.27"           # LLM orchestration
langchain-openai = "^0.3.33"    # OpenAI integration
opensearch-py = "^2.3.0"        # OpenSearch client
python-dotenv = "^1.0.0"        # Environment management
pydantic = "^2.0.0"             # Data validation
```

### Infrastructure Requirements
```yaml
minimum:
  python: "3.10"
  memory: "2GB"
  cpu: "2 cores"
  disk: "1GB"

recommended:
  python: "3.12"
  memory: "4GB"
  cpu: "4 cores"
  disk: "5GB"
```

## Security Architecture

### Authentication Flow
```mermaid
sequenceDiagram
    participant U as User
    participant A as App
    participant E as Environment
    participant M as MCP Server
    participant O as OpenSearch
    
    U->>A: Access Application
    A->>E: Load Credentials
    E-->>A: OpenSearch Auth
    E-->>A: OpenAI Key
    
    A->>M: Connect with Auth
    M->>O: Authenticate
    O-->>M: Token/Session
    M-->>A: Connection OK
    
    Note over A,E: Credentials never stored in code
    Note over M,O: TLS/SSL encryption
```

### Security Layers
1. **Transport Security**
   - TLS 1.3
   - Certificate validation
   - Encrypted connections

2. **Authentication**
   - Basic auth (username/password)
   - API key authentication
   - IAM role support (AWS)

3. **Authorization**
   - Role-based access control
   - Index-level permissions
   - Document-level security

4. **Data Protection**
   - Environment variables for secrets
   - No credentials in logs
   - Secure session management

## Performance Optimization

### Caching Strategy
```mermaid
graph TD
    A[Query Request] --> B{Cache Check}
    B -->|Hit| C[Return Cached Result]
    B -->|Miss| D[Execute Query]
    D --> E[Store in Cache]
    E --> F[Return Result]
    C --> G[Update Stats]
    F --> G
    
    style B fill:#4CAF50,color:#fff
    style C fill:#2196F3,color:#fff
    style D fill:#FF9800,color:#fff
```

### Optimization Techniques
- **Connection Pooling**: Reuse OpenSearch connections
- **Query Caching**: Cache frequent queries (TTL: 5 minutes)
- **Result Pagination**: Limit results to 100 per page
- **Async Operations**: Non-blocking I/O with asyncio
- **Tool Preloading**: Load MCP tools at startup

### Performance Metrics
```python
# Target Performance
response_time_p50 = "< 500ms"
response_time_p95 = "< 2000ms"
response_time_p99 = "< 5000ms"
concurrent_users = 50
queries_per_second = 10
```

## Deployment Architecture

### Development Environment
```mermaid
graph LR
    A[Developer Machine] --> B[Local OpenSearch]
    A --> C[MCP Server Process]
    A --> D[Gradio App Process]
    
    B --> E[Port 9200]
    C --> F[Port 9900]
    D --> G[Port 7860]
    
    style A fill:#4CAF50,color:#fff
    style B fill:#2196F3,color:#fff
    style C fill:#FF9800,color:#fff
    style D fill:#9C27B0,color:#fff
```

### Production Environment
```mermaid
graph TB
    subgraph "Load Balancer"
        A[nginx/ALB]
    end
    
    subgraph "Application Tier"
        B[Gradio App 1]
        C[Gradio App 2]
        D[Gradio App N]
    end
    
    subgraph "MCP Layer"
        E[MCP Server Pool]
    end
    
    subgraph "Data Tier"
        F[OpenSearch Cluster]
        G[Node 1]
        H[Node 2]
        I[Node N]
    end
    
    A --> B
    A --> C
    A --> D
    
    B --> E
    C --> E
    D --> E
    
    E --> F
    F --> G
    F --> H
    F --> I
    
    style A fill:#4CAF50,color:#fff
    style E fill:#FF9800,color:#fff
    style F fill:#2196F3,color:#fff
```

## Error Handling

### Error Flow
```mermaid
graph TD
    A[Error Occurs] --> B{Error Type}
    
    B -->|Network| C[Connection Error]
    B -->|Auth| D[Authentication Error]
    B -->|Query| E[Query Syntax Error]
    B -->|MCP| F[Tool Execution Error]
    B -->|OpenSearch| G[API Error]
    
    C --> H[Retry Logic]
    D --> I[Re-authenticate]
    E --> J[Suggest Correction]
    F --> K[Fallback Tool]
    G --> L[Parse Error Message]
    
    H --> M[User Notification]
    I --> M
    J --> M
    K --> M
    L --> M
    
    M --> N[Log Error]
    N --> O[Display Help]
    
    style A fill:#ffebee
    style M fill:#fff9e6
    style O fill:#e8f5e9
```

### Error Categories
1. **User Errors** (4xx)
   - Invalid input
   - Permission denied
   - Resource not found

2. **System Errors** (5xx)
   - Service unavailable
   - Internal error
   - Timeout

3. **Integration Errors**
   - OpenAI API errors
   - MCP server errors
   - OpenSearch errors

## Monitoring & Observability

### Metrics Collection
```mermaid
graph LR
    A[Application] --> B[Metrics Collector]
    B --> C[Query Latency]
    B --> D[Error Rate]
    B --> E[Active Users]
    B --> F[Tool Usage]
    
    C --> G[Dashboard]
    D --> G
    E --> G
    F --> G
    
    G --> H[Alerts]
    
    style B fill:#4CAF50,color:#fff
    style G fill:#2196F3,color:#fff
    style H fill:#FF5722,color:#fff
```

### Key Metrics
- **Application Metrics**
  - Requests per second
  - Response time (p50, p95, p99)
  - Error rate
  - Active sessions

- **MCP Metrics**
  - Tool call latency
  - Success/failure rate
  - Tool usage distribution

- **OpenSearch Metrics**
  - Query execution time
  - Index size
  - Document count
  - Cluster health

## Testing Strategy

### Test Pyramid
```mermaid
graph TD
    A[E2E Tests<br/>10%] --> B[Integration Tests<br/>30%]
    B --> C[Unit Tests<br/>60%]
    
    style A fill:#FF5722,color:#fff
    style B fill:#FF9800,color:#fff
    style C fill:#4CAF50,color:#fff
```

### Test Coverage
- **Unit Tests**: Individual functions and classes
- **Integration Tests**: MCP client, OpenSearch client
- **E2E Tests**: Full user workflows through UI
- **Performance Tests**: Load testing with locust
- **Security Tests**: Authentication, authorization

## API Reference

### MCP Client API
```python
# Initialize client
client = MCPClient(config)
await client.initialize()

# Execute query
result = await client.query(
    question="List all indices",
    verbose=True
)

# Get tools information
tools = client.get_tools_info()

# Cleanup
await client.close()
```

### Configuration API
```python
# Load from environment
config = Settings()

# Override settings
config = Settings(
    opensearch_url="https://custom:9200",
    mcp_server_port=9901
)

# Validate settings
config.validate()
```

## Troubleshooting Guide

### Common Issues

#### 1. MCP Server Not Responding
```bash
# Check if server is running
curl http://localhost:9900/health

# Restart server
python -m mcp_server_opensearch --transport stream --port 9900
```

#### 2. OpenSearch Connection Failed
```bash
# Verify cluster is running
curl -k https://localhost:9200

# Check credentials
curl -k -u admin:password https://localhost:9200
```

#### 3. OpenAI API Errors
```bash
# Verify API key
echo $OPENAI_API_KEY

# Test API
curl https://api.openai.com/v1/models \
  -H "Authorization: Bearer $OPENAI_API_KEY"
```

## Best Practices

### Code Organization
```
opensearch_mcp_server_app/
├── app.py                 # Main application
├── mcp_client.py          # MCP client wrapper
├── config.py              # Configuration
├── utils/
│   ├── formatting.py      # Output formatting
│   ├── validation.py      # Input validation
│   └── logging.py         # Logging utilities
├── docs/                  # Documentation
└── tests/                 # Test suite
```

### Development Workflow
1. Set up virtual environment
2. Install dependencies with uv
3. Configure environment variables
4. Start OpenSearch cluster
5. Start MCP server
6. Run application
7. Run tests
8. Commit changes

### Production Checklist
- [ ] Environment variables secured
- [ ] SSL certificates configured
- [ ] Monitoring enabled
- [ ] Backups configured
- [ ] Load testing completed
- [ ] Security audit passed
- [ ] Documentation updated
- [ ] Deployment runbook created

## Conclusion

This architecture provides a scalable, secure, and maintainable foundation for the OpenSearch MCP Server Educational App. The modular design allows for easy extension and customization while maintaining clean separation of concerns.

For questions or contributions, refer to the project repository and community guidelines.
