# OpenSearch PostgreSQL RAG System

A bi-agentic RAG (Retrieval-Augmented Generation) system that combines PostgreSQL database metadata with OpenSearch vector search and AI-powered natural language querying.

## 🏗️ System Architecture

```mermaid
graph TD
    A[User Query] --> B[RAG Agent 1: Metadata Retrieval]
    B --> C[OpenSearch Vector Search]
    C --> D[Relevant Tables & Columns]
    D --> E[RAG Agent 2: SQL Generation]
    E --> F[PostgreSQL Query]
    F --> G[Data Results]
    G --> H[AI-Powered Insights & Visualization]
```

## 📋 Components

### 1. Database Metadata Extraction (`1. build_ingest_meta_dictionary.ipynb`)
- **PostgreSQL Connection**: Connects to PostgreSQL database using psycopg2
- **Schema Analysis**: Extracts table structures, column information, and sample data
- **AI Description Generation**: Uses DeepSeek API to generate human-readable column descriptions
- **OpenSearch Indexing**: Creates searchable metadata index for RAG retrieval

### 2. RAG-Powered SQL Query & Insights (`2. text-to-sql-viz-insights.ipynb`)
- **Natural Language Processing**: Converts user queries to relevant database context
- **Intelligent SQL Generation**: Uses RAG to generate PostgreSQL-specific queries
- **Data Visualization**: Creates charts and insights from query results
- **Bi-Agentic Flow**: Two AI agents work together for optimal results

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose
- Python 3.8+
- PostgreSQL database with sample data
- OpenSearch cluster
- DeepSeek API key

### 1. Environment Setup
```bash
# Copy environment template
cp sample_env.env .env

# Edit with your credentials
nano .env
```

Required environment variables:
```env
# PostgreSQL Database
POSTGRES_HOST=localhost
POSTGRES_DB=your_database
POSTGRES_USER=your_username
POSTGRES_PASSWORD=your_password

# OpenSearch
OPENSEARCH_HOST=localhost
OPENSEARCH_PORT=9200
OPENSEARCH_USER=admin
OPENSEARCH_PASSWORD=admin

# AI API
DEEPSEEK_API_KEY=your_deepseek_api_key
```

### 2. Start PostgreSQL (if using Docker)
```bash
docker-compose -f docker-compose-postgres.yml up -d
```

### 3. Install Dependencies
```bash
pip install psycopg2-binary opensearch-py pandas matplotlib seaborn requests python-dotenv sqlalchemy
```

### 4. Run the Notebooks

#### Step 1: Build Metadata Dictionary
1. Open `1. build_ingest_meta_dictionary.ipynb`
2. Execute all cells to:
   - Extract database schema and metadata
   - Generate AI-powered column descriptions
   - Index metadata in OpenSearch

#### Step 2: RAG Query System
1. Open `2. text-to-sql-viz-insights.ipynb`
2. Execute cells to:
   - Set up RAG agents
   - Test natural language queries
   - Generate SQL and visualizations

## 💡 Usage Examples

### Natural Language Queries
```python
# Example queries the system can handle:
queries = [
    "Show me all customers from California",
    "What are the top 5 selling products?",
    "Find orders with shipping delays",
    "Analyze sales trends by region"
]
```

### Generated SQL (PostgreSQL)
```sql
-- Query: "Show customers from California"
SELECT 
    c.customer_id,
    c.first_name,
    c.last_name,
    a.address,
    a.city,
    a.state
FROM customers c
JOIN addresses a ON c.address_id = a.address_id
WHERE a.state = 'CA'
LIMIT 100;
```

## 🔧 Technical Features

### PostgreSQL Integration
- **psycopg2 driver** for robust database connectivity
- **SQLAlchemy ORM** for database abstraction
- **PostgreSQL-specific SQL** syntax and functions
- **Connection pooling** for performance

### RAG Components
- **Vector embeddings** for metadata similarity search
- **Semantic retrieval** of relevant table/column information
- **Context-aware SQL generation** using retrieved metadata
- **Bi-agentic architecture** for improved accuracy

### AI & ML
- **DeepSeek API** for natural language processing
- **Automated metadata descriptions** for better context
- **Query understanding** and intent recognition
- **Result interpretation** and insight generation

## 📊 System Flow

1. **Metadata Extraction Phase**:
   - Connect to PostgreSQL database
   - Extract table schemas and sample data
   - Generate AI descriptions for each column
   - Index metadata in OpenSearch with embeddings

2. **Query Processing Phase**:
   - Receive natural language query
   - Use RAG to find relevant database metadata
   - Generate contextually appropriate PostgreSQL query
   - Execute query and return results

3. **Insight Generation Phase**:
   - Analyze query results
   - Generate visualizations
   - Provide AI-powered insights and recommendations

## 🛠️ Configuration

### PostgreSQL Settings
```python
# Database connection configuration
POSTGRES_CONFIG = {
    'host': os.getenv('POSTGRES_HOST'),
    'database': os.getenv('POSTGRES_DB'),
    'user': os.getenv('POSTGRES_USER'),
    'password': os.getenv('POSTGRES_PASSWORD'),
    'port': 5432
}
```

### OpenSearch Settings
```python
# Vector search configuration
OPENSEARCH_CONFIG = {
    'hosts': [{'host': 'localhost', 'port': 9200}],
    'http_auth': ('admin', 'admin'),
    'use_ssl': True,
    'verify_certs': False
}
```

## 🔍 Troubleshooting

### Common Issues

**Database Connection Errors**:
```bash
# Check PostgreSQL status
docker-compose -f docker-compose-postgres.yml ps

# Test connection
psql -h localhost -U your_user -d your_db
```

**OpenSearch Connection Issues**:
```bash
# Verify OpenSearch is running
curl -k https://admin:admin@localhost:9200

# Check cluster health
curl -k https://admin:admin@localhost:9200/_cluster/health
```

**Missing Dependencies**:
```bash
# Install PostgreSQL driver
pip install psycopg2-binary

# Or if compilation issues:
pip install psycopg2
```

## 📈 Performance Optimization

- **Connection pooling** for database efficiency
- **Batch processing** for metadata extraction
- **Vector index optimization** for fast retrieval
- **Query caching** for repeated patterns
- **Async processing** for large datasets

## 🔒 Security Best Practices

- Store credentials in environment variables
- Use connection pooling with proper timeout settings
- Implement query validation and sanitization
- Regular security updates for dependencies
- Monitor API usage and rate limits

## 📚 Additional Resources

- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [OpenSearch Documentation](https://opensearch.org/docs/)
- [DeepSeek API Documentation](https://platform.deepseek.com/docs/)

## 🤝 Contributing

1. Fork the repository
2. Create feature branch
3. Test with your PostgreSQL setup
4. Submit pull request with detailed description

## 📝 License

This project is available under the MIT License. See LICENSE file for details.

---

**Ready to explore your PostgreSQL data with AI-powered natural language queries!** 🚀