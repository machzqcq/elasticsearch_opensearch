from opensearchpy import OpenSearch, RequestsHttpConnection
import os, time, json
from dotenv import load_dotenv

# 1. Load environment variables from .env file
load_dotenv("../../.env")

# 2. Retrieve the OpenAI API key from environment variables
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

# 3. Connect to OpenSearch / Initialize the OpenSearch client
IS_AUTH = True
OLLAMA_IP_URL = '10.2.23.181:11434'  # Change to your Ollama host if needed. See README.md for more details.
OLLAMA_MODEL = "smollm2:135m" # neural-chat:latest if you have more memory on ollama_ip_url host
HOST = 'localhost'
if IS_AUTH:
    # Initialize the OpenSearch client
    client = OpenSearch(
        hosts=[{'host': HOST, 'port': 9200}],
        http_auth=('admin', 'Developer@123'),  # Replace with your credentials
        use_ssl=True,
        verify_certs=False,
        ssl_assert_hostname = False,
        ssl_show_warn=False
    )
else:
    # Initialize the OpenSearch client without authentication
    client = OpenSearch(
        hosts=[{'host': HOST, 'port': 9200}],
        use_ssl=False,
        verify_certs=False,
        ssl_assert_hostname = False,
        ssl_show_warn=False
    )

# 4. Modify cluster settings to accept OpenAI as trusted connector endpoint
cluster_settings = {
    "persistent": {
        "plugins.ml_commons.trusted_connector_endpoints_regex": [".*"],
        "plugins.ml_commons.only_run_on_ml_node": "false",
        "plugins.ml_commons.memory_feature_enabled": "true"
    }
}
client.cluster.put_settings(body=cluster_settings)

# 5. Register model with no group
embedding_model_body = {
  "name": "huggingface/sentence-transformers/all-MiniLM-L12-v2",
  "version": "1.0.1",
  "model_format": "TORCH_SCRIPT"
}
embedding_response = client.transport.perform_request('POST', '/_plugins/_ml/models/_register?deploy=true', body=embedding_model_body)
embedding_task_id = embedding_response['task_id']

# Extract task_id from the response
embedding_task_id = embedding_response['task_id']

# Wait until the status becomes completed
while True:
    embedding_model_status = client.transport.perform_request(
        method='GET',
        url=f'/_plugins/_ml/tasks/{embedding_task_id}'
    )
    print(embedding_model_status)
    if embedding_model_status['state'] == 'COMPLETED':
        embedding_model_id = embedding_model_status['model_id']
        break
    time.sleep(10)  # Wait for 10 seconds before checking again

# 6. Deploy the model and wait for the status to become completed
deploy_body = {
    "deployment_plan": [
        {
            "model_id": embedding_model_id,
            "workers": 1
        }
    ]
}

try:
    client.transport.perform_request('POST', 
                                     f'/_plugins/_ml/models/{embedding_model_id}/_deploy', 
                                     body=deploy_body)
except Exception as e:
    print(f"Error deploying model: {e}")

# 7. Wait for deployment to complete
while True:
    status_response = client.transport.perform_request('GET', f'/_plugins/_ml/models/{embedding_model_id}')
    print(f"Embedding model status: {status_response['model_state']}")
    if status_response['model_state'] == 'DEPLOYED':
        break
    time.sleep(5)

# 8. Create ingest pipeline
pipeline_body = {
    "description": "A text embedding pipeline",
    "processors": [
        {
            "text_embedding": {
                "model_id": embedding_model_id,
                "field_map": {
                    "text": "embedding"
                }
            }
        }
    ]
}

pipeline_id = f"test-pipeline-local-model_{embedding_model_id}"
client.ingest.put_pipeline(id=pipeline_id, body=pipeline_body)

# 9: Create index - note that the dimension is 384
index_body = {
  "mappings": {
    "properties": {
      "text": {
        "type": "text"
      },
      "embedding": {
        "type": "knn_vector",
        "dimension": 384,
        "method": {
              "name": "hnsw",
              "engine": "lucene"
            }
      }
    }
  },
  "settings": {
    "index": {
      "default_pipeline": pipeline_id,
      "knn": "true"
    }
  }
}

index_name = f"my_test_data_{int(time.time())}"
response = client.indices.create(index=index_name, body=index_body)
print("Index created:", response)

# 10. Bulk index documents
bulk_body = [
    {"index": {"_index": index_name, "_id": "1"}},
    {"text": "Chart and table of population level and growth rate for the Ogden-Layton metro area from 1950 to 2023. United Nations population projections are also included through the year 2035.\nThe current metro area population of Ogden-Layton in 2023 is 750,000, a 1.63% increase from 2022.\nThe metro area population of Ogden-Layton in 2022 was 738,000, a 1.79% increase from 2021.\nThe metro area population of Ogden-Layton in 2021 was 725,000, a 1.97% increase from 2020.\nThe metro area population of Ogden-Layton in 2020 was 711,000, a 2.16% increase from 2019."},
    {"index": {"_index": index_name, "_id": "2"}},
    {"text": "Chart and table of population level and growth rate for the New York City metro area from 1950 to 2023. United Nations population projections are also included through the year 2035.\nThe current metro area population of New York City in 2023 is 18,937,000, a 0.37% increase from 2022.\nThe metro area population of New York City in 2022 was 18,867,000, a 0.23% increase from 2021.\nThe metro area population of New York City in 2021 was 18,823,000, a 0.1% increase from 2020.\nThe metro area population of New York City in 2020 was 18,804,000, a 0.01% decline from 2019."},
    {"index": {"_index": index_name, "_id": "3"}},
    {"text": "Chart and table of population level and growth rate for the Chicago metro area from 1950 to 2023. United Nations population projections are also included through the year 2035.\nThe current metro area population of Chicago in 2023 is 8,937,000, a 0.4% increase from 2022.\nThe metro area population of Chicago in 2022 was 8,901,000, a 0.27% increase from 2021.\nThe metro area population of Chicago in 2021 was 8,877,000, a 0.14% increase from 2020.\nThe metro area population of Chicago in 2020 was 8,865,000, a 0.03% increase from 2019."},
    {"index": {"_index": index_name, "_id": "4"}},
    {"text": "Chart and table of population level and growth rate for the Miami metro area from 1950 to 2023. United Nations population projections are also included through the year 2035.\nThe current metro area population of Miami in 2023 is 6,265,000, a 0.8% increase from 2022.\nThe metro area population of Miami in 2022 was 6,215,000, a 0.78% increase from 2021.\nThe metro area population of Miami in 2021 was 6,167,000, a 0.74% increase from 2020.\nThe metro area population of Miami in 2020 was 6,122,000, a 0.71% increase from 2019."},
    {"index": {"_index": index_name, "_id": "5"}},
    {"text": "Chart and table of population level and growth rate for the Austin metro area from 1950 to 2023. United Nations population projections are also included through the year 2035.\nThe current metro area population of Austin in 2023 is 2,228,000, a 2.39% increase from 2022.\nThe metro area population of Austin in 2022 was 2,176,000, a 2.79% increase from 2021.\nThe metro area population of Austin in 2021 was 2,117,000, a 3.12% increase from 2020.\nThe metro area population of Austin in 2020 was 2,053,000, a 3.43% increase from 2019."},
    {"index": {"_index": index_name, "_id": "6"}},
    {"text": "Chart and table of population level and growth rate for the Seattle metro area from 1950 to 2023. United Nations population projections are also included through the year 2035.\nThe current metro area population of Seattle in 2023 is 3,519,000, a 0.86% increase from 2022.\nThe metro area population of Seattle in 2022 was 3,489,000, a 0.81% increase from 2021.\nThe metro area population of Seattle in 2021 was 3,461,000, a 0.82% increase from 2020.\nThe metro area population of Seattle in 2020 was 3,433,000, a 0.79% increase from 2019."}
]
client.bulk(body=bulk_body, index=index_name, pipeline=pipeline_id)

print("Bulk indexing completed")

# 11. Register model group
model_group_name = f"openai_model_group_{int(time.time())}"
llm_model_group_body = {
  "name": model_group_name,
  "description": "A model group for open ai models"
}
response = client.transport.perform_request('POST', '/_plugins/_ml/model_groups/_register', body=llm_model_group_body)
print("Model group registered:", response)
llm_model_group_id = response['model_group_id']

# 12. Create connector
print("Step 4: Creating Ollama connector...")
# Use the proper Ollama API format with HTTP protocol
connector_body = {
    "name": "ollama_connector",
    "description": "Connector for Ollama API",
    "version": 1,
    "protocol": "http",
    "parameters": {
        "endpoint": OLLAMA_IP_URL,
        "model": OLLAMA_MODEL
    },
    "credential": {
        "dummy_key": "dummy"
    },
    "actions": [
        {
            "action_type": "predict",
            "method": "POST",
            "url": "http://${parameters.endpoint}/api/generate",
            "headers": {
                "Content-Type": "application/json"
            },
            "request_body": "{ \"model\": \"${parameters.model}\", \"prompt\": \"${parameters.prompt}\", \"stream\": false }"
        }
    ]
}
connector_response = client.transport.perform_request('POST', '/_plugins/_ml/connectors/_create', body=connector_body)
llm_connector_id = connector_response['connector_id']
print(f"✓ Created Ollama connector with ID: {llm_connector_id}\n")


# 13. Register model
llm_model_body = {
    "name": "openAI-gpt-3.5-turbo",
    "function_name": "remote",
    "model_group_id": llm_model_group_id,
    "description": "test model",
    "connector_id": llm_connector_id
}
response = client.transport.perform_request('POST', '/_plugins/_ml/models/_register', body=llm_model_body)
print("Model registered:", response)
llm_model_id = response['model_id']

# 14. Deploy the model and wait for the status to become completed
llm_deploy_body = {
    "deployment_plan": [
        {
            "model_id": llm_model_id,
            "workers": 1
        }
    ]
}

try:
    response = client.transport.perform_request('POST', 
                                                f'/_plugins/_ml/models/{llm_model_id}/_deploy', 
                                                body=llm_deploy_body)
    print("Model deployment initiated:", response)
except Exception as e:
    print(f"Error deploying model: {e}")

# 15. Wait for deployment to complete
while True:
    status_response = client.transport.perform_request('GET', f'/_plugins/_ml/models/{llm_model_id}')
    if status_response['model_state'] == 'DEPLOYED':
        print("Model deployed successfully")
        break
    time.sleep(5)

# 16. Test prediction
test_llm_predict_body = {
  "parameters": {
    "prompt": "Why is the sky blue?"
  }
}


predict_response = client.transport.perform_request(
    'POST',
    f'/_plugins/_ml/models/{llm_model_id}/_predict',
    body=test_llm_predict_body
)

print(json.dumps(predict_response, indent=2))

# 17. Register an Agent

agent_register_body = {
  "name": "Test_Agent_For_RAG",
  "type": "flow",
  "description": "this is a test agent",
  "tools": [
    {
      "type": "VectorDBTool",
      "parameters": {
        "model_id": embedding_model_id,
        "index": "my_test_data",
        "embedding_field": "embedding",
        "source_field": [
          "text"
        ],
        "input": "${parameters.question}"
      }
    },
    {
      "type": "MLModelTool",
      "description": "A general tool to answer any question",
      "parameters": {
        "model_id": llm_model_id,
        "prompt": "You are a professional data analyst. You will always answer a question based on the given context first. If the answer is not directly shown in the context, you will analyze the data and find the answer. If you don't know the answer, just say you don't know.\n\nContext:\n${parameters.VectorDBTool.output}\n\nQuestion: ${parameters.question}\n\nAnswer:"
      }
    }
  ]
}

agent_response = client.transport.perform_request('POST', '/_plugins/_ml/agents/_register', body=agent_register_body)
print("Agent registered:", agent_response)
agent_id = agent_response['agent_id']

# 18. inspect agent

inspect_response = client.transport.perform_request('GET', f'/_plugins/_ml/agents/{agent_id}')
print("Agent inspected:", inspect_response)

# 19. Execute agent

execute_body = {
  "parameters": {
    "question": "what's the population increase of Seattle from 2021 to 2023"
  }
}

execute_response = client.transport.perform_request('POST', f'/_plugins/_ml/agents/{agent_id}/_execute', body=execute_body)
print("Agent executed:", execute_response)


