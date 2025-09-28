from opensearchpy import OpenSearch, RequestsHttpConnection
import os, time
from dotenv import load_dotenv
import sys, pandas as pd
sys.path.append('../../')
from helpers import opensearch_bulk_async, dataframe_to_actions
from opensearchpy import OpenSearch, helpers

# 1. Load environment variables from .env file
load_dotenv("../../../.env")

# 2. Retrieve the OpenAI API key from environment variables
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

# 3. Connect to OpenSearch / Initialize the OpenSearch client
IS_AUTH = True

HOST = 'localhost'
if IS_AUTH:
    # Initialize the OpenSearch client
    client = OpenSearch(
        hosts=[{'host': HOST, 'port': 9200}],
        http_auth=('admin', 'Developer@123'),  # Replace with your credentials
        use_ssl=True,
        verify_certs=False,
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
        "plugins.ml_commons.trusted_connector_endpoints_regex": "^https://api\\.openai\\.com/.*$"
    }
}
response = client.cluster.put_settings(body=cluster_settings)
print("Cluster settings updated:", response)

# 5. Register model group
model_group_name = f"remote_model_group_{int(time.time())}"
model_group_body = {
    "name": model_group_name,
    "description": "A model group for external models"
}
response = client.transport.perform_request('POST', '/_plugins/_ml/model_groups/_register', body=model_group_body)
print("Model group registered:", response)
model_group_id = response['model_group_id']

# 6. Create connector
connector_body = {
    "name": "openai_connector",
    "description": "Connector for OpenAI API",
    "version": 1,
    "protocol": "http",
    "parameters": {
        "endpoint": "api.openai.com",
        "model": "text-embedding-ada-002"
    },
    "credential": {
        "openAI_key": OPENAI_API_KEY
    },
    "actions": [
        {
            "action_type": "predict",
            "method": "POST",
            "url": "https://${parameters.endpoint}/v1/embeddings",
            "headers": {
                "Authorization": "Bearer ${credential.openAI_key}"
            },
            "request_body": """{ "input": ${parameters.input}, "model": "${parameters.model}" }""",
            "pre_process_function": "connector.pre_process.openai.embedding",
            "post_process_function": "connector.post_process.openai.embedding"
        }
    ]
}
response = client.transport.perform_request('POST', '/_plugins/_ml/connectors/_create', body=connector_body)
print("Connector created:", response)
connector_id = response['connector_id']

# 7. Register model
model_body = {
    "name": "openAI-gpt-3.5-turbo",
    "function_name": "remote",
    "model_group_id": model_group_id,
    "description": "test model",
    "connector_id": connector_id
}
response = client.transport.perform_request('POST', '/_plugins/_ml/models/_register', body=model_body)
print("Model registered:", response)
model_id = response['model_id']

# 8. Deploy the model and wait for the status to become completed
deploy_body = {
    "deployment_plan": [
        {
            "model_id": model_id,
            "workers": 1
        }
    ]
}

try:
    response = client.transport.perform_request('POST', 
                                                f'/_plugins/_ml/models/{model_id}/_deploy', 
                                                body=deploy_body)
    print("Model deployment initiated:", response)
except Exception as e:
    print(f"Error deploying model: {e}")

# Wait for deployment to complete
while True:
    status_response = client.transport.perform_request('GET', f'/_plugins/_ml/models/{model_id}')
    if status_response['model_state'] == 'DEPLOYED':
        print("Model deployed successfully")
        break
    time.sleep(5)

# 9. Disable automatic deployment - optional
settings_body = {
    "persistent": {
        "plugins.ml_commons.model_auto_deploy.enable": "false"
    }
}
response = client.cluster.put_settings(body=settings_body)
print("Automatic deployment disabled:", response)

# 10: Create ingest pipeline
pipeline_body = {
    "description": "interns embedding pipeline",
    "processors": [
        {
            "text_embedding": {
                "model_id": model_id,
                "field_map": {
                    "COMPANY": "company_embedding_vector",
                    "JOB_TITLE": "job_title_embedding_vector",
                    "JOB_CONTENT_TEXT": "job_content_text_embedding_vector"
                }
            }
        }
    ]
}
response = client.ingest.put_pipeline(id="interns_embedding_pipeline", body=pipeline_body)
print("Ingest pipeline created:", response)

# 11: Create index - note that the dimension is 1536
index_body = {
    "settings": {
        "index.knn": True,
        "default_pipeline": "interns_embedding_pipeline"
    },
    "mappings": {
        "properties": {
            "COMPANY": {"type": "text"},
            "JOB_TITLE": {"type": "text"},
            "JOB_CONTENT_TEXT": {"type": "text"},
            "company_embedding_vector": {
                "type": "knn_vector",
                "dimension": 1536,
                "method": {
                    "name": "hnsw",
                    "space_type": "l2",
                    "engine": "lucene"
                }
            },
            "job_title_embedding_vector": {
                "type": "knn_vector",
                "dimension": 1536,
                "method": {
                    "name": "hnsw",
                    "space_type": "l2",
                    "engine": "lucene"
                }
            },
            "job_content_text_embedding_vector": {
                "type": "knn_vector",
                "dimension": 1536,
                "method": {
                    "name": "hnsw",
                    "space_type": "l2",
                    "engine": "lucene"
                }
            }
        }
    }
}
response = client.indices.create(index="interns", body=index_body)
print("Index created:", response)

# 12: Load sample documents
BASE_DIR = "../../../../data"
df = pd.read_parquet(f"{BASE_DIR}/interns_sample.parquet")

data = dataframe_to_actions(df.iloc[0:2], "interns")
success, failed = helpers.bulk(client=client, actions=data)

print(f"Successfully indexed {success} documents.")
print(f"Failed to index {failed} documents.")

print("Sample documents loaded")

# 13. Search all documents
search_body = {
    "query": {
        "match_all": {}
    }
}
response = client.search(index="interns", body=search_body)
print("Search response:", response)

# 14. Delete ingestion pipeline
response = client.ingest.delete_pipeline(id="interns_embedding_pipeline")
print("Ingestion pipeline deleted:", response)

# 15. Undeploy the model
try:
    response = client.transport.perform_request('POST', f'/_plugins/_ml/models/{model_id}/_undeploy')
    print(f"Undeployed model with ID: {model_id}", response)
except Exception as e:
    print(f"Error undeploying model: {e}")

# 16. Delete the model
try:
    response = client.transport.perform_request('DELETE', f'/_plugins/_ml/models/{model_id}')
    print(f"Deleted model with ID: {model_id}", response)
except Exception as e:
    print(f"Error deleting model: {e}")

# 17. Delete the connector
try:
    response = client.transport.perform_request('DELETE', f'/_plugins/_ml/connectors/{connector_id}')
    print(f"Deleted connector with ID: {connector_id}", response)
except Exception as e:
    print(f"Error deleting connector: {e}")

# 18. Delete the model group
try:
    response = client.transport.perform_request('DELETE', f'/_plugins/_ml/model_groups/{model_group_id}')
    print(f"Deleted model group with ID: {model_group_id}", response)
except Exception as e:
    print(f"Error deleting model group: {e}")