from opensearchpy import OpenSearch, RequestsHttpConnection
import time
import json
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Retrieve the OpenAI API key from environment variables
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

# OpenSearch client setup
client = OpenSearch(
    hosts=[{'host': '192.168.0.111', 'port': 9200}],
    http_auth=('admin', 'Developer@123'),
    use_ssl=True,
    verify_certs=False,
    connection_class=RequestsHttpConnection
)

# 1. Modify cluster settings to accept OpenAI as trusted connector endpoint
cluster_settings = {
    "persistent": {
        "plugins.ml_commons.trusted_connector_endpoints_regex": "^https://api\\.openai\\.com/.*$"
    }
}
client.cluster.put_settings(body=cluster_settings)

# 2. Create a model group
model_group_name = "openai_embedding_group"

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
print(f"Created model group '{model_group_name}' with ID: {model_group_id}")

# 3. Create a connector for OpenAI
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

# 4. Register a model using the previously created model_group_id and connector_id
model_body = {
    "name": "openai_embedding_model",
    "function_name": "remote",
    "model_group_id": model_group_id,
    "description": "OpenAI text-embedding-ada-002 model",
    "connector_id": connector_id,
    "model_format": "TORCH_SCRIPT"
}
model_response = client.transport.perform_request(
    'POST',
    '/_plugins/_ml/models/_register',
    body=model_body
)
model_id = model_response['model_id']

# 5. Deploy the model and wait for the status to become completed
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

# 6. Call the predict endpoint with sample data
predict_body = {
  "parameters": {
    "input": [ "What is the meaning of life?" ]
  }
}
predict_response = client.transport.perform_request(
    'POST',
    f'/_plugins/_ml/models/{model_id}/_predict',
    body=predict_body
)

print(json.dumps(predict_response, indent=2))

# Undeploy the model
try:
    client.transport.perform_request('POST', f'/_plugins/_ml/models/{model_id}/_undeploy')
    print(f"Undeployed model with ID: {model_id}")
except Exception as e:
    print(f"Error undeploying model: {e}")

# Delete the model
try:
    client.transport.perform_request('DELETE', f'/_plugins/_ml/models/{model_id}')
    print(f"Deleted model with ID: {model_id}")
except Exception as e:
    print(f"Error deleting model: {e}")

# Delete the connector
try:
    client.transport.perform_request('DELETE', f'/_plugins/_ml/connectors/{connector_id}')
    print(f"Deleted connector with ID: {connector_id}")
except Exception as e:
    print(f"Error deleting connector: {e}")

# Delete the model group
try:
    client.transport.perform_request('DELETE', f'/_plugins/_ml/model_groups/{model_group_id}')
    print(f"Deleted model group with ID: {model_group_id}")
except Exception as e:
    print(f"Error deleting model group: {e}")