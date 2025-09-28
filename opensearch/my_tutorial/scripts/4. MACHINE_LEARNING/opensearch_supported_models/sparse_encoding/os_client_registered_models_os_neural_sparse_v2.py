# The below doesn't use MLCommons client. MLCommons client is used when you prepare the model outside and want to use in opensearch
# However this is a low level script to show how to register, deploy, predict, undeploy and delete a model using OpenSearch Python client.

# Sparse encoding models transfer text into a sparse vector and convert the vector to a list of <token: weight> pairs representing the text entry and its corresponding weight in the sparse vector

# Sparse encoding models - https://docs.opensearch.org/latest/ml-commons-plugin/pretrained-models/sparse-encoding-models/

from opensearchpy import OpenSearch, RequestsHttpConnection
import time

HOST = 'localhost' # Replace with your OpenSearch host
# Initialize the OpenSearch client
client = OpenSearch(
    hosts=[{'host': HOST, 'port': 9200}],
    http_auth=('admin', 'Developer@123'),  # Replace with your credentials
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

model_group_name = f"local_model_group_{int(time.time())}"
print(f"Registering model group: {model_group_name}")
# Register a model group
model_group_response = client.transport.perform_request(
    method='POST',
    url='/_plugins/_ml/model_groups/_register',
    body={
        "name": model_group_name,
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
        "name": "amazon/neural-sparse/opensearch-neural-sparse-encoding-v2-distill",
        "version": "1.0.0",
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
    url=f'/_plugins/_ml/_predict/sparse_encoding/{model_id}',
    body={
        "text_docs": ["today is sunny"]
    }
)
print(prediction)

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