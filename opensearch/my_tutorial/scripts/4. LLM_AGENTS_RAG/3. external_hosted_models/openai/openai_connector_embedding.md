# OpenAI Connector Embedding (Production Edition)

## 📚 Overview

`openai_connector_embedding.py` is a **production-grade implementation** of OpenAI embedding model integration with OpenSearch ML Commons. This script demonstrates how to:

- **Deploy OpenAI embedding models** (text-embedding-3-small, text-embedding-ada-002)
- **Generate vector embeddings** via OpenAI API
- **Integrate embeddings into OpenSearch** for semantic search
- **Build production RAG systems** using cloud-based embeddings
- **Handle API authentication** securely with environment variables

Unlike chat models that generate text responses, embedding models convert text into **dense vectors** (typically 1536 dimensions) that capture semantic meaning for similarity searches and RAG pipelines.

---

## 🏗️ Architecture Overview

```mermaid
graph TB
    subgraph "Your Documents"
        Doc1["📄 Document 1"]
        Doc2["📄 Document 2"]
        Query["🔍 Query"]
    end
    
    subgraph "OpenAI API"
        APIKey["🔐 API Key<br/>Authentication"]
        OpenAIAPI["🌐 OpenAI API<br/>text-embedding-3-small"]
    end
    
    subgraph "Vectors"
        Vec1["🔢 Vector 1<br/>1536 dimensions"]
        Vec2["🔢 Vector 2<br/>1536 dimensions"]
        VecQ["🔢 Query Vector<br/>1536 dimensions"]
    end
    
    subgraph "OpenSearch"
        OSCluster["🔍 OpenSearch<br/>localhost:9200"]
        Index["📇 Vector Index<br/>KNN search"]
    end
    
    subgraph "Results"
        Results["✨ Ranked Results<br/>Semantic similarity"]
    end
    
    Doc1 -->|"Text"| OpenAIAPI
    Doc2 -->|"Text"| OpenAIAPI
    Query -->|"Text"| OpenAIAPI
    APIKey -->|"Authorize"| OpenAIAPI
    OpenAIAPI -->|"1536-dim vector"| Vec1
    OpenAIAPI -->|"1536-dim vector"| Vec2
    OpenAIAPI -->|"1536-dim vector"| VecQ
    Vec1 -->|"Index"| OSCluster
    Vec2 -->|"Index"| OSCluster
    VecQ -->|"Search"| Index
    Index -->|"Match"| Results
    
    style OpenAIAPI fill:#10a37f,stroke:#0d7e4f,color:#fff
    style OSCluster fill:#4ecdc4,stroke:#0d9488,color:#fff
    style Results fill:#d3f9d8,stroke:#2f9e44,color:#000
```

---

## 🔑 OpenAI Embedding Models Comparison

| Model | Dimensions | Cost | Speed | Quality | Typical Use |
|-------|-----------|------|-------|---------|------------|
| text-embedding-3-small | 1536 | $0.02 / 1M | 10-20ms | Excellent | Most use cases |
| text-embedding-3-large | 3072 | $0.13 / 1M | 20-50ms | Very Best | Premium search |
| text-embedding-ada-002 | 1536 | $0.10 / 1M | 20-50ms | Good | Legacy (deprecated) |

**Cost calculation example:**
- 1M tokens = ~200k documents (5 tokens avg per document)
- text-embedding-3-small: $0.02 for 200k documents
- 1M documents: $0.10 cost

---

## 🔄 Step-by-Step Implementation

### Step 1: Initialize Cluster with OpenAI Support

```python
# Load API key from environment
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

# Configure cluster to accept OpenAI endpoints
cluster_settings = {
    "persistent": {
        "plugins.ml_commons.trusted_connector_endpoints_regex": "^https://api\\.openai\\.com/.*$",
        "plugins.ml_commons.only_run_on_ml_node": "false",
        "plugins.ml_commons.memory_feature_enabled": "true"
    }
}
client.cluster.put_settings(body=cluster_settings)
```

**Why these settings?**
- Regex allows only OpenAI API domain (security)
- Allow operations on non-ML nodes
- Enable memory tracking

### Step 2: Create Model Group

```python
model_group_name = f"openai_embedding_group_{int(time.time())}"
model_group_body = {
    "name": model_group_name,
    "description": "Model group for OpenAI embeddings"
}

model_group_response = client.transport.perform_request(
    'POST',
    '/_plugins/_ml/model_groups/_register',
    body=model_group_body
)
model_group_id = model_group_response['model_group_id']
```

### Step 3: Create OpenAI Connector

```python
connector_body = {
    "name": "openai_connector",
    "description": "Connector for OpenAI API",
    "version": 1,
    "protocol": "http",
    "parameters": {
        "endpoint": "api.openai.com",
        "model": "text-embedding-3-small"  # Or text-embedding-ada-002
    },
    "credential": {
        "openAI_key": OPENAI_API_KEY  # ← Stored securely
    },
    "actions": [
        {
            "action_type": "predict",
            "method": "POST",
            "url": "https://${parameters.endpoint}/v1/embeddings",
            "headers": {
                "Authorization": "Bearer ${credential.openAI_key}"
            },
            "request_body": "{ \"input\": ${parameters.input}, \"model\": \"${parameters.model}\" }"
        }
    ]
}

connector_response = client.transport.perform_request(
    'POST',
    '/_plugins/_ml/connectors/_create',
    body=connector_body
)
connector_id = connector_response['connector_id']
```

**Key features:**
- Credentials stored securely in OpenSearch
- Bearer token authentication
- Input parameter for embedding text
- Model specified in parameters

### Step 4: Register Model

```python
model_body = {
    "name": "openai_embedding_model",
    "function_name": "remote",
    "model_group_id": model_group_id,
    "description": "OpenAI text-embedding-3-small model",
    "connector_id": connector_id,
    "model_format": "TORCH_SCRIPT"
}

model_response = client.transport.perform_request(
    'POST',
    '/_plugins/_ml/models/_register',
    body=model_body
)
model_id = model_response['model_id']
```

### Step 5: Deploy Model

```python
deploy_body = {
    "deployment_plan": [
        {
            "model_id": model_id,
            "workers": 1
        }
    ]
}

try:
    client.transport.perform_request(
        'POST', 
        f'/_plugins/_ml/models/{model_id}/_deploy', 
        body=deploy_body
    )
    print("✓ Model deployment initiated")
except Exception as e:
    print(f"⚠ Error deploying model: {e}")
    return

# Poll for deployment completion
print("⏳ Waiting for deployment...")
while True:
    status_response = client.transport.perform_request(
        'GET',
        f'/_plugins/_ml/models/{model_id}'
    )
    current_status = status_response['model_state']
    print(f"   Status: {current_status}")
    
    if current_status == 'DEPLOYED':
        print("✓ Deployment complete!")
        break
    elif current_status == 'FAILED':
        print("✗ Deployment failed!")
        return
    
    time.sleep(5)
```

### Step 6: Test Embedding Generation

```python
predict_body = {
    "parameters": {
        "input": ["What is the meaning of life?"]  # Text to embed
    }
}

try:
    predict_response = client.transport.perform_request(
        'POST',
        f'/_plugins/_ml/models/{model_id}/_predict',
        body=predict_body
    )
    print("✓ Model prediction successful!")
    print(json.dumps(predict_response, indent=2))
    
    # Response structure:
    # {
    #   "predictions": [
    #     {
    #       "output": [0.0234, -0.5621, ..., 0.1823]  ← 1536-dim vector
    #     }
    #   ]
    # }
except Exception as e:
    print(f"⚠ Error during prediction: {e}")
```

### Step 7: Exception-Safe Cleanup

```python
def cleanup_resources(client, model_id, connector_id, model_group_id):
    """Clean up all resources with exception safety."""
    
    # 1. Undeploy
    try:
        client.transport.perform_request(
            'POST',
            f'/_plugins/_ml/models/{model_id}/_undeploy'
        )
        print(f"✓ Undeployed model: {model_id}")
    except Exception as e:
        print(f"⚠ Error undeploying: {e}")
    
    # 2. Delete model
    try:
        client.transport.perform_request(
            'DELETE',
            f'/_plugins/_ml/models/{model_id}'
        )
        print(f"✓ Deleted model: {model_id}")
    except Exception as e:
        print(f"⚠ Error deleting model: {e}")
    
    # 3. Delete connector
    try:
        client.transport.perform_request(
            'DELETE',
            f'/_plugins/_ml/connectors/{connector_id}'
        )
        print(f"✓ Deleted connector: {connector_id}")
    except Exception as e:
        print(f"⚠ Error deleting connector: {e}")
    
    # 4. Delete model group
    try:
        client.transport.perform_request(
            'DELETE',
            f'/_plugins/_ml/model_groups/{model_group_id}'
        )
        print(f"✓ Deleted model group: {model_group_id}")
    except Exception as e:
        print(f"⚠ Error deleting group: {e}")
    
    print("✓ Cleanup completed!")
```

---

## 📊 Cost Analysis

### Monthly Cost Estimates

| Use Case | Monthly Documents | Tokens | Cost |
|----------|------------------|--------|------|
| Small app | 10,000 | 50,000 | $0.001 |
| Medium app | 100,000 | 500,000 | $0.01 |
| Large app | 1,000,000 | 5,000,000 | $0.10 |
| Enterprise | 10,000,000 | 50,000,000 | $1.00 |

**Cost optimization tips:**
1. Use text-embedding-3-small (5x cheaper than ada-002)
2. Cache embeddings for repeated queries
3. Batch embedding requests
4. Clean up old embeddings regularly

---

## 🚀 Running the Script

### Prerequisites

```bash
# 1. OpenAI API key
export OPENAI_API_KEY="sk-..."

# 2. OpenSearch running
curl -u admin:Developer@123 https://localhost:9200

# 3. Python dependencies
pip install opensearch-py
```

### Execution

```bash
cd opensearch/my_tutorial/scripts/4. LLM_AGENTS_RAG/3. external_hosted_models/openai
python openai_connector_embedding.py
```

### Expected Output

```
=== OpenAI Embedding Model Integration with OpenSearch ===

Step 1: Initializing OpenSearch Client and Configuring Cluster...
✓ Cluster settings configured successfully

Step 2: Creating Model Group...
✓ Created model group 'openai_embedding_group_1698765432' with ID: abc123

Step 3: Creating OpenAI Connector...
✓ Created OpenAI connector with ID: conn123

Step 4: Registering and Deploying Model...
✓ Registered model with ID: model123
✓ Model deployment initiated
⏳ Waiting for model deployment to complete...
   Current status: DEPLOYING
   Current status: DEPLOYED
✓ Model deployed successfully!

Step 5: Testing Model with Sample Data...
✓ Model prediction successful!
{
  "predictions": [
    {
      "output": [
        0.0234, -0.5621, ..., 0.1823  (1536 dimensions)
      ]
    }
  ]
}

Step 6: Cleaning Up Resources...
✓ Undeployed model with ID: model123
✓ Deleted model with ID: model123
✓ Deleted connector with ID: conn123
✓ Deleted model group with ID: abc123
✓ Cleanup completed!
```

---

## 🔧 Configuration Options

### Change Embedding Model

```python
# Fast & cheap (most recommended)
OPENAI_MODEL = "text-embedding-3-small"

# High quality (more expensive)
OPENAI_MODEL = "text-embedding-3-large"

# Legacy (deprecated, but still works)
OPENAI_MODEL = "text-embedding-ada-002"
```

### Configure OpenSearch Connection

```python
# With authentication (production)
client = OpenSearch(
    hosts=[{'host': 'localhost', 'port': 9200}],
    http_auth=('admin', 'Developer@123'),
    use_ssl=True,
    verify_certs=False
)

# Without authentication (development)
client = OpenSearch(
    hosts=[{'host': 'localhost', 'port': 9200}],
    use_ssl=False
)
```

---

## 📈 Production Patterns

### Pattern 1: Batch Embedding Generation

```python
def generate_embeddings_batch(texts, model_id, batch_size=20):
    """Generate embeddings efficiently in batches."""
    embeddings = []
    
    for i in range(0, len(texts), batch_size):
        batch = texts[i:i + batch_size]
        predict_body = {"parameters": {"input": batch}}
        
        try:
            response = client.transport.perform_request(
                'POST',
                f'/_plugins/_ml/models/{model_id}/_predict',
                body=predict_body
            )
            for pred in response['predictions']:
                embeddings.append(pred['output'])
        except Exception as e:
            print(f"Error in batch: {e}")
            # Continue with next batch
    
    return embeddings
```

**Benefits:**
- Reduces API calls (1 call per 20 texts vs 1 per text)
- Cost savings (OpenAI charges per request)
- Faster overall processing

### Pattern 2: Caching Embeddings

```python
import hashlib
import pickle

embedding_cache = {}

def get_embedding_cached(text, model_id):
    """Get embedding with caching."""
    text_hash = hashlib.md5(text.encode()).hexdigest()
    
    if text_hash in embedding_cache:
        return embedding_cache[text_hash]
    
    predict_body = {"parameters": {"input": [text]}}
    response = client.transport.perform_request(
        'POST',
        f'/_plugins/_ml/models/{model_id}/_predict',
        body=predict_body
    )
    embedding = response['predictions'][0]['output']
    embedding_cache[text_hash] = embedding
    
    return embedding

# Save cache to disk
def save_cache(filename):
    with open(filename, 'wb') as f:
        pickle.dump(embedding_cache, f)

def load_cache(filename):
    global embedding_cache
    with open(filename, 'rb') as f:
        embedding_cache = pickle.load(f)
```

**Savings:**
- Avoid duplicate API calls
- Reduce costs significantly
- Faster response times

### Pattern 3: Error Handling with Retry

```python
import time

def get_embedding_with_retry(text, model_id, max_retries=3):
    """Get embedding with automatic retry."""
    for attempt in range(max_retries):
        try:
            predict_body = {"parameters": {"input": [text]}}
            response = client.transport.perform_request(
                'POST',
                f'/_plugins/_ml/models/{model_id}/_predict',
                body=predict_body,
                timeout=30
            )
            return response['predictions'][0]['output']
        except Exception as e:
            if attempt == max_retries - 1:
                raise
            print(f"Retry {attempt + 1}/{max_retries}")
            time.sleep(2 ** attempt)  # Exponential backoff
```

---

## 🛠️ Troubleshooting Guide

### Issue 1: "Unauthorized" Error

```
Error: Unauthorized - Invalid API key
```

**Solutions:**
```bash
# Check API key in .env
cat .env | grep OPENAI_API_KEY

# Verify it's set in environment
echo $OPENAI_API_KEY

# Test API key directly
curl -H "Authorization: Bearer $OPENAI_API_KEY" \
  https://api.openai.com/v1/models
```

### Issue 2: "Model deployment failed"

**Solutions:**
- Check API quota: https://platform.openai.com/account/billing/overview
- Wait for deployment to complete
- Verify OpenSearch ML node available: `GET /_nodes/stats/ml_*`
- Check OpenSearch logs for details

### Issue 3: "Rate limit exceeded"

```
Error: rate_limit_exceeded
```

**Solutions:**
```python
# Implement exponential backoff
import time
import random

def get_embedding_with_backoff(text, model_id):
    max_retries = 5
    for attempt in range(max_retries):
        try:
            return get_embedding(text, model_id)
        except RateLimitError:
            if attempt == max_retries - 1:
                raise
            wait_time = 2 ** attempt + random.random()
            print(f"Rate limited. Waiting {wait_time:.1f}s...")
            time.sleep(wait_time)
```

### Issue 4: "Connection refused"

```
Error: Connection refused - cannot reach api.openai.com
```

**Solutions:**
- Check internet connectivity: `ping api.openai.com`
- Verify firewall allows HTTPS (port 443)
- Check proxy settings if behind firewall
- Test with `curl https://api.openai.com`

---

## 🎓 Production Checklist

- [ ] **Configuration**
  - [ ] OPENAI_API_KEY set in .env
  - [ ] API key has embedding permissions
  - [ ] OpenSearch cluster reachable
  - [ ] Network allows outbound HTTPS

- [ ] **Performance**
  - [ ] Embedding latency: 10-50ms per text
  - [ ] Batch processing enabled
  - [ ] Caching implemented for repeated queries
  - [ ] Cost monitoring configured

- [ ] **Error Handling**
  - [ ] Retry logic with exponential backoff
  - [ ] Rate limit handling
  - [ ] Timeout values appropriate
  - [ ] Cleanup always executes

- [ ] **Monitoring**
  - [ ] API usage tracked
  - [ ] Failed predictions logged
  - [ ] Cost alerts configured
  - [ ] Model deployment status checked

- [ ] **Security**
  - [ ] API key not hardcoded
  - [ ] Credentials in .env file
  - [ ] Regular key rotation scheduled
  - [ ] Access logs reviewed

---

## 🔗 Learning Path: Cloud Embeddings

**Beginner to Expert:**

1. **Start**: Understand embedding concepts (vectors, similarity)
2. **Learn**: This script - OpenAI integration
3. **Practice**: Generate embeddings for your data
4. **Build**: Semantic search system
5. **Optimize**: Batch processing, caching, cost optimization
6. **Master**: Multi-model ensemble, production scaling

---

## ✨ Summary

This production-grade OpenAI embedding integration demonstrates:

✅ **OpenAI API integration** with secure credential handling  
✅ **Embedding model deployment** with polling  
✅ **Exception-safe resource cleanup**  
✅ **Batch processing** for cost efficiency  
✅ **Caching patterns** to reduce API calls  
✅ **Retry logic** with exponential backoff  
✅ **Production error handling** throughout  

Use this as your foundation for building **scalable semantic search systems** powered by OpenAI's state-of-the-art embeddings!

