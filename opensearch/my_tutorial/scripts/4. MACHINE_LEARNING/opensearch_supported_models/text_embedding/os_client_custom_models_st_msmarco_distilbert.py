# The below doesn't use MLCommons client. MLCommons client is used when you prepare the model outside and want to use in opensearch
# However this is a low level script to show how to register, deploy, predict, undeploy and delete a model using OpenSearch Python client.
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


mode_group_name = f"local_model_group_{int(time.time())}"
print(f"Registering model group: {mode_group_name}")
# Register a model group
model_group_response = client.transport.perform_request(
    method='POST',
    url='/_plugins/_ml/model_groups/_register',
    body={
        "name": mode_group_name,
        "description": "A model group for local models"
    }
)

# Extract model_group_id from the response
model_group_id = model_group_response['model_group_id']

print(f"Model group ID: {model_group_id}")

# Register a model
# Custom model requires all key value pairs in the model_config field (unlike registered models that MLCommons client registers)
register_response = client.transport.perform_request(
    method='POST',
    url='/_plugins/_ml/models/_register',
    body={
        "name": "huggingface/sentence-transformers/msmarco-distilbert-base-tas-b",
        "version": "1.0.1",
        "model_group_id": model_group_id,
        "description": "This is a port of the DistilBert TAS-B Model to sentence-transformers model: It maps sentences and paragraphs to a 768 dimensional dense vector space and is optimized for the task of semantic search.",
        "function_name": "TEXT_EMBEDDING",
        "model_format": "TORCH_SCRIPT",
        "model_content_size_in_bytes": 266352827,
        "model_content_hash_value": "acdc81b652b83121f914c5912ae27c0fca8fabf270e6f191ace6979a19830413",
        "model_config": {
            "model_type": "distilbert",
            "embedding_dimension": 768,
            "framework_type": "sentence_transformers",
            "all_config": """{"_name_or_path":"old_models/msmarco-distilbert-base-tas-b/0_Transformer","activation":"gelu","architectures":["DistilBertModel"],"attention_dropout":0.1,"dim":768,"dropout":0.1,"hidden_dim":3072,"initializer_range":0.02,"max_position_embeddings":512,"model_type":"distilbert","n_heads":12,"n_layers":6,"pad_token_id":0,"qa_dropout":0.1,"seq_classif_dropout":0.2,"sinusoidal_pos_embds":false,"tie_weights_":true,"transformers_version":"4.7.0","vocab_size":30522}"""
        },
        "created_time": 1676073973126,
        "url": "https://artifacts.opensearch.org/models/ml-models/huggingface/sentence-transformers/msmarco-distilbert-base-tas-b/1.0.1/torch_script/sentence-transformers_msmarco-distilbert-base-tas-b-1.0.1-torch_script.zip"
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
    url=f'/_plugins/_ml/_predict/text_embedding/{model_id}',
    body={
        "text_docs": ["today is sunny"],
        "return_number": True,
        "target_response": ["sentence_embedding"]
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