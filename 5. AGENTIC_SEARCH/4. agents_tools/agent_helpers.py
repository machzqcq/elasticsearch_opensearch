# ================================================================================
# AGENT HELPER FUNCTIONS - REUSABLE UTILITIES FOR AGENT NOTEBOOKS
# ================================================================================
"""
This module contains helper functions for creating and managing OpenSearch agents
with OpenAI models. These functions are designed to be reused across multiple
agent tool demonstration notebooks.
"""

import os
import time
import json
import warnings
from dotenv import load_dotenv
from opensearchpy import OpenSearch

# Suppress warnings
warnings.filterwarnings("ignore", message="Unverified HTTPS request")
warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", message="using SSL with verify_certs=False is insecure.")

# Load environment variables
load_dotenv("../../.env")

# Configuration
HOST = 'localhost'
PORT = 9200
DEFAULT_USERNAME = 'admin'
DEFAULT_PASSWORD = 'Developer@123'
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
OPENAI_MODEL = "gpt-4o-mini"


def get_os_client(host=HOST, port=PORT, username=DEFAULT_USERNAME, password=DEFAULT_PASSWORD):
    """
    Create and return an OpenSearch client with SSL configuration.
    
    Args:
        host (str): OpenSearch host
        port (int): OpenSearch port
        username (str): Username for authentication
        password (str): Password for authentication
        
    Returns:
        OpenSearch: Configured OpenSearch client instance
    """
    client = OpenSearch(
        hosts=[{'host': host, 'port': port}],
        http_auth=(username, password),
        verify_certs=False,
        ssl_assert_hostname=False,
        ssl_show_warn=False,
        use_ssl=True,
        timeout=300
    )
    return client


def configure_cluster_for_openai(client):
    """
    Configure OpenSearch cluster settings to allow OpenAI connector.
    
    Args:
        client: OpenSearch client instance
    """
    print("   Configuring cluster settings for OpenAI connector...")
    cluster_settings = {
        "persistent": {
            "plugins.ml_commons.trusted_connector_endpoints_regex": "^https://api\\.openai\\.com/.*$",
            "plugins.ml_commons.only_run_on_ml_node": "false",
            "plugins.ml_commons.memory_feature_enabled": "true"
        }
    }
    client.cluster.put_settings(body=cluster_settings)
    print("   ✓ Cluster settings configured successfully")


def wait_for_model_deployment(client, model_id, timeout=300, check_interval=5):
    """
    Wait for a model to reach DEPLOYED state.
    
    Args:
        client: OpenSearch client instance
        model_id (str): ID of the model to monitor
        timeout (int): Maximum time to wait in seconds
        check_interval (int): Time between status checks in seconds
        
    Returns:
        bool: True if model deployed successfully, False if timeout or error
    """
    start_time = time.time()
    while True:
        try:
            status_response = client.transport.perform_request('GET', f'/_plugins/_ml/models/{model_id}')
            current_status = status_response['model_state']
            print(f"      Model status: {current_status}")
            
            if current_status == 'DEPLOYED':
                print("      ✓ Model deployed successfully!")
                return True
            elif current_status == 'FAILED':
                print("      ✗ Model deployment failed!")
                return False
                
            if time.time() - start_time > timeout:
                print("      ✗ Model deployment timeout!")
                return False
                
            time.sleep(check_interval)
        except Exception as e:
            print(f"      ⚠ Error checking model status: {e}")
            time.sleep(check_interval)


def create_embedding_model(client):
    # ============================================================================
    # STEP 2: SETUP EMBEDDING MODEL FOR SEMANTIC SEARCH
    # ============================================================================
    
    print("STEP 2: Setting up Embedding Model (Semantic Search)...")
    print("   Registering HuggingFace sentence-transformers model...")
    
    embedding_model_body = {
        "name": "huggingface/sentence-transformers/all-MiniLM-L6-v2",
        "version": "1.0.1",
        "model_format": "TORCH_SCRIPT"
    }
    embedding_response = client.transport.perform_request(
        'POST', 
        '/_plugins/_ml/models/_register?deploy=true', 
        body=embedding_model_body
    )
    embedding_task_id = embedding_response['task_id']
    print(f"   Task ID: {embedding_task_id}")
    
    # Wait until the status becomes completed
    print("   ⏳ Waiting for embedding model registration to complete...")
    while True:
        embedding_model_status = client.transport.perform_request(
            method='GET',
            url=f'/_plugins/_ml/tasks/{embedding_task_id}'
        )
        status_state = embedding_model_status['state']
        print(f"      Registration status: {status_state}")
        if status_state == 'COMPLETED':
            embedding_model_id = embedding_model_status['model_id']
            print(f"   ✓ Embedding model registered with ID: {embedding_model_id}")
            break
        time.sleep(10)
    
    # Deploy the embedding model
    print("\n   Deploying embedding model...")
    deploy_body = {
        "deployment_plan": [
            {
                "model_id": embedding_model_id,
                "workers": 1
            }
        ]
    }
    
    try:
        client.transport.perform_request(
            'POST', 
            f'/_plugins/_ml/models/{embedding_model_id}/_deploy', 
            body=deploy_body
        )
    except Exception as e:
        print(f"   ⚠ Error deploying model: {e}")

    # Wait for deployment to complete
    print("   ⏳ Waiting for embedding model deployment...")
    wait_for_model_deployment(client, embedding_model_id)
    return embedding_model_id
    

def create_ingest_pipeline_and_index(client, embedding_model_id, bulk_body):
    # ============================================================================
    # STEP 3: CREATE INGEST PIPELINE AND INDEX
    # ============================================================================
    
    print("STEP 3: Creating Ingest Pipeline and Index...")
    
    # Create ingest pipeline
    pipeline_body = {
        "description": "A text embedding pipeline using HuggingFace model",
        "processors": [
            {
                "text_embedding": {
                    "model_id": embedding_model_id,
                    "field_map": {
                        "text": "embedding"
                    }
                }
            }
        ]
    }
    
    pipeline_id = f"openai-agent-pipeline_{int(time.time())}"
    client.ingest.put_pipeline(id=pipeline_id, body=pipeline_body)
    print(f"   ✓ Ingest pipeline created with ID: {pipeline_id}")
    
    # Create index with vector field for semantic search
    print("   Creating index with vector field for semantic search...")
    index_body = {
        "mappings": {
            "properties": {
                "text": {
                    "type": "text"
                },
                "embedding": {
                    "type": "knn_vector",
                    "dimension": 384,
                    "method": {
                        "name": "hnsw",
                        "engine": "lucene"
                    }
                }
            }
        },
        "settings": {
            "index": {
                "default_pipeline": pipeline_id,
                "knn": "true"
            }
        }
    }
    
    index_name = f"openai_agent_data_{int(time.time())}"
    client.indices.create(index=index_name, body=index_body)
    print(f"   ✓ Index created with name: {index_name}\n")
    
    client.bulk(body=bulk_body, index=index_name, pipeline=pipeline_id)
    print(f"   ✓ {len(bulk_body) // 2} documents indexed successfully\n")
    
    return index_name


def create_openai_connector(client, model_name=OPENAI_MODEL):
    """
    Create an OpenAI connector for chat completions.
    
    Args:
        client: OpenSearch client instance
        model_name (str): OpenAI model name (e.g., 'gpt-4o-mini')
        
    Returns:
        str: Connector ID
    """
    print(f"   Creating OpenAI connector for {model_name}...")
    connector_body = {
        "name": f"OpenAI {model_name} Connector",
        "description": f"Connector to OpenAI {model_name}",
        "version": 1,
        "protocol": "http",
        "parameters": {
            "endpoint": "api.openai.com",
            "model": model_name
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
                    "Authorization": "Bearer ${credential.openAI_key}",
                    "Content-Type": "application/json"
                },
                "request_body": "{\"model\": \"${parameters.model}\", \"messages\": ${parameters.messages}, \"temperature\": 0}"
            }
        ]
    }
    
    response = client.transport.perform_request('POST', '/_plugins/_ml/connectors/_create', body=connector_body)
    connector_id = response['connector_id']
    print(f"   ✓ Connector created: {connector_id}")
    return connector_id


def register_and_deploy_openai_model(client, connector_id, model_name=OPENAI_MODEL):
    """
    Register and deploy an OpenAI model.
    
    Args:
        client: OpenSearch client instance
        connector_id (str): Connector ID
        model_name (str): Model name for identification
        
    Returns:
        str: Model ID
    """
    # Create model group
    print("   Creating model group...")
    model_group_body = {
        "name": f"openai_{model_name}_group_{int(time.time())}",
        "description": f"Model group for OpenAI {model_name}"
    }
    response = client.transport.perform_request('POST', '/_plugins/_ml/model_groups/_register', body=model_group_body)
    model_group_id = response['model_group_id']
    print(f"   ✓ Model group created: {model_group_id}")
    
    # Register model
    print(f"   Registering {model_name} model...")
    model_body = {
        "name": f"openai-{model_name}-{int(time.time())}",
        "function_name": "remote",
        "model_group_id": model_group_id,
        "description": f"OpenAI {model_name} model",
        "connector_id": connector_id
    }
    response = client.transport.perform_request('POST', '/_plugins/_ml/models/_register', body=model_body)
    model_id = response['model_id']
    print(f"   ✓ Model registered: {model_id}")
    
    # Deploy model
    print("   Deploying model...")
    deploy_body = {
        "deployment_plan": [
            {
                "model_id": model_id,
                "workers": 1
            }
        ]
    }
    
    try:
        client.transport.perform_request('POST', f'/_plugins/_ml/models/{model_id}/_deploy', body=deploy_body)
    except Exception as e:
        print(f"   ⚠ Deploy request sent (error: {e})")
    
    print("   ⏳ Waiting for model deployment...")
    wait_for_model_deployment(client, model_id)
    
    return model_id


def create_flow_agent(client, agent_name, description, tools):
    """
    Create a flow agent with specified tools.
    
    Args:
        client: OpenSearch client instance
        agent_name (str): Name of the agent
        description (str): Description of the agent
        tools (list): List of tool configurations
        
    Returns:
        str: Agent ID
    """
    print(f"   Registering flow agent: {agent_name}...")
    agent_body = {
        "name": agent_name,
        "type": "flow",
        "description": description,
        "tools": tools
    }
    
    response = client.transport.perform_request('POST', '/_plugins/_ml/agents/_register', body=agent_body)
    agent_id = response['agent_id']
    print(f"   ✓ Agent registered: {agent_id}")
    return agent_id


def execute_agent(client, agent_id, parameters):
    """
    Execute an agent with given parameters.
    
    Args:
        client: OpenSearch client instance
        agent_id (str): Agent ID
        parameters (dict): Parameters to pass to the agent
        
    Returns:
        dict: Agent execution response
    """
    execute_body = {
        "parameters": parameters
    }
    
    response = client.transport.perform_request('POST', f'/_plugins/_ml/agents/{agent_id}/_execute', body=execute_body)
    return response


def print_agent_response(response, pretty=True):
    """
    Print agent response in a readable format.
    
    Args:
        response: Agent execution response
        pretty (bool): Whether to pretty-print JSON
    """
    if isinstance(response, dict):
        if 'inference_results' in response:
            for result in response['inference_results']:
                if 'output' in result:
                    for output in result['output']:
                        if 'result' in output:
                            print(f"\n   Result:")
                            if pretty:
                                try:
                                    result_data = json.loads(output['result']) if isinstance(output['result'], str) else output['result']
                                    print(json.dumps(result_data, indent=2))
                                except:
                                    print(output['result'])
                            else:
                                print(output['result'])
        else:
            print(json.dumps(response, indent=2))
    else:
        print(response)


def cleanup_resources(client, model_ids=None, agent_ids=None, index_names=None):
    """
    Clean up OpenSearch resources.
    
    Args:
        client: OpenSearch client instance
        model_ids (list): List of model IDs to undeploy and delete
        agent_ids (list): List of agent IDs to delete
        index_names (list): List of index names to delete
    """
    print("\n🧹 Cleaning up resources...")
    
    # Undeploy and delete models
    if model_ids:
        for model_id in model_ids:
            try:
                print(f"   Undeploying model: {model_id}")
                client.transport.perform_request('POST', f'/_plugins/_ml/models/{model_id}/_undeploy')
                time.sleep(2)
                print(f"   Deleting model: {model_id}")
                client.transport.perform_request('DELETE', f'/_plugins/_ml/models/{model_id}')
            except Exception as e:
                print(f"   ⚠ Error cleaning model {model_id}: {e}")
    
    # Delete agents
    if agent_ids:
        for agent_id in agent_ids:
            try:
                print(f"   Deleting agent: {agent_id}")
                client.transport.perform_request('DELETE', f'/_plugins/_ml/agents/{agent_id}')
            except Exception as e:
                print(f"   ⚠ Error deleting agent {agent_id}: {e}")
    
    # Delete indexes
    if index_names:
        for index_name in index_names:
            try:
                print(f"   Deleting index: {index_name}")
                client.indices.delete(index=index_name)
            except Exception as e:
                print(f"   ⚠ Error deleting index {index_name}: {e}")
    
    print("   ✓ Cleanup complete")
