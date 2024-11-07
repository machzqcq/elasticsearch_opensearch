from opensearchpy import OpenSearch, RequestsHttpConnection
import os, time, json
from dotenv import load_dotenv
import requests
import base64, os
import sys
sys.path.append('../../')
from helpers import *

# 1. Load environment variables from .env file
load_dotenv("../../.env")

# 2. Retrieve the OpenAI API key from environment variables
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

# 3. Connect to OpenSearch / Initialize the OpenSearch client
IS_AUTH = True

if IS_AUTH:
    # Initialize the OpenSearch client
    client = OpenSearch(
        hosts=[{'host': '192.168.0.111', 'port': 9200}],
        http_auth=('admin', 'Padmasini10'),  # Replace with your credentials
        use_ssl=True,
        verify_certs=False,
        ssl_assert_hostname = False,
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
        "plugins.ml_commons.trusted_connector_endpoints_regex": "^https://api\\.openai\\.com/.*$",
        "plugins.ml_commons.only_run_on_ml_node": "false",
        "plugins.ml_commons.memory_feature_enabled": "true"
    }
}
client.cluster.put_settings(body=cluster_settings)

# 11. Register model group
llm_model_group_body = {
  "name": "openai_model_group",
  "description": "A model group for open ai models"
}
response = client.transport.perform_request('POST', '/_plugins/_ml/model_groups/_register', body=llm_model_group_body)
print("Model group registered:", response)
llm_model_group_id = response['model_group_id']

# 12. Create connector
llm_connector_body = {
    "name": "OpenAI Chat Connector",
    "description": "The connector to public OpenAI model service for GPT-4o-mini",
    "version": 1,
    "protocol": "http",
    "parameters": {
        "endpoint": "api.openai.com",
        "model": "gpt-4o-mini",
        # "response_filter": "$.choices[0].text"
    },
    "credential": {
        "openAI_key": OPENAI_API_KEY
    },
    "actions": [
        {
            "action_type": "predict",
            "method": "POST",
            "url": "https://${parameters.endpoint}/v1/chat/completions",
            "headers": {
                "Authorization": "Bearer ${credential.openAI_key}"
            },
            "request_body": "{ \"model\": \"${parameters.model}\", \"messages\": ${parameters.messages} }"
        }
    ]
}
response = client.transport.perform_request('POST', '/_plugins/_ml/connectors/_create', body=llm_connector_body)
print("Connector created:", response)
llm_connector_id = response['connector_id']

# 13. Register model
llm_model_body = {
    "name": "openAI-gpt-4o-mini",
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


# Path to your image
image_path = "diapers.png"

# Encoding the image
base64_image = encode_image(image_path)

# 16. Test prediction
test_llm_predict_body = {
  "parameters": {
    "messages": [
    {
      "role": "user",
      "content": [
        {
          "type": "text",
          "text": "What’s in this image?"
        },
        {
          "type": "image_url",
          "image_url": {
            "url": f"data:image/jpeg;base64,{base64_image}"
          }
        }
      ]
    }
  ]
  }
}
predict_response = client.transport.perform_request(
    'POST',
    f'/_plugins/_ml/models/{llm_model_id}/_predict',
    body=test_llm_predict_body
)

print(json.dumps(predict_response, indent=2))


