from opensearchpy import OpenSearch, helpers
from sentence_transformers import SentenceTransformer
import pandas as pd
import os
import json
import hashlib, base64


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

def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')
    

def restore_interns_all_snapshot(client):

    # Define the repository and snapshot name
    repository_name = 'my_backup_repo'
    snapshot_name = 'interns_snapshot'
    index_name = "interns"

    # Create the repository
    repository_settings = {
        "type": "fs",
        "settings": {
            "location": "/usr/share/opensearch/snapshots"
        }
    }

    # Restore the snapshot
    restore_body = {
        "indices": index_name,  # Restore all indices, you can specify specific indices if needed
        "ignore_unavailable": True,
        "include_global_state": False
    }

    client.snapshot.create_repository(repository_name, body=repository_settings)

    # Delete if index already exists
    try:
        client.indices.delete(index='interns')
    except Exception as e:
        print("Index not found:", e)

    # Restore the snapshot
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

    return True


# Create OpenAI connector
def create_openai_connector(client, openai_key):
    connector_body = {
        "name": "OpenAI GPT-3.5 Connector",
        "description": "Connector to OpenAI GPT-3.5 model",
        "version": 1,
        "protocol": "http",
        "parameters": {
            "endpoint": "api.openai.com",
            "model": "gpt-3.5-turbo"
        },
        "credential": {
            "openai_key": openai_key
        },
        "actions": [
            {
                "action_type": "predict",
                "method": "POST",
                "url": "https://${parameters.endpoint}/v1/chat/completions",
                "headers": {
                    "Authorization": "Bearer ${credential.openai_key}",
                    "Content-Type": "application/json"
                },
                "request_body": "{ \"model\": \"${parameters.model}\", \"messages\": [{\"role\":\"system\",\"content\":\"${parameters.system_instruction}\"},{\"role\":\"user\",\"content\":\"${parameters.prompt}\"}] }"
            }
        ]
    }
    
    response = client.transport.perform_request('POST', '/_plugins/_ml/connectors/_create', body=connector_body)
    return response['connector_id']

# Register the model
def register_openai_model(client, connector_id):
    model_body = {
        "name": "OpenAI GPT-3.5 Model",
        "function_name": "remote",
        "description": "OpenAI GPT-3.5 model for text generation",
        "connector_id": connector_id
    }
    
    response = client.transport.perform_request('POST', '/_plugins/_ml/models/_register', body=model_body)
    return response['model_id']

# Deploy the model
import time
def deploy_openai_model(client, model_id):
    register_openai_model = client.transport.perform_request('POST', f'/_plugins/_ml/models/{model_id}/_deploy')
    # wait for the model to be deployed
    register_openai_task_id = register_openai_model['task_id']
    # Monitor task status
    while True:
        task_status = client.transport.perform_request('GET', f'/_plugins/_ml/tasks/{register_openai_task_id}')
        if task_status['state'] == 'COMPLETED':
            # Extract model_id from the response
            openai_model_id = task_status['model_id']
            break
        time.sleep(5)

    print(f"Open ai model ID: {openai_model_id} deployed successfully")
    return openai_model_id

# Create a conversational agent
def create_conversational_agent(client, model_id, embedding_model_id):
    agent_body = {
        "name": "OpenAI RAG Chatbot",
        "type": "conversational",
        "description": "RAG chatbot using OpenAI GPT-3.5",
        "app_type": "chat_with_rag",
        "llm": {
            "model_id": model_id,
            "parameters": {
                "max_iteration": 3,
                "response_filter": "$.choices[0].message.content",
                "system_instruction": "You are an assistant which is designed to be able to assist with a wide range of tasks, from answering simple questions to providing in-depth explanations and discussions on a wide range of topics.",
                "prompt": "Assistant can ask Human to use tools to look up information that may be helpful in answering the users original question.\n${parameters.tool_descriptions}\n\n${parameters.chat_history}\n\n${parameters.prompt.format_instruction}\n\nHuman: ${parameters.question}\n\n${parameters.scratchpad}\n\nHuman: follow RESPONSE FORMAT INSTRUCTIONS\n\nAssistant:",
            }
        },
        "memory": {
            "type": "conversation_index"
        },
        "tools": [
            {
                "type": "VisualizationTool",
                "parameters": {
                    "index": ".kibana"
                },
                "include_output_in_agent_response": True
            },
            {
                "type": "VectorDBTool",
                "name": "population_knowledge_base",
                "parameters": {
                    "model_id": embedding_model_id,
                    "index": "test_population_data",
                    "embedding_field": "population_description_embedding",
                    "source_field": ["population_description"],
                    "input": "${parameters.input}"
                }
            },
            {
                "type": "VectorDBTool",
                "name": "stock_price_knowledge_base",
                "parameters": {
                    "model_id": embedding_model_id,
                    "index": "test_stock_price_data",
                    "embedding_field": "stock_price_history_embedding",
                    "source_field": ["stock_price_history"],
                    "input": "${parameters.input}"
                }
            },
            {
                "type": "CatIndexTool",
                "description": "Use this tool to get OpenSearch index information: (health, status, index, uuid, primary count, replica count, docs.count, docs.deleted, store.size, primary.store.size). \nIt takes 2 optional arguments named `index` which is a comma-delimited list of one or more indices to get information from (default is an empty list meaning all indices), and `local` which means whether to return information from the local node only instead of the cluster manager node (default is false)."
            },
            {
                "type": "SearchAnomalyDetectorsTool"
            },
            {
                "type": "SearchAnomalyResultsTool"
            },
            {
                "type": "SearchMonitorsTool"
            },
            {
                "type": "SearchAlertsTool"
            },
        ]
    }
    
    response = client.transport.perform_request('POST', '/_plugins/_ml/agents/_register', body=agent_body)
    return response['agent_id']

# Execute the agent
def execute_agent(client, agent_id, question, memory_id=None):
    execute_body = {
        "parameters": {
            "question": question
        }
    }
    if memory_id:
        execute_body["memory_id"] = memory_id
    
    response = client.transport.perform_request('POST', f'/_plugins/_ml/agents/{agent_id}/_execute', body=execute_body)
    return response

# Execute the agent
def execute_agent_tools(client, agent_id, question, selected_tools):
    execute_body = {
        "parameters": {
            "question": question,
            "verbose": True,
            "selected_tools": selected_tools
        }
    }
    
    response = client.transport.perform_request('POST', f'/_plugins/_ml/agents/{agent_id}/_execute', body=execute_body)
    return response

# Create a conversational agent
def create_root_agent(client, agent_id, model_id):
    agent_body = {
    "name": "Chatbot agent",
    "type": "flow",
    "description": "this is a test chatbot agent",
    "tools": [
        {
        "type": "AgentTool",
        "name": "LLMResponseGenerator",
        "parameters": {
            "agent_id": agent_id 
        },
        "include_output_in_agent_response": True
        },
        {
        "type": "MLModelTool",
        "name": "QuestionSuggestor",
        "description": "A general tool to answer any question",
        "parameters": {
            "model_id": model_id,  
            "prompt": "Human:  You are an AI that only speaks JSON. Do not write normal text. Output should follow example JSON format: \n\n {\"response\": [\"question1\", \"question2\"]}\n\n. \n\nHuman:You will be given a chat history between OpenSearch Assistant and a Human.\nUse the context provided to generate follow up questions the Human would ask to the Assistant.\nThe Assistant can answer general questions about logs, traces and metrics.\nAssistant can access a set of tools listed below to answer questions given by the Human:\nQuestion suggestions generator tool\nHere's the chat history between the human and the Assistant.\n${parameters.LLMResponseGenerator.output}\nUse the following steps to generate follow up questions Human may ask after the response of the Assistant:\nStep 1. Use the chat history to understand what human is trying to search and explore.\nStep 2. Understand what capabilities the assistant has with the set of tools it has access to.\nStep 3. Use the above context and generate follow up questions.Step4:You are an AI that only speaks JSON. Do not write normal text. Output should follow example JSON format: \n\n {\"response\": [\"question1\", \"question2\"]} \n \n----------------\n\nAssistant:"
        },
        "include_output_in_agent_response": True
        }
    ],
    "memory": {
        "type": "conversation_index"
    }
    }
    
    response = client.transport.perform_request('POST', '/_plugins/_ml/agents/_register', body=agent_body)
    return response['agent_id']


