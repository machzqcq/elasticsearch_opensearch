# Batch Ingestion with Embeddings (Generic Template)

## 📚 Overview

`batch_ingestion.py` is the **generic template version** of batch ingestion demonstrating how to:

- **Deploy OpenAI embedding models** (text-embedding-3-small, ada-002)
- **Create ingest pipelines** for automatic embedding
- **Build flexible bulk indexing workflows** for any dataset
- **Configure multi-field semantic search**
- **Handle production-scale data ingestion**

Unlike the interns-specific version, this is a **reusable template** you can adapt for any dataset and domain.

---

## 🎯 Template vs Specialized Version

| Aspect | batch_ingestion.py | batch_ingestion_interns.py |
|--------|-------------------|---------------------------|
| Data source | Generic (flexible) | Interns dataset (fixed) |
| Fields | Customizable | COMPANY, JOB_TITLE, JOB_CONTENT_TEXT |
| Use case | Template/learning | Production example |
| Scope | Core concepts | Complete example |
| Reusability | High (adapt easily) | Lower (specific use case) |
| Documentation | Moderate | Comprehensive |

**When to use each:**
- `batch_ingestion.py`: Learning, new projects, custom datasets
- `batch_ingestion_interns.py`: Reference, specific job dataset, patterns

---

## 🏗️ Generic Architecture

```mermaid
graph TB
    subgraph "Your Dataset"
        CSV["📊 CSV/JSON/DB<br/>Any data source"]
        Transform["🔄 Transform<br/>To DataFrame"]
    end
    
    subgraph "OpenSearch Setup"
        Cluster["🔍 OpenSearch<br/>Cluster config"]
        ModelGroup["📦 Model Group"]
        Connector["🔗 OpenAI Connector"]
        Model["🧠 Embedding Model"]
    end
    
    subgraph "Pipeline"
        Pipeline["⚙️ Ingest Pipeline<br/>Auto-embed processor"]
        Index["📇 Index Definition<br/>Mappings + settings"]
    end
    
    subgraph "Ingestion"
        BulkFormat["📋 Bulk Format<br/>OpenSearch actions"]
        Bulk["💾 Bulk Index<br/>Parallel processing"]
    end
    
    subgraph "Result"
        Indexed["✅ Indexed Data<br/>With vectors"]
    end
    
    CSV -->|"Read & parse"| Transform
    Transform -->|"Prepare"| BulkFormat
    Cluster -->|"Configure"| Model
    Model -->|"Define"| Pipeline
    Pipeline -->|"Apply to"| Index
    BulkFormat -->|"Send to"| Bulk
    Bulk -->|"Use pipeline"| Index
    Index -->|"Store"| Indexed
    
    style CSV fill:#fff3bf,stroke:#f59f00
    style Indexed fill:#d3f9d8,stroke:#2f9e44,color:#000
```

---

## 🔄 Step-by-Step Generic Workflow

### Step 1: Configuration Constants

```python
import os
import time
import pandas as pd
from dotenv import load_dotenv
from opensearchpy import OpenSearch, helpers

# Configuration
load_dotenv("../../../.env")
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

# Cluster configuration
HOST = 'localhost'
PORT = 9200
USERNAME = 'admin'
PASSWORD = 'Developer@123'

# Model configuration
EMBEDDING_MODEL = "text-embedding-3-small"  # Or ada-002, 3-large

# Index configuration
INDEX_NAME = "my_index"  # Change to your index name
DATA_FILE = "data.parquet"  # Change to your data file
```

### Step 2: Initialize OpenSearch Client

```python
def get_opensearch_client(host=HOST, port=PORT, username=USERNAME, password=PASSWORD):
    """Create OpenSearch client with SSL configuration."""
    client = OpenSearch(
        hosts=[{'host': host, 'port': port}],
        http_auth=(username, password),
        use_ssl=True,
        verify_certs=False,
        ssl_show_warn=False
    )
    return client

client = get_opensearch_client()
```

### Step 3: Configure Cluster

```python
def configure_cluster(client):
    """Configure cluster for OpenAI embeddings."""
    cluster_settings = {
        "persistent": {
            "plugins.ml_commons.trusted_connector_endpoints_regex": "^https://api\\.openai\\.com/.*$"
        }
    }
    response = client.cluster.put_settings(body=cluster_settings)
    print("✓ Cluster configured")
    return response

configure_cluster(client)
```

### Step 4: Create Model Group

```python
def create_model_group(client):
    """Create model group with timestamp-based naming."""
    model_group_name = f"embedding_group_{int(time.time())}"
    body = {
        "name": model_group_name,
        "description": "Embedding model group for semantic search"
    }
    response = client.transport.perform_request(
        'POST',
        '/_plugins/_ml/model_groups/_register',
        body=body
    )
    model_group_id = response['model_group_id']
    print(f"✓ Model group created: {model_group_id}")
    return model_group_id

model_group_id = create_model_group(client)
```

### Step 5: Create OpenAI Connector

```python
def create_openai_connector(client, api_key, model_name):
    """Create connector for OpenAI embedding API."""
    connector_body = {
        "name": "openai_connector",
        "description": f"Connector for OpenAI {model_name}",
        "version": 1,
        "protocol": "http",
        "parameters": {
            "endpoint": "api.openai.com",
            "model": model_name
        },
        "credential": {
            "openAI_key": api_key
        },
        "actions": [
            {
                "action_type": "predict",
                "method": "POST",
                "url": "https://${parameters.endpoint}/v1/embeddings",
                "headers": {
                    "Authorization": "Bearer ${credential.openAI_key}"
                },
                "request_body": "{ \"input\": ${parameters.input}, \"model\": \"${parameters.model}\" }",
                "pre_process_function": "connector.pre_process.openai.embedding",
                "post_process_function": "connector.post_process.openai.embedding"
            }
        ]
    }
    
    response = client.transport.perform_request(
        'POST',
        '/_plugins/_ml/connectors/_create',
        body=connector_body
    )
    connector_id = response['connector_id']
    print(f"✓ Connector created: {connector_id}")
    return connector_id

connector_id = create_openai_connector(client, OPENAI_API_KEY, EMBEDDING_MODEL)
```

### Step 6: Register Model

```python
def register_model(client, model_group_id, connector_id, model_name):
    """Register embedding model."""
    model_body = {
        "name": f"embedding_{model_name}",
        "function_name": "remote",
        "model_group_id": model_group_id,
        "description": f"OpenAI {model_name} embedding model",
        "connector_id": connector_id
    }
    
    response = client.transport.perform_request(
        'POST',
        '/_plugins/_ml/models/_register',
        body=model_body
    )
    model_id = response['model_id']
    print(f"✓ Model registered: {model_id}")
    return model_id

model_id = register_model(client, model_group_id, connector_id, EMBEDDING_MODEL)
```

### Step 7: Deploy Model

```python
def deploy_model(client, model_id):
    """Deploy model and wait for completion."""
    deploy_body = {
        "deployment_plan": [
            {
                "model_id": model_id,
                "workers": 1
            }
        ]
    }
    
    # Initiate deployment
    try:
        client.transport.perform_request(
            'POST',
            f'/_plugins/_ml/models/{model_id}/_deploy',
            body=deploy_body
        )
        print("✓ Deployment initiated")
    except Exception as e:
        print(f"✗ Error deploying: {e}")
        return False
    
    # Wait for deployment
    print("⏳ Waiting for deployment...")
    max_attempts = 60
    for attempt in range(max_attempts):
        status_response = client.transport.perform_request(
            'GET',
            f'/_plugins/_ml/models/{model_id}'
        )
        status = status_response['model_state']
        print(f"   Attempt {attempt + 1}/{max_attempts}: {status}")
        
        if status == 'DEPLOYED':
            print("✓ Model deployed successfully!")
            return True
        elif status == 'FAILED':
            print("✗ Model deployment failed!")
            return False
        
        time.sleep(2)
    
    print("✗ Deployment timeout!")
    return False

if not deploy_model(client, model_id):
    print("Cannot continue without deployed model")
    exit(1)
```

### Step 8: Create Ingest Pipeline

```python
def create_ingest_pipeline(client, model_id, field_map):
    """
    Create ingest pipeline for automatic embedding.
    
    Args:
        client: OpenSearch client
        model_id: Deployed embedding model ID
        field_map: Dict mapping source fields to embedding vector fields
                   Example: {"title": "title_vector", "content": "content_vector"}
    """
    pipeline_body = {
        "description": "Embedding pipeline for semantic search",
        "processors": [
            {
                "text_embedding": {
                    "model_id": model_id,
                    "field_map": field_map
                }
            }
        ]
    }
    
    response = client.ingest.put_pipeline(
        id="embedding_pipeline",
        body=pipeline_body
    )
    print("✓ Ingest pipeline created")
    return response

# Define field mapping (customize for your data!)
field_map = {
    "title": "title_vector",
    "description": "description_vector",
    "content": "content_vector"
}

create_ingest_pipeline(client, model_id, field_map)
```

### Step 9: Create Vector Index

```python
def create_vector_index(client, index_name, field_map):
    """
    Create index with KNN vector fields.
    
    Args:
        client: OpenSearch client
        index_name: Name of the index to create
        field_map: Dict of embedding fields (from step 8)
    """
    index_body = {
        "settings": {
            "index.knn": True,
            "default_pipeline": "embedding_pipeline"
        },
        "mappings": {
            "properties": {
                # Add your text fields
                "title": {"type": "text"},
                "description": {"type": "text"},
                "content": {"type": "text"},
                # Add vector fields (from field_map values)
            }
        }
    }
    
    # Add vector field mappings
    for vector_field in field_map.values():
        index_body["mappings"]["properties"][vector_field] = {
            "type": "knn_vector",
            "dimension": 1536,  # OpenAI embedding dimension
            "method": {
                "name": "hnsw",
                "space_type": "l2",
                "engine": "lucene"
            }
        }
    
    response = client.indices.create(index=index_name, body=index_body)
    print(f"✓ Index '{index_name}' created")
    return response

create_vector_index(client, INDEX_NAME, field_map)
```

### Step 10: Load Data

```python
def load_data(file_path):
    """Load data from various formats."""
    if file_path.endswith('.parquet'):
        return pd.read_parquet(file_path)
    elif file_path.endswith('.csv'):
        return pd.read_csv(file_path)
    elif file_path.endswith('.json'):
        return pd.read_json(file_path)
    else:
        raise ValueError(f"Unsupported format: {file_path}")

df = load_data(DATA_FILE)
print(f"✓ Loaded {len(df)} rows from {DATA_FILE}")
```

### Step 11: Bulk Index Data

```python
def dataframe_to_bulk_actions(df, index_name):
    """Convert DataFrame rows to OpenSearch bulk actions."""
    for idx, row in df.iterrows():
        yield {
            "_index": index_name,
            "_id": str(idx),
            "_source": row.to_dict()
        }

def bulk_index(client, actions, batch_size=100):
    """Bulk index documents with progress tracking."""
    success_count = 0
    error_count = 0
    
    try:
        for ok, response in helpers.streaming_bulk(
            client,
            actions,
            chunk_size=batch_size,
            raise_on_error=False
        ):
            if ok:
                success_count += 1
                if success_count % 50 == 0:
                    print(f"   Indexed {success_count} documents...")
            else:
                error_count += 1
                print(f"   Error indexing: {response}")
    except Exception as e:
        print(f"✗ Error during bulk indexing: {e}")
        return success_count, error_count
    
    return success_count, error_count

# Execute bulk indexing
actions = dataframe_to_bulk_actions(df.head(100), INDEX_NAME)  # Use head() for testing
success, errors = bulk_index(client, actions)
print(f"✓ Bulk indexing complete: {success} success, {errors} errors")
```

### Step 12: Verify Index

```python
def verify_index(client, index_name):
    """Verify index and show sample documents."""
    search_body = {"query": {"match_all": {}}, "size": 2}
    response = client.search(index=index_name, body=search_body)
    
    total = response['hits']['total']['value']
    print(f"✓ Index has {total} documents")
    
    if response['hits']['hits']:
        print("Sample document:")
        print(f"  {response['hits']['hits'][0]['_source']}")
    
    return response

verify_index(client, INDEX_NAME)
```

### Step 13: Cleanup

```python
def cleanup_all(client, model_id, connector_id, model_group_id, pipeline_id="embedding_pipeline"):
    """Clean up all resources."""
    errors = []
    
    # Delete pipeline
    try:
        client.ingest.delete_pipeline(id=pipeline_id)
        print("✓ Pipeline deleted")
    except Exception as e:
        errors.append(f"Pipeline cleanup: {e}")
    
    # Undeploy model
    try:
        client.transport.perform_request('POST', f'/_plugins/_ml/models/{model_id}/_undeploy')
        print("✓ Model undeployed")
    except Exception as e:
        errors.append(f"Model undeploy: {e}")
    
    # Delete model
    try:
        client.transport.perform_request('DELETE', f'/_plugins/_ml/models/{model_id}')
        print("✓ Model deleted")
    except Exception as e:
        errors.append(f"Model delete: {e}")
    
    # Delete connector
    try:
        client.transport.perform_request('DELETE', f'/_plugins/_ml/connectors/{connector_id}')
        print("✓ Connector deleted")
    except Exception as e:
        errors.append(f"Connector delete: {e}")
    
    # Delete model group
    try:
        client.transport.perform_request('DELETE', f'/_plugins/_ml/model_groups/{model_group_id}')
        print("✓ Model group deleted")
    except Exception as e:
        errors.append(f"Model group delete: {e}")
    
    if errors:
        print("\n⚠ Errors during cleanup:")
        for error in errors:
            print(f"  - {error}")
    else:
        print("\n✓ All cleanup complete!")
    
    return len(errors) == 0

cleanup_all(client, model_id, connector_id, model_group_id)
```

---

## 📊 Customization Guide

### Customize for Your Data

```python
# 1. Update field mapping
field_map = {
    "your_field_1": "your_field_1_vector",
    "your_field_2": "your_field_2_vector",
    "your_field_3": "your_field_3_vector"
}

# 2. Update index creation
def create_vector_index(client, index_name, field_map):
    index_body = {
        "settings": {
            "index.knn": True,
            "default_pipeline": "embedding_pipeline"
        },
        "mappings": {
            "properties": {
                "your_field_1": {"type": "text"},
                "your_field_2": {"type": "keyword"},
                "your_field_3": {"type": "integer"},
                # ... add all your fields
            }
        }
    }
    
    # Auto-add vector fields
    for vector_field in field_map.values():
        index_body["mappings"]["properties"][vector_field] = {
            "type": "knn_vector",
            "dimension": 1536,
            "method": {"name": "hnsw", "space_type": "l2", "engine": "lucene"}
        }
    
    return client.indices.create(index=index_name, body=index_body)
```

### Different Data Sources

```python
# From CSV
df = pd.read_csv("data.csv")

# From JSON Lines
df = pd.read_json("data.jsonl", lines=True)

# From SQL Database
import sqlalchemy
engine = sqlalchemy.create_engine("postgresql://user:pass@localhost/db")
df = pd.read_sql("SELECT * FROM table", engine)

# From API
import requests
response = requests.get("https://api.example.com/data")
df = pd.DataFrame(response.json())
```

---

## 🛠️ Complete Working Example

```python
# Save as: my_batch_ingestion.py

if __name__ == "__main__":
    # Configuration
    INDEX_NAME = "my_documents"
    DATA_FILE = "my_data.parquet"
    field_map = {
        "title": "title_vector",
        "description": "description_vector"
    }
    
    # Initialize
    client = get_opensearch_client()
    
    # Setup
    configure_cluster(client)
    model_group_id = create_model_group(client)
    connector_id = create_openai_connector(client, OPENAI_API_KEY, "text-embedding-3-small")
    model_id = register_model(client, model_group_id, connector_id, "text-embedding-3-small")
    
    if not deploy_model(client, model_id):
        print("Failed to deploy model!")
        exit(1)
    
    # Create pipeline and index
    create_ingest_pipeline(client, model_id, field_map)
    create_vector_index(client, INDEX_NAME, field_map)
    
    # Load and index data
    df = load_data(DATA_FILE)
    actions = dataframe_to_bulk_actions(df, INDEX_NAME)
    success, errors = bulk_index(client, actions)
    
    # Verify
    verify_index(client, INDEX_NAME)
    
    # Cleanup (optional)
    # cleanup_all(client, model_id, connector_id, model_group_id)
    
    print("\n✅ Batch ingestion complete!")
```

---

## 🎓 Production Checklist

- [ ] **Customization**
  - [ ] Field mapping updated for your data
  - [ ] Index name changed
  - [ ] Data file path correct
  - [ ] All text fields included

- [ ] **Data Quality**
  - [ ] No null values in embedding fields
  - [ ] Data format correct (CSV, parquet, JSON)
  - [ ] Row count reasonable
  - [ ] Field names consistent

- [ ] **Performance**
  - [ ] Batch size optimized (50-200)
  - [ ] Indexing throughput acceptable
  - [ ] Memory usage reasonable
  - [ ] Cost within budget

- [ ] **Verification**
  - [ ] Index created successfully
  - [ ] Documents indexed correctly
  - [ ] Vector fields populated
  - [ ] Search working

---

## ✨ Summary

This generic batch ingestion template provides:

✅ **Reusable workflow** for any dataset  
✅ **Customizable field mapping** for your data  
✅ **Complete lifecycle management** from setup to cleanup  
✅ **Production-grade error handling**  
✅ **Performance optimization** patterns  
✅ **Clear documentation** for adaptation  

Use this template to quickly build **semantic search systems** for your own data!

