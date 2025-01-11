from opensearchpy import OpenSearch
import os, time, json
from dotenv import load_dotenv
# import mlcommon to later register the model to OpenSearch Cluster
from opensearch_py_ml.ml_commons import MLCommonClient
from opensearch_py_ml.ml_models import SentenceTransformerModel
import warnings
warnings.filterwarnings('ignore', category=DeprecationWarning)
warnings.filterwarnings('ignore', category=FutureWarning)
warnings.filterwarnings("ignore", message="Unverified HTTPS request")
warnings.filterwarnings("ignore", message="using SSL with verify_certs=False is insecure.")

# 1. Load environment variables from .env file
load_dotenv("../../.env")

# 2. Retrieve the OpenAI API key from environment variables
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

CLUSTER_URL = {'host': '192.168.0.111', 'port': 9200}

def get_os_client(cluster_url = CLUSTER_URL,
          username='admin',
          password='Developer@123'):
  '''
  Get OpenSearch client
  :param cluster_url: cluster URL like https://ml-te-netwo-1s12ba42br23v-ff1736fa7db98ff2.elb.us-west-2.amazonaws.com:443
  :return: OpenSearch client
  '''
  client = OpenSearch(
    hosts=[cluster_url], #[cluster_url], # {'host': '192.168.0.111', 'port': 9200}
    http_auth=(username, password),
    verify_certs=False,
    ssl_assert_hostname = False,
    ssl_show_warn=False,
    use_ssl=True
  )
  return client

client = get_os_client()
# 3. Connect to ml_common client with OpenSearch client
ml_client = MLCommonClient(client)

# 4. Modify cluster settings
cluster_settings = {
  "persistent": {
  "plugins.ml_commons.trusted_connector_endpoints_regex": "^https://api\\.openai\\.com/.*$",
  "plugins.ml_commons.only_run_on_ml_node": "false",
  "plugins.ml_commons.memory_feature_enabled": "true",
  "plugins": {
      "ml_commons": {
        "allow_registering_model_via_url": "true",
        "allow_registering_model_via_local_file": "true",
        "only_run_on_ml_node": "false",
        "model_access_control_enabled": "true",
        "native_memory_threshold": "99"
      }
    }
  }
}
client.cluster.put_settings(body=cluster_settings)

# 5. Map the manage_snapshots role to the current user especially when security is enabled
# https://opensearch.org/docs/latest/tuning-your-cluster/availability-and-recovery/snapshots/snapshot-restore/#security-considerations
role_mapping_body = {
  "users": ["admin"]
}

try:
  response = client.security.create_role_mapping(
    role='manage_snapshots',
    body=role_mapping_body
  )
  print(f"Role mapping created successfully: {response}")
except Exception as e:
  print(f"Error creating role mapping: {e}")

####*************** Below is because we want to use msmarco-distilbert-base-v2, which is not default supported opensearch**************####

# 6. Use the SentenceTransformerModel class to register a model to OpenSearch Cluster
embedding_model_name = "sentence-transformers/msmarco-distilbert-base-v2"
folder_path = "sentence-transformer-onnx/msmarco-distilbert-base-v2"

# 7. Initialize the SentenceTransformerModel
pre_trained_model = SentenceTransformerModel(model_id=embedding_model_name, overwrite=True)

# 8. Save the model to a directory
model_path_onnx = pre_trained_model.save_as_onnx(model_id=embedding_model_name)

# 9. Zip the model
print(f'Model saved and zipped at {model_path_onnx}')

# 10. Model config file
model_config_path_onnx = pre_trained_model.make_model_config_json(model_format='ONNX')

# 11. Register the model to OpenSearch Cluster, deploy automatically
embedding_model_id = ml_client.register_model(model_path_onnx, model_config_path_onnx, isVerbose=True, wait_until_deployed=True)

print(f"Model {embedding_model_id} registered successfully")

# 12. Create ingest pipeline
pipeline_body = {
  "description": "A text embedding pipeline",
  "processors": [
    {
      "text_embedding": {
        "model_id": embedding_model_id,
        "field_map": {
          "JOB_TITLE": "JOB_TITLE_EMBEDDING"
        }
      }
    }
  ]
}
client.ingest.put_pipeline(id="test-pipeline-local-model", body=pipeline_body)

####### Restore interns_all snapshot ########
# 13. Define the repository and snapshot name
repository_name = 'my_backup_repo'
snapshot_name = 'interns_snapshot'
index_name = "interns"

# 14. Create the repository
repository_settings = {
  "type": "fs",
  "settings": {
    "location": "/usr/share/opensearch/snapshots"
  }
}

# 15. Restore the snapshot
restore_body = {
  "indices": index_name,  # Restore all indices, you can specify specific indices if needed
  "ignore_unavailable": True,
  "include_global_state": False
}

client.snapshot.create_repository(repository_name, body=repository_settings)

# 16. Delete if index already exists
try:
  client.indices.delete(index='interns')
except Exception as e:
  print("Index not found:", e)

# 17. Restore the snapshot
try:
  response = client.snapshot.restore(
    repository=repository_name,
    snapshot=snapshot_name,
    body=restore_body,
    wait_for_completion=True
  )
  print("Snapshot restored successfully:", response)
except Exception as e:
  print("Error restoring snapshot:", e)


########## Register OpenAI model to OpenSearch Cluster ##########

# 18. Register model group
llm_model_group_body = {
  "name": "openai_model_group",
  "description": "A model group for open ai models"
}
response = client.transport.perform_request('POST', '/_plugins/_ml/model_groups/_register', body=llm_model_group_body)
print("Model group registered:", response)
llm_model_group_id = response['model_group_id']

# 19. Create connector
llm_connector_body = {
  "name": "OpenAI Chat Connector",
  "description": "The connector to public OpenAI model service for GPT 3.5",
  "version": 1,
  "protocol": "http",
  "parameters": {
    "endpoint": "api.openai.com",
    "model": "gpt-3.5-turbo"
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

# 20. Register model
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

# 21. Deploy the model and wait for the status to become completed
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

# 22. Wait for deployment to complete
while True:
  status_response = client.transport.perform_request('GET', f'/_plugins/_ml/models/{llm_model_id}')
  if status_response['model_state'] == 'DEPLOYED':
    print("Model deployed successfully")
    break
  time.sleep(5)

# 23. Test prediction
test_llm_predict_body = {
  "parameters": {
  "messages": [
    {
    "role": "system",
    "content": "You are a helpful assistant."
    },
    {
    "role": "user",
    "content": "Hello!"
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

# 24. Register an Agent

agent_register_body = {
  "name": "Test_Agent_For_RAG",
  "type": "flow",
  "description": "this is a recruiter agent",
  "tools": [
  {
    "type": "VectorDBTool",
    "parameters": {
    "model_id": embedding_model_id,
    "index": index_name,
    "embedding_field": "JOB_CONTENT_TEXT_EMBEDDING",
    "source_field": [
      "JOB_CONTENT_TEXT"
    ],
    "input": "${parameters.question}"
    }
  },
  {
    "type": "MLModelTool",
    "description": "A general tool to answer any question",
    "parameters": {
    "model_id": llm_model_id,
    "messages": [
      {
      "role": "system",
      "content": "You are a professional recruiter. You will always answer a question based on the given context first. If the answer is not directly shown in the context, you will analyze the data and find the answer. If you don't know the answer, just say you don't know."
      },
      {
      "role": "user",
      "content": "Context:\n${parameters.VectorDBTool.output}\n\nQuestion:${parameters.question}\n\n"
      }
    ]
    }
  }
  ]
}

agent_response = client.transport.perform_request('POST', '/_plugins/_ml/agents/_register', body=agent_register_body)
print("Agent registered:", agent_response)
agent_id = agent_response['agent_id']

# 25. Inspect agent

inspect_response = client.transport.perform_request('GET', f'/_plugins/_ml/agents/{agent_id}')
print("Agent inspected:", inspect_response)

# 26. Execute agent

execute_body = {
  "parameters": {
  "question": "What is the lowest and highest salary for senior frontend engineer ?"
  }
}

execute_response = client.transport.perform_request(
  'POST', 
  f'/_plugins/_ml/agents/{agent_id}/_execute', 
  body=execute_body,
)
print("Agent executed:", execute_response)
