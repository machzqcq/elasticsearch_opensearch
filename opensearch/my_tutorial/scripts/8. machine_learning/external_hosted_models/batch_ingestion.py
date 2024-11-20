from opensearchpy import OpenSearch, RequestsHttpConnection
import os, time
from dotenv import load_dotenv

# 1. Load environment variables from .env file
load_dotenv()

# 2. Retrieve the OpenAI API key from environment variables
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

# 3. Connect to OpenSearch / Initialize the OpenSearch client
IS_AUTH = True

if IS_AUTH:
    # Initialize the OpenSearch client
    client = OpenSearch(
        hosts=[{'host': '192.168.0.111', 'port': 9200}],
        http_auth=('admin', 'Developer123'),  # Replace with your credentials
        use_ssl=True,
        verify_certs=False,
        ssl_show_warn=False
    )
else:
    # Initialize the OpenSearch client without authentication
    client = OpenSearch(
        hosts=[{'host': '192.168.0.111', 'port': 9200}],
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
client.cluster.put_settings(body=cluster_settings)

# 5. Register model group
model_group_body = {
    "name": "remote_model_group",
    "description": "A model group for external models"
}
response = client.perform_request('POST', '/_plugins/_ml/model_groups/_register', body=model_group_body)
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
response = client.perform_request('POST', '/_plugins/_ml/connectors/_create', body=connector_body)
connector_id = response['connector_id']

# 7. Register model
model_body = {
    "name": "openAI-gpt-3.5-turbo",
    "function_name": "remote",
    "model_group_id": model_group_id,
    "description": "test model",
    "connector_id": connector_id
}
response = client.perform_request('POST', '/_plugins/_ml/models/_register', body=model_body)
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
    client.transport.perform_request('POST', 
                                     f'/_plugins/_ml/models/{model_id}/_deploy', 
                                     body=deploy_body)
except Exception as e:
    print(f"Error deploying model: {e}")

# Wait for deployment to complete
while True:
    status_response = client.transport.perform_request('GET', f'/_plugins/_ml/models/{model_id}')
    if status_response['model_state'] == 'DEPLOYED':
        break
    time.sleep(5)

# 9. Disable automatic deployment - optional
settings_body = {
    "persistent": {
        "plugins.ml_commons.model_auto_deploy.enable": "false"
    }
}
client.cluster.put_settings(body=settings_body)

# 10. Create ingest pipeline
pipeline_body = {
    "description": "A text embedding pipeline",
    "processors": [
        {
            "text_embedding": {
                "model_id": model_id,
                "field_map": {
                    "passage_text": "passage_embedding"
                },
                "batch_size": 5
            }
        }
    ]
}
client.ingest.put_pipeline(id="nlp-ingest-pipeline", body=pipeline_body)

# 11. Create index
client.indices.create(index="testindex")

# 12. Bulk index documents
bulk_body = [
    {"create": {"_index": "testindex", "_id": "2"}},
    {"passage_text": "hello world"},
    {"create": {"_index": "testindex", "_id": "3"}},
    {"passage_text": "big apple"},
    {"create": {"_index": "testindex", "_id": "4"}},
    {"passage_text": "golden gate bridge"},
    {"create": {"_index": "testindex", "_id": "5"}},
    {"passage_text": "fine tune"},
    {"create": {"_index": "testindex", "_id": "6"}},
    {"passage_text": "random test"},
    {"create": {"_index": "testindex", "_id": "7"}},
    {"passage_text": "sun and moon"},
    {"create": {"_index": "testindex", "_id": "8"}},
    {"passage_text": "windy"},
    {"create": {"_index": "testindex", "_id": "9"}},
    {"passage_text": "new york"},
    {"create": {"_index": "testindex", "_id": "10"}},
    {"passage_text": "fantastic"}
]
client.bulk(body=bulk_body, index="testindex", pipeline="nlp-ingest-pipeline")

# 13. Search all documents
search_body = {
    "query": {
        "match_all": {}
    }
}
response = client.search(index="testindex", body=search_body)
print(response)

# 14. Delete ingestion pipeline
client.ingest.delete_pipeline(id="nlp-ingest-pipeline")

# 15. Undeploy the model
try:
    client.transport.perform_request('POST', f'/_plugins/_ml/models/{model_id}/_undeploy')
    print(f"Undeployed model with ID: {model_id}")
except Exception as e:
    print(f"Error undeploying model: {e}")

# 16. Delete the model
try:
    client.transport.perform_request('DELETE', f'/_plugins/_ml/models/{model_id}')
    print(f"Deleted model with ID: {model_id}")
except Exception as e:
    print(f"Error deleting model: {e}")

# 17. Delete the connector
try:
    client.transport.perform_request('DELETE', f'/_plugins/_ml/connectors/{connector_id}')
    print(f"Deleted connector with ID: {connector_id}")
except Exception as e:
    print(f"Error deleting connector: {e}")

# 18. Delete the model group
try:
    client.transport.perform_request('DELETE', f'/_plugins/_ml/model_groups/{model_group_id}')
    print(f"Deleted model group with ID: {model_group_id}")
except Exception as e:
    print(f"Error deleting model group: {e}")