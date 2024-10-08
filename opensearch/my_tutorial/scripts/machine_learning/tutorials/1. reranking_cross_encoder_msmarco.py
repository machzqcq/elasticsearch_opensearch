# The below doesn't use MLCommons client. MLCommons client is used when you prepare the model outside and want to use in opensearch
# However this is a low level script to show how to register, deploy, predict, undeploy and delete a model using OpenSearch Python client.

# The model calculates the similarity score of query_text and each document in text_docs and returns a list of scores for each document in the order they were provided in text_docs
from opensearchpy import OpenSearch, RequestsHttpConnection
import time
import sys
sys.path.append('../../')
from helpers import restore_interns_all_snapshot

# Initialize the OpenSearch client
client = OpenSearch(
    hosts=[{'host': '192.168.0.111', 'port': 9200}],
    http_auth=('admin', 'Padmasini10'),  # Replace with your credentials
    use_ssl=True,
    verify_certs=False,
    connection_class=RequestsHttpConnection
)

# Update cluster settings
client.cluster.put_settings(body={
    "persistent": {
        "plugins": {
            "ml_commons": {
                "allow_registering_model_via_url": "true",
                "only_run_on_ml_node": "false",
                "model_access_control_enabled": "true",
                "native_memory_threshold": "99"
            }
        }
    }
})

# Register a model group
model_group_response = client.transport.perform_request(
    method='POST',
    url='/_plugins/_ml/model_groups/_register',
    body={
        "name": "local_model_group",
        "description": "A model group for local models"
    }
)

# Extract model_group_id from the response
model_group_id = model_group_response['model_group_id']

print(f"Model group ID: {model_group_id}")

# Register a model
register_response = client.transport.perform_request(
    method='POST',
    url='/_plugins/_ml/models/_register',
    body={
        "name": "huggingface/cross-encoders/ms-marco-MiniLM-L-6-v2",
        "version": "1.0.2",
        "model_group_id": model_group_id,
        "model_format": "TORCH_SCRIPT"
    }
)

# Extract task_id from the response
register_task_id = register_response['task_id']

# Get task status
while True:
    task_status = client.transport.perform_request(
            method='GET',
            url=f'/_plugins/_ml/tasks/{register_task_id}'
    )
    print(task_status)
    if task_status['state'] == 'COMPLETED':
            # Extract model_id from the deployment response
            model_id = task_status['model_id']
            break
    time.sleep(10)  # Wait for 10 seconds before checking again

# Deploy the model
deploy_response = client.transport.perform_request(
    method='POST',
    url=f'/_plugins/_ml/models/{model_id}/_deploy'
)
print(deploy_response)


# Extract deployment task_id from the response
deploy_task_id = deploy_response['task_id']

# Wait until the deployment status becomes completed
while True:
    deployment_status = client.transport.perform_request(
        method='GET',
        url=f'/_plugins/_ml/tasks/{deploy_task_id}'
    )
    print(deployment_status)
    if deployment_status['state'] == 'COMPLETED':
        break
    time.sleep(10)  # Wait for 10 seconds before checking again

# Make a prediction
prediction = client.transport.perform_request(
    method='POST',
    url=f'/_plugins/_ml/models/{model_id}/_predict',
    body={
        "query_text": "today is sunny",
        "text_docs": [
            "how are you",
            "today is sunny",
            "today is july fifth",
            "it is winter"
        ]
    }
)
print(prediction)

# Map the manage_snapshots role to the current user especially when security is enabled
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

# restore a snapshot
if restore_interns_all_snapshot(client):
    print("Snapshot restored successfully")
else:
    print("Error restoring snapshot")

# cretae a reranking pipeline
reranking_pipeline_response = client.transport.perform_request(
    method='PUT',
    url='/_search/pipeline/reranking_pipeline',
    body={
    "description": "Pipeline for reranking cross-encoder model",
    "response_processors": [
        {
            "rerank": {
                "ml_opensearch": {
                    "model_id": model_id
                },
                "context": {
                    "document_fields": ["JOB_TITLE"]
                }
            }
        }
    ]
}
)

print(reranking_pipeline_response)

# Test the reranking pipeline
search_response_pipeline = client.transport.perform_request(
    method='GET',
    url='/interns/_search?search_pipeline=reranking_pipeline',
    body={
  "query": {
    "match": {"JOB_TITLE": "content writer"}
  },
  "size": 4,
  "ext": {
    "rerank": {
      "query_context": {
         "query_text": "content writer"
      }
    }
  },
  # disable the _source field
    "_source": False,
    # retrieve only the specified fields
    "fields": ["JOB_TITLE","COMPANY","LOCATION"]
}
)
print(search_response_pipeline)

# test without reranking pipeline
search_response_without_reranking = client.transport.perform_request(
    method='GET',
    url='/interns/_search',
    body={
  "query": {
    "match": {"JOB_TITLE": "content writer"}
  },
  "size": 4,
  "ext": {
    "rerank": {
      "query_context": {
         "query_text": "content writer"
      }
    }
  },
    # disable the _source field
    "_source": False,
    # retrieve only the specified fields
    "fields": ["JOB_TITLE","COMPANY","LOCATION"]
}
)
print(search_response_without_reranking)

# Delete the reranking pipeline
delete_reranking_pipeline_response = client.transport.perform_request(
    method='DELETE',
    url='/_search/pipeline/reranking_pipeline'
)

# Undeploy the model
undeploy_response = client.transport.perform_request(
    method='POST',
    url=f'/_plugins/_ml/models/{model_id}/_undeploy'
)
print(undeploy_response)

# Delete the model
delete_model_response = client.transport.perform_request(
    method='DELETE',
    url=f'/_plugins/_ml/models/{model_id}'
)
print(delete_model_response)

# Delete the model group
delete_model_group_response = client.transport.perform_request(
    method='DELETE',
    url=f'/_plugins/_ml/model_groups/{model_group_id}'
)
print(delete_model_group_response)