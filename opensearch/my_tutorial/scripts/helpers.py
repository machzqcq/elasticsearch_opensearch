from opensearchpy import OpenSearch, helpers
from sentence_transformers import SentenceTransformer
import pandas as pd
import os
import json
import hashlib


def opensearch_client(host, port, auth=None, ssl=False):
    client = OpenSearch(
        hosts=[{'host': host, 'port': port}],
        http_auth=auth if auth else None,
        use_ssl=ssl,
        verify_certs=False,
        ssl_show_warn=False
    )
    info = client.info()
    print(f"Welcome to {info['version']['distribution']} {info['version']['number']}!")
    return client

def opensearch_bulk_sync(client, index_name, df, mapping=None):
    if client.indices.exists(index=index_name):
        client.indices.delete(index=index_name)
    
    if mapping:
        client.indices.create(index=index_name, body=mapping)
    else:
        client.indices.create(index=index_name)

    data = [
        {"_index": index_name, "_id": i, "_source": row.to_dict()}
        for i, row in df.iterrows()
    ]

        
    success, failed = helpers.bulk(client=client, actions=data)
    return success, failed

def opensearch_bulk_async(client, index_name, df, mapping=None, delete_index=False):
    if delete_index and client.indices.exists(index=index_name):
        print(f"Deleting index {index_name}")
        client.indices.delete(index=index_name)
    if mapping:
        print(f"Creating index {index_name} with mapping {mapping}")
        client.indices.create(index=index_name, body=mapping)
    else:
        client.indices.create(index=index_name)
        
    data = dataframe_to_actions(df, index_name)
    success, failed = helpers.bulk(client=client, actions=data)
    return success, failed

def opensearch_bulk_async_with_embeddings(client, index_name, df, mapping=None, delete_index=False, 
                                          embedding_model=None, embedding_source_destination_map=None):
    if delete_index and client.indices.exists(index=index_name):
        print(f"Deleting index {index_name}")
        client.indices.delete(index=index_name)
    if mapping:
        print(f"Creating index {index_name} with mapping {mapping}")
        client.indices.create(index=index_name, body=mapping)
    else:
        client.indices.create(index=index_name)
    
    if embedding_source_destination_map:
        for source, destination in embedding_source_destination_map.items():
            print(f"Adding embeddings from {source} to {destination}")
            df = add_embeddings_from_source_to_destination(df, source, destination, embedding_model)

    data = dataframe_to_actions(df, index_name)
    success, failed = helpers.bulk(client=client, actions=data)
    return success, failed

def add_embeddings_from_source_to_destination(df, source, destination, embedding_model_name):
    model = SentenceTransformer(embedding_model_name)
    df.loc[:, destination] = df[source].apply(lambda x: model.encode(str(x)).tolist() if x else None)
    return df

def return_index_mapping_with_vectors(vectorize_fields,mapping=None):
    # Create OpenSearch mapping for each field with corresponding embedding vector
    if mapping:
        print(f"Using existing mapping: {mapping}")
        mappings = mapping
        mappings["settings"] = {
            "index": {
            "knn": True
            }
        }
        for field in vectorize_fields:
            mappings["mappings"]["properties"][field] = {"type": "text"}
    else:
        mappings = {
            "settings": {
                "index": {
                    "knn": True
                }
            },
            "mappings": {
                "properties": {
                    field: {"type": "text"} for field in vectorize_fields
                }
            }
        }

    # Add KNN vector fields to the mapping
    for field in vectorize_fields:
        mappings["mappings"]["properties"][f"{field}_EMBEDDING"] = {
            "type": "knn_vector",
            "dimension": 768,
            "method": {
                "name": "hnsw",
                "space_type": "l2",
                "engine": "lucene"
            }
        }

    mappings["mappings"]["properties"] = {k: v for k, v in mappings["mappings"]["properties"].items() if k.endswith("_EMBEDDING")}
    return mappings

def dataframe_to_actions(df, index_name):
    for i, row in df.iterrows():
        yield {
            "_index": index_name,
            "_id": i,
            "_source": row.to_dict()
        }


"""
# Generate the API request body for registering a model in OpenSearch (uses tokenizer.json and model_config.json)
folder_path = '/path/to/your/folder'
model_group_id = 'your_model_group_id'
model_name = 'huggingface/sentence-transformers/msmarco-distilbert-base-tas-b'
model_version = '1.0.1'
description = 'This is a port of the DistilBert TAS-B Model to sentence-transformers model: It maps sentences & paragraphs to a 768 dimensional dense vector space and is optimized for the task of semantic search.'
function_name = 'TEXT_EMBEDDING'
model_format = 'TORCH_SCRIPT'
url = 'https://artifacts.opensearch.org/models/ml-models/huggingface/sentence-transformers/msmarco-distilbert-base-tas-b/1.0.1/torch_script/sentence-transformers_msmarco-distilbert-base-tas-b-1.0.1-torch_script.zip'

opensearch_body = generate_opensearch_body_json(folder_path, model_group_id, model_name, model_version, description, function_name, model_format, url)
print(json.dumps(opensearch_body, indent=4))
"""
def generate_opensearch_body_json(folder_path, model_group_id, model_name, model_version, description, function_name, model_format, url):
    # Read the config.json file
    config_file = os.path.join(folder_path, 'config.json')
    with open(config_file, 'r') as f:
        config_data = json.load(f)
    
    # Read the tokenizer.json file
    tokenizer_file = os.path.join(folder_path, 'tokenizer.json')
    with open(tokenizer_file, 'r') as f:
        tokenizer_data = json.load(f)
    
    # Identify the .pt file
    pt_file = None
    for file in os.listdir(folder_path):
        if file.endswith('.pt'):
            pt_file = os.path.join(folder_path, file)
            break
    
    if not pt_file:
        raise FileNotFoundError("No .pt file found in the specified folder.")
    
    # Calculate the size and hash of the .pt file
    model_content_size_in_bytes = os.path.getsize(pt_file)
    with open(pt_file, 'rb') as f:
        model_content_hash_value = hashlib.sha256(f.read()).hexdigest()
    
    # Construct the model_config
    model_config = {
        "model_type": config_data.get("model_type", "distilbert"),
        "embedding_dimension": config_data.get("dim", 768),
        "framework_type": "sentence_transformers",
        "all_config": json.dumps(config_data)
    }
    
    # Construct the final JSON body
    opensearch_body = {
        "name": model_name,
        "version": model_version,
        "model_group_id": model_group_id,
        "description": description,
        "function_name": function_name,
        "model_format": model_format,
        "model_content_size_in_bytes": model_content_size_in_bytes,
        "model_content_hash_value": model_content_hash_value,
        "model_config": model_config,
        "created_time": int(os.path.getmtime(pt_file) * 1000),  # Convert to milliseconds
        "url": url
    }
    
    return opensearch_body


def create_embedding_model(os_client, model_group_name,model_body):
    from opensearchpy import OpenSearch, RequestsHttpConnection
    import time

    # Update cluster settings
    os_client.cluster.put_settings(body={
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

    if model_group_name:
        # Register a model group
        model_group_response = os_client.transport.perform_request(
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
        register_response = os_client.transport.perform_request(
            method='POST',
            url='/_plugins/_ml/models/_register',
            body=model_body
        )

    else: 
        # Register a model
        register_response = os_client.transport.perform_request(
            method='POST',
            url='/_plugins/_ml/models/_register',
            body=model_body
        )

    # Extract task_id from the response
    register_task_id = register_response['task_id']

    # Get task status
    while True:
        task_status = os_client.transport.perform_request(
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
    deploy_response = os_client.transport.perform_request(
        method='POST',
        url=f'/_plugins/_ml/models/{model_id}/_deploy'
    )
    print(deploy_response)
    # Extract deployment task_id from the response
    deploy_task_id = deploy_response['task_id']
    # Wait until the deployment status becomes completed
    while True:
        deployment_status = os_client.transport.perform_request(
            method='GET',
            url=f'/_plugins/_ml/tasks/{deploy_task_id}'
        )
        print(deployment_status)
        if deployment_status['state'] == 'COMPLETED':
            break
        time.sleep(10)  # Wait for 10 seconds before checking again

    # Make a prediction
    prediction = os_client.transport.perform_request(
        method='POST',
        url=f'/_plugins/_ml/_predict/text_embedding/{model_id}',
        body={
            "text_docs": ["today is sunny"],
            "return_number": True,
            "target_response": ["sentence_embedding"]
        }
    )
    print(prediction)
    print(f"Model ID: {model_id}")
    return model_id


from huggingface_hub import HfApi

def get_sentence_transformer_models():
    """Fetches a list of all Sentence Transformer models using the Hugging Face API."""

    api = HfApi()
    models = api.list_models(author="sentence-transformers")

    model_names = [model.modelId for model in models]
    return model_names