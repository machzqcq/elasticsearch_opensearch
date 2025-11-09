# Anthropic Claude Integration with OpenSearch

## 📚 Overview
This guide demonstrates integrating **Anthropic's Claude LLM** with OpenSearch using connectors for advanced Q&A, chat, and content generation capabilities.

### 🎯 Key Concept: OpenSearch Connectors
- **Connector**: Bridge between OpenSearch and external API
- **Credential Management**: Secure API key storage
- **Seamless Integration**: Use external models in OpenSearch pipelines

---

## 🏗️ Architecture

```mermaid
graph TD
    A["OpenSearch Cluster"] -->|REST API| B["OpenSearch ML Commons"]
    B -->|Connector| C["Anthropic Connector"]
    C -->|HTTPS| D["api.anthropic.com"]
    D -->|Claude 3| E["LLM Processing"]
    E -->|Response| D
    D -->|JSON| C
    C -->|Result| B
    B -->|Answer| A
```

---

## 💡 Supported Claude Models

```mermaid
graph LR
    A["Claude 3 Models"]
    
    A -->|Opus| B1["Most capable<br/>Complex reasoning<br/>Slower, costlier"]
    A -->|Sonnet| B2["Balanced<br/>Fast & smart<br/>Good default"]
    A -->|Haiku| B3["Fastest<br/>Simple tasks<br/>Cheapest"]
    
    B1 --> C["Best for:<br/>Analysis<br/>Complex coding"]
    B2 --> D["Best for:<br/>General use<br/>Q&A"]
    B3 --> E["Best for:<br/>Simple tasks<br/>Low latency"]
```

---

## 📋 Step-by-Step Implementation

### **Step 1: Environment Setup** 🔧

```python
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv("../../../.env")

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

# Verify API key exists
if not ANTHROPIC_API_KEY:
    raise ValueError("ANTHROPIC_API_KEY not found in environment")
```

**Create `.env` file:**
```
ANTHROPIC_API_KEY=sk-ant-xxxxxxxxxxxxxxxxxxxxxxxx
```

### **Step 2: Initialize OpenSearch Client** 🔌

```python
from opensearchpy import OpenSearch
import time
import warnings

warnings.filterwarnings("ignore", message="Unverified HTTPS request")
warnings.filterwarnings('ignore', category=DeprecationWarning)

def get_os_client(cluster_url={'host': 'localhost', 'port': 9200},
                  username='admin',
                  password='Developer@123'):
    """Create OpenSearch client"""
    client = OpenSearch(
        hosts=[cluster_url],
        http_auth=(username, password),
        verify_certs=False,
        ssl_assert_hostname=False,
        ssl_show_warn=False,
        use_ssl=True,
        max_retries=10,
        retry_on_timeout=True,
        timeout=300  # Long timeout for LLM calls
    )
    return client

client = get_os_client()
```

### **Step 3: Configure Cluster Settings** ⚙️

```python
print("Configuring cluster settings for Anthropic connector...")

cluster_settings = {
    "persistent": {
        # Trust external endpoints (Anthropic API)
        "plugins.ml_commons.trusted_connector_endpoints_regex": [".*"],
        
        # Allow running on any node
        "plugins.ml_commons.only_run_on_ml_node": "false",
        
        # Enable memory features for conversation
        "plugins.ml_commons.memory_feature_enabled": "true",
        
        # Enable private IP connections
        "plugins.ml_commons.connector.private_ip_enabled": "true"
    }
}

client.cluster.put_settings(body=cluster_settings)
print("✅ Cluster settings configured")
```

**Key Settings Explained:**

| Setting | Purpose |
|---------|---------|
| `trusted_connector_endpoints_regex` | Define allowed external endpoints |
| `only_run_on_ml_node` | false = any node can call external LLM |
| `memory_feature_enabled` | true = enables conversation memory |
| `connector.private_ip_enabled` | true = allow private IP connections |

### **Step 4: Create Model Group** 👥

```python
print("Creating model group for Anthropic...")

model_group_name = f"anthropic_chat_group_{int(time.time())}"
model_group_body = {
    "name": model_group_name,
    "description": "Model group for anthropic chat models"
}

model_group_response = client.transport.perform_request(
    method='POST',
    url='/_plugins/_ml/model_groups/_register',
    body=model_group_body
)

model_group_id = model_group_response['model_group_id']
print(f"✅ Model group created: {model_group_id}")
```

### **Step 5: Create Anthropic Connector** 🔗

```python
print("Creating Anthropic connector...")

connector_body = {
    "name": "Anthropic Chat Connector",
    "description": "Connector for Anthropic Claude API",
    "version": "1",
    "protocol": "http",  # HTTP protocol (HTTPS at API endpoint)
    "parameters": {
        "endpoint": "api.anthropic.com",  # Anthropic API endpoint
        "model": "claude-3-opus-20240229"  # Claude model to use
    },
    "credential": {
        "anthropic_key": os.getenv("ANTHROPIC_API_KEY")  # Your API key
    }
}

connector_response = client.transport.perform_request(
    method='POST',
    url='/_plugins/_ml/connectors/_create',
    body=connector_body
)

connector_id = connector_response['connector_id']
print(f"✅ Connector created: {connector_id}")
```

**Connector Parameters:**

| Parameter | Value | Purpose |
|-----------|-------|---------|
| `endpoint` | api.anthropic.com | Anthropic API host |
| `model` | claude-3-opus-20240229 | Model ID |
| `protocol` | http | HTTP/HTTPS protocol |
| `anthropic_key` | Your API key | Authentication |

### **Step 6: Register Claude Model** 📦

```python
print("Registering Claude model in OpenSearch...")

register_body = {
    "name": "Claude 3 Chat",
    "description": "Anthropic Claude 3 chat model via connector",
    "model_group_id": model_group_id,
    "function_name": "CHAT",  # ← Chat function
    "connector_id": connector_id,
    "model_format": "REMOTE"  # ← Remote model (external)
}

register_response = client.transport.perform_request(
    method='POST',
    url='/_plugins/_ml/models/_register',
    body=register_body
)

model_id = register_response['model_id']
print(f"✅ Model registered: {model_id}")
```

### **Step 7: Deploy Model** 🚀

```python
print("Deploying Claude model...")

deploy_response = client.transport.perform_request(
    method='POST',
    url=f'/_plugins/_ml/models/{model_id}/_deploy'
)

print(f"✅ Model deployed: {deploy_response['task_id']}")
```

### **Step 8: Test Chat** 💬

```python
print("Testing Claude chat...")

messages = [
    {
        "role": "user",
        "content": "What is the capital of France?"
    }
]

chat_response = client.transport.perform_request(
    method='POST',
    url=f'/_plugins/_ml/models/{model_id}/_predict',
    body={
        "messages": messages
    }
)

response_text = chat_response['inference_results'][0]['output'][0]['data']
print(f"Claude: {response_text}")
```

---

## 💡 Key Learning Points

### 🎓 Message Format

```python
messages = [
    {
        "role": "user",
        "content": "Your question here"
    },
    {
        "role": "assistant",
        "content": "Previous response"
    },
    {
        "role": "user",
        "content": "Follow-up question"
    }
]
```

### 📊 Context Window Sizes

| Model | Context | Best For |
|-------|---------|----------|
| Claude 3 Opus | 200K tokens | Large documents, complex reasoning |
| Claude 3 Sonnet | 200K tokens | Balanced speed/quality |
| Claude 3 Haiku | 200K tokens | Fast responses |

### 🔐 Credential Security

```python
# ✅ GOOD: Environment variables
api_key = os.getenv("ANTHROPIC_API_KEY")
connector_body = {
    "credential": {
        "anthropic_key": api_key
    }
}

# ❌ BAD: Hardcoded keys
connector_body = {
    "credential": {
        "anthropic_key": "sk-ant-..."  # EXPOSED!
    }
}
```

---

## 📋 Common Patterns

### Pattern: RAG with Claude

```python
def rag_with_claude(question: str, documents: list, model_id: str) -> str:
    """
    Retrieve documents and generate answer with Claude
    """
    # Format context
    context = "\n---\n".join([
        f"Document {i+1}:\n{doc}"
        for i, doc in enumerate(documents)
    ])
    
    # Build prompt
    messages = [
        {
            "role": "user",
            "content": f"""Using the following context, answer the question.

Context:
{context}

Question: {question}

Answer:"""
        }
    ]
    
    # Call Claude
    response = client.transport.perform_request(
        method='POST',
        url=f'/_plugins/_ml/models/{model_id}/_predict',
        body={"messages": messages}
    )
    
    return response['inference_results'][0]['output'][0]['data']

# Usage
docs = ["Paris is in France", "France is in Europe"]
answer = rag_with_claude("Where is Paris?", docs, model_id)
```

### Pattern: Multi-turn Conversation

```python
class ClaudeConversation:
    def __init__(self, client, model_id):
        self.client = client
        self.model_id = model_id
        self.history = []
    
    def add_message(self, role: str, content: str):
        self.history.append({
            "role": role,
            "content": content
        })
    
    def respond(self, user_message: str) -> str:
        # Add user message
        self.add_message("user", user_message)
        
        # Get Claude response
        response = self.client.transport.perform_request(
            method='POST',
            url=f'/_plugins/_ml/models/{self.model_id}/_predict',
            body={"messages": self.history}
        )
        
        assistant_message = response['inference_results'][0]['output'][0]['data']
        
        # Add assistant response to history
        self.add_message("assistant", assistant_message)
        
        return assistant_message

# Usage
conv = ClaudeConversation(client, model_id)
print(conv.respond("What is AI?"))
print(conv.respond("Can you explain it more simply?"))  # Uses context
```

---

## 🔧 Troubleshooting

| Issue | Solution |
|-------|----------|
| "Invalid API key" | Check `ANTHROPIC_API_KEY` in `.env` |
| Connector not found | Verify connector was created successfully |
| Timeout errors | Increase `timeout` value in client config |
| Rate limit errors | Add exponential backoff retry logic |

---

## 💰 Cost Optimization

```python
# Use faster/cheaper models for simple tasks
"model": "claude-3-haiku-20240307"  # Fastest & cheapest

# Only use Opus for complex tasks
"model": "claude-3-opus-20240229"   # Expensive but best

# Batch requests when possible
messages_batch = [
    {"role": "user", "content": question1},
    {"role": "assistant", "content": answer1},
    {"role": "user", "content": question2}
]
```

---

## 📖 Additional Resources

- 🔗 [Anthropic API Documentation](https://docs.anthropic.com/claude/reference/getting-started-with-the-api)
- 🔗 [Claude Model Comparison](https://www.anthropic.com/news/claude-3-family)
- 🔗 [OpenSearch Connectors Guide](https://opensearch.org/docs/latest/ml-commons-plugin/ml-commons-connectors/)

---

## ✨ Summary

Anthropic integration provides:
- ✅ **State-of-the-art reasoning** with Claude
- ✅ **Large context windows** (200k tokens)
- ✅ **Constitutional AI** safety training
- ✅ **Seamless OpenSearch integration**

Perfect for **enterprise-grade RAG systems and analysis tasks**! 🚀

