# ================================================================================
# OPENAI AGENT TOOLS - DEMONSTRATING AGENT WORKFLOW WITH OPENAI
# ================================================================================
# This script demonstrates how to integrate OpenAI GPT models with OpenSearch
# agent tools. It combines the setup from openai_connector_chat_completions_organized.py
# with the agent workflow from ollama_agent_tools.py
#
# Workflow:
# 1. Setup embedding model for semantic search (HuggingFace sentence transformers)
# 2. Create ingest pipeline and index with embeddings
# 3. Bulk index sample data
# 4. Setup OpenAI connector (GPT-4o-mini via OpenAI API)
# 5. Create and deploy OpenAI model
# 6. Register agent with VectorDBTool and MLModelTool
# 7. Execute agent to answer questions based on indexed data
# ================================================================================

import json
import os
import sys
import time
import warnings
from dotenv import load_dotenv
from opensearchpy import OpenSearch

# ================================================================================
# CONFIGURATION AND SETUP
# ================================================================================

# Suppress warnings for cleaner output
warnings.filterwarnings("ignore", message="Unverified HTTPS request")
warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", message="using SSL with verify_certs=False is insecure.")

# Load environment variables from .env file
load_dotenv("../../.env")

# Environment configuration
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

# OpenSearch cluster configuration
HOST = 'localhost'
PORT = 9200
CLUSTER_URL = {'host': HOST, 'port': PORT}
DEFAULT_USERNAME = 'admin'
DEFAULT_PASSWORD = 'Developer@123'
USE_AUTHENTICATION = True

# Model configuration
OPENAI_MODEL = "gpt-4o-mini"  # You can also use "gpt-3.5-turbo" or other OpenAI models

# ================================================================================
# HELPER FUNCTIONS
# ================================================================================

def get_os_client(cluster_url=CLUSTER_URL, username=DEFAULT_USERNAME, 
                   password=DEFAULT_PASSWORD, use_auth=USE_AUTHENTICATION):
    """
    Create and return an OpenSearch client with SSL configuration.
    
    Args:
        cluster_url (dict): Dictionary containing host and port information
        username (str): OpenSearch username for authentication
        password (str): OpenSearch password for authentication
        use_auth (bool): Whether to use authentication
        
    Returns:
        OpenSearch: Configured OpenSearch client instance
    """
    if use_auth:
        client = OpenSearch(
            hosts=[cluster_url],
            http_auth=(username, password),
            verify_certs=False,
            ssl_assert_hostname=False,
            ssl_show_warn=False,
            use_ssl=True,
            timeout=300
        )
    else:
        client = OpenSearch(
            hosts=[cluster_url],
            verify_certs=False,
            ssl_assert_hostname=False,
            ssl_show_warn=False,
            use_ssl=False,
            timeout=300
        )
    return client


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
        status_response = client.transport.perform_request('GET', f'/_plugins/_ml/models/{model_id}')
        current_status = status_response['model_state']
        print(f"   Model status: {current_status}")
        
        if current_status == 'DEPLOYED':
            print("   ✓ Model deployed successfully!")
            return True
        elif current_status == 'FAILED':
            print("   ✗ Model deployment failed!")
            return False
            
        if time.time() - start_time > timeout:
            print("   ✗ Model deployment timeout!")
            return False
            
        time.sleep(check_interval)

# ================================================================================
# MAIN EXECUTION WORKFLOW
# ================================================================================

def main():
    """
    Main function demonstrating OpenAI agent tools with OpenSearch.
    
    Steps:
    1. Initialize OpenSearch client and configure cluster
    2. Setup embedding model (HuggingFace sentence transformers)
    3. Create ingest pipeline and index
    4. Bulk index sample data
    5. Create OpenAI connector and deploy model
    6. Register and execute agent
    """
    
    print("\n" + "="*80)
    print("OPENAI AGENT TOOLS - OpenSearch Agent with GPT-4o-mini")
    print("="*80 + "\n")
    
    # ============================================================================
    # STEP 1: INITIALIZE CLIENT AND CONFIGURE CLUSTER
    # ============================================================================
    
    print("STEP 1: Initializing OpenSearch Client and Configuring Cluster...")
    client = get_os_client()
    print("   ✓ OpenSearch client initialized\n")
    
    # Configure cluster settings to accept OpenAI as trusted connector endpoint
    print("   Configuring cluster settings for OpenAI connector...")
    cluster_settings = {
        "persistent": {
            "plugins.ml_commons.trusted_connector_endpoints_regex": "^https://api\\.openai\\.com/.*$",
            "plugins.ml_commons.only_run_on_ml_node": "false",
            "plugins.ml_commons.memory_feature_enabled": "true"
        }
    }
    client.cluster.put_settings(body=cluster_settings)
    print("   ✓ Cluster settings configured successfully\n")
    
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
    print()
    
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
    
    # ============================================================================
    # STEP 4: BULK INDEX SAMPLE DATA
    # ============================================================================
    
    print("STEP 4: Bulk Indexing Sample Data...")
    
    bulk_body = [
        {"index": {"_index": index_name, "_id": "1"}},
        {"text": "Chart and table of population level and growth rate for the Ogden-Layton metro area from 1950 to 2023. United Nations population projections are also included through the year 2035.\nThe current metro area population of Ogden-Layton in 2023 is 750,000, a 1.63% increase from 2022.\nThe metro area population of Ogden-Layton in 2022 was 738,000, a 1.79% increase from 2021.\nThe metro area population of Ogden-Layton in 2021 was 725,000, a 1.97% increase from 2020.\nThe metro area population of Ogden-Layton in 2020 was 711,000, a 2.16% increase from 2019."},
        {"index": {"_index": index_name, "_id": "2"}},
        {"text": "Chart and table of population level and growth rate for the New York City metro area from 1950 to 2023. United Nations population projections are also included through the year 2035.\nThe current metro area population of New York City in 2023 is 18,937,000, a 0.37% increase from 2022.\nThe metro area population of New York City in 2022 was 18,867,000, a 0.23% increase from 2021.\nThe metro area population of New York City in 2021 was 18,823,000, a 0.1% increase from 2020.\nThe metro area population of New York City in 2020 was 18,804,000, a 0.01% decline from 2019."},
        {"index": {"_index": index_name, "_id": "3"}},
        {"text": "Chart and table of population level and growth rate for the Chicago metro area from 1950 to 2023. United Nations population projections are also included through the year 2035.\nThe current metro area population of Chicago in 2023 is 8,937,000, a 0.4% increase from 2022.\nThe metro area population of Chicago in 2022 was 8,901,000, a 0.27% increase from 2021.\nThe metro area population of Chicago in 2021 was 8,877,000, a 0.14% increase from 2020.\nThe metro area population of Chicago in 2020 was 8,865,000, a 0.03% increase from 2019."},
        {"index": {"_index": index_name, "_id": "4"}},
        {"text": "Chart and table of population level and growth rate for the Miami metro area from 1950 to 2023. United Nations population projections are also included through the year 2035.\nThe current metro area population of Miami in 2023 is 6,265,000, a 0.8% increase from 2022.\nThe metro area population of Miami in 2022 was 6,215,000, a 0.78% increase from 2021.\nThe metro area population of Miami in 2021 was 6,167,000, a 0.74% increase from 2020.\nThe metro area population of Miami in 2020 was 6,122,000, a 0.71% increase from 2019."},
        {"index": {"_index": index_name, "_id": "5"}},
        {"text": "Chart and table of population level and growth rate for the Austin metro area from 1950 to 2023. United Nations population projections are also included through the year 2035.\nThe current metro area population of Austin in 2023 is 2,228,000, a 2.39% increase from 2022.\nThe metro area population of Austin in 2022 was 2,176,000, a 2.79% increase from 2021.\nThe metro area population of Austin in 2021 was 2,117,000, a 3.12% increase from 2020.\nThe metro area population of Austin in 2020 was 2,053,000, a 3.43% increase from 2019."},
        {"index": {"_index": index_name, "_id": "6"}},
        {"text": "Chart and table of population level and growth rate for the Seattle metro area from 1950 to 2023. United Nations population projections are also included through the year 2035.\nThe current metro area population of Seattle in 2023 is 3,519,000, a 0.86% increase from 2022.\nThe metro area population of Seattle in 2022 was 3,489,000, a 0.81% increase from 2021.\nThe metro area population of Seattle in 2021 was 3,461,000, a 0.82% increase from 2020.\nThe metro area population of Seattle in 2020 was 3,433,000, a 0.79% increase from 2019."}
    ]
    
    client.bulk(body=bulk_body, index=index_name, pipeline=pipeline_id)
    print(f"   ✓ {len(bulk_body) // 2} documents indexed successfully\n")
    
    # ============================================================================
    # STEP 5: CREATE OPENAI CONNECTOR AND MODEL
    # ============================================================================
    
    print("STEP 5: Creating OpenAI Connector and Model...")
    
    # Create model group
    model_group_name = f"openai_agent_model_group_{int(time.time())}"
    print("   Creating model group...")
    llm_model_group_body = {
        "name": model_group_name,
        "description": "A model group for OpenAI agent models"
    }
    response = client.transport.perform_request(
        'POST', 
        '/_plugins/_ml/model_groups/_register', 
        body=llm_model_group_body
    )
    llm_model_group_id = response['model_group_id']
    print(f"   ✓ Model group created with ID: {llm_model_group_id}")
    
    # Create OpenAI connector
    print("   Creating OpenAI chat completions connector...")
    llm_connector_body = {
        "name": "OpenAI Chat Connector",
        "description": "The connector to public OpenAI model service for GPT models",
        "version": 1,
        "protocol": "http",
        "parameters": {
            "endpoint": "api.openai.com",
            "model": OPENAI_MODEL
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
                "request_body": "{\"model\": \"${parameters.model}\", \"messages\": ${parameters.messages}, \"temperature\": 0.7}"
            }
        ]
    }
    
    response = client.transport.perform_request(
        'POST', 
        '/_plugins/_ml/connectors/_create', 
        body=llm_connector_body
    )
    llm_connector_id = response['connector_id']
    print(f"   ✓ OpenAI connector created with ID: {llm_connector_id}")
    
    # Register the model
    print("   Registering OpenAI model...")
    llm_model_body = {
        "name": f"openai-{OPENAI_MODEL}",
        "function_name": "remote",
        "model_group_id": llm_model_group_id,
        "description": f"OpenAI {OPENAI_MODEL} model for agent",
        "connector_id": llm_connector_id
    }
    response = client.transport.perform_request(
        'POST', 
        '/_plugins/_ml/models/_register', 
        body=llm_model_body
    )
    llm_model_id = response['model_id']
    print(f"   ✓ Model registered with ID: {llm_model_id}")
    
    # Deploy the model
    print("   Deploying OpenAI model...")
    llm_deploy_body = {
        "deployment_plan": [
            {
                "model_id": llm_model_id,
                "workers": 1
            }
        ]
    }
    
    try:
        response = client.transport.perform_request(
            'POST', 
            f'/_plugins/_ml/models/{llm_model_id}/_deploy', 
            body=llm_deploy_body
        )
    except Exception as e:
        print(f"   ⚠ Error deploying model: {e}")
    
    print("   ⏳ Waiting for OpenAI model deployment...")
    wait_for_model_deployment(client, llm_model_id)
    print()
    
    # ============================================================================
    # STEP 6: REGISTER AGENT WITH TOOLS
    # ============================================================================
    
    print("STEP 6: Registering Agent with VectorDBTool and MLModelTool...")
    
    agent_register_body = {
        "name": "OpenAI_Agent_For_RAG",
        "type": "flow",
        "description": "An agent that uses OpenAI GPT model with semantic search",
        "tools": [
            {
                "type": "VectorDBTool",
                "parameters": {
                    "model_id": embedding_model_id,
                    "index": index_name,
                    "embedding_field": "embedding",
                    "source_field": [
                        "text"
                    ],
                    "input": "${parameters.question}"
                }
            },
            {
                "type": "MLModelTool",
                "description": "A tool using OpenAI GPT to answer questions based on context",
                "parameters": {
                    "model_id": llm_model_id,
                    "messages": "[{\"role\": \"system\", \"content\": \"You are a professional data analyst. You will always answer a question based on the given context first. If the answer is not directly shown in the context, you will analyze the data and find the answer. If you don't know the answer, just say you don't know.\"}, {\"role\": \"user\", \"content\": \"Context:\\n${parameters.VectorDBTool.output}\\n\\nQuestion: ${parameters.question}\"}]"
                }
            }
        ]
    }
    
    agent_response = client.transport.perform_request(
        'POST', 
        '/_plugins/_ml/agents/_register', 
        body=agent_register_body
    )
    agent_id = agent_response['agent_id']
    print(f"   ✓ Agent registered with ID: {agent_id}")
    
    # Inspect the agent
    print("   Inspecting agent configuration...")
    inspect_response = client.transport.perform_request(
        'GET', 
        f'/_plugins/_ml/agents/{agent_id}'
    )
    print(f"   ✓ Agent name: {inspect_response.get('name')}")
    print(f"   ✓ Agent type: {inspect_response.get('type')}")
    print(f"   ✓ Number of tools: {len(inspect_response.get('tools', []))}\n")
    
    # ============================================================================
    # STEP 7: EXECUTE AGENT
    # ============================================================================
    
    print("STEP 7: Executing Agent with Sample Questions...")
    
    # Test questions
    test_questions = [
        "What's the population increase of Seattle from 2021 to 2023?",
        "Which city had the highest growth rate in 2023?",
        "Compare the population of Austin and Miami in 2023"
    ]
    
    for i, question in enumerate(test_questions, 1):
        print(f"\n   Question {i}: {question}")
        print("   " + "-" * 70)
        
        execute_body = {
            "parameters": {
                "question": question
            }
        }
        
        try:
            execute_response = client.transport.perform_request(
                'POST', 
                f'/_plugins/_ml/agents/{agent_id}/_execute', 
                body=execute_body
            )
            
            # Response format: list of dicts with 'name' and 'result' keys
            answer = None
            
            if isinstance(execute_response, list) and len(execute_response) > 0:
                # Get the MLModelTool result (usually the last item)
                for item in execute_response:
                    if isinstance(item, dict) and item.get('name') == 'MLModelTool':
                        result_str = item.get('result', '')
                        if result_str:
                            try:
                                # Parse the JSON result string
                                result_json = json.loads(result_str)
                                # Extract answer from OpenAI response
                                choices = result_json.get('choices', [])
                                if choices and len(choices) > 0:
                                    message = choices[0].get('message', {})
                                    answer = message.get('content', '')
                                    break
                            except json.JSONDecodeError:
                                answer = result_str
                                break
            
            if answer and str(answer).strip():
                print(f"   Agent Response: {answer}")
            else:
                print(f"   Response (raw): {json.dumps(execute_response, indent=4)}")
                
        except Exception as e:
            print(f"   ⚠ Error executing agent: {e}")
    
    print("\n" + "="*80)
    print("✓ OpenAI Agent Tools Demo Completed Successfully!")
    print("="*80 + "\n")
    
    # Print summary
    print("Summary of Created Resources:")
    print(f"  • Embedding Model ID: {embedding_model_id}")
    print(f"  • OpenAI Model ID: {llm_model_id}")
    print(f"  • OpenAI Connector ID: {llm_connector_id}")
    print(f"  • Agent ID: {agent_id}")
    print(f"  • Index Name: {index_name}")
    print(f"  • Pipeline ID: {pipeline_id}\n")


# ================================================================================
# SCRIPT ENTRY POINT
# ================================================================================

if __name__ == "__main__":
    main()
