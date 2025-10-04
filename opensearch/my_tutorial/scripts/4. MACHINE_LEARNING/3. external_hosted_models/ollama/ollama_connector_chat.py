# ================================================================================
# IMPORTS
# ================================================================================
import json
import os
import time
import warnings
import requests
import ipaddress
from dotenv import load_dotenv
from opensearchpy import OpenSearch

# ================================================================================
# CONFIGURATION AND SETUP
# ================================================================================

# Suppress warnings for cleaner output
warnings.filterwarnings("ignore", message="Unverified HTTPS request")
warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", message="TracerWarning: torch.tensor")
warnings.filterwarnings("ignore", message="using SSL with verify_certs=False is insecure.")

# Load environment variables from .env file
load_dotenv("../../../.env")

# Default Ollama URL can be overridden by setting OLLAMA_IP_URL env var.
# For example: export OLLAMA_IP_URL="http://localhost:11434"

# OpenSearch cluster configuration
HOST = 'localhost'
OLLAMA_IP_URL = '192.168.0.151:11435'  # Change to your Ollama host if needed. See README.md for more details.
OLLAMA_MODEL = "smollm2:135m" # neural-chat:latest if you have more memory on ollama_ip_url host
PORT = 9200
CLUSTER_URL = {'host': HOST, 'port': PORT}
DEFAULT_USERNAME = 'admin'
DEFAULT_PASSWORD = 'Developer@123'

# ================================================================================
# HELPER FUNCTIONS
# ================================================================================

def get_os_client(cluster_url=CLUSTER_URL, username=DEFAULT_USERNAME, password=DEFAULT_PASSWORD):
    """
    Create and return an OpenSearch client with SSL configuration.
    
    Args:
        cluster_url (dict): Dictionary containing host and port information
        username (str): OpenSearch username for authentication
        password (str): OpenSearch password for authentication
        
    Returns:
        OpenSearch: Configured OpenSearch client instance
    """
    client = OpenSearch(
        hosts=[cluster_url],
        http_auth=(username, password),
        verify_certs=False,
        ssl_assert_hostname=False,
        ssl_show_warn=False,
        use_ssl=True,
        max_retries=10,
        retry_on_timeout=True,
        timeout=300  # Increased timeout to 300 seconds
    )

    return client

# ================================================================================
# MAIN EXECUTION WORKFLOW
# ================================================================================

def main():
    """
    Main function to demonstrate Ollama connector integration with OpenSearch.
    
    This function performs the following steps:
    1. Initialize OpenSearch client and configure cluster settings
    2. List available Ollama models and download the specified model
    3. Create model group for organizing ML models
    4. Create Ollama connector for API communication
    5. Register and deploy the chat model
    6. Test the model with sample data
    7. Clean up resources
    """
    
    print("=== Ollama Embedding Model Integration with OpenSearch ===\n")
    
    # ============================================================================
    # STEP 1: INITIALIZE CLIENT AND CONFIGURE CLUSTER
    # ============================================================================
    print("Step 1: Initializing OpenSearch Client and Configuring Cluster...")
    client = get_os_client()
    
    # Configure cluster settings to accept Ollama as trusted connector endpoint
    cluster_settings = {
        "persistent": {
            "plugins.ml_commons.trusted_connector_endpoints_regex": [".*"],
            "plugins.ml_commons.only_run_on_ml_node": "false",
            "plugins.ml_commons.memory_feature_enabled": "true",
            "plugins.ml_commons.connector.private_ip_enabled": "true"
        }
    }
    client.cluster.put_settings(body=cluster_settings)
    print("✓ Cluster settings configured successfully\n")
    
    # ============================================================================
    # STEP 2: LIST AVAILABLE MODELS AND DOWNLOAD SPECIFIED MODEL
    # ============================================================================
    print("Step 2: Listing available Ollama models from endpoint...")
    try:
        resp = requests.get(f"http://{OLLAMA_IP_URL}/api/tags")
        resp.raise_for_status()
        models = resp.json().get('models', [])
        if not models:
            print("No models returned from Ollama endpoint.")
            return
        print("Available Ollama models:")
        for i, m in enumerate(models, start=1):
            print(f"  {i}. {m.get('name')}")
    except Exception as e:
        print(f"Could not list models from {OLLAMA_IP_URL}: {e}")
        return
    
    # Download the model
    try:
        print(f"Downloading model: {OLLAMA_MODEL}\n")
        payload = {
            "name": OLLAMA_MODEL,
            "stream": True # Set to True to stream the pull progress
            }
        headers = {"Content-Type": "application/json"}
        # Send the POST request to pull the model
        response = requests.post(f"http://{OLLAMA_IP_URL}/api/pull", headers=headers, data=json.dumps(payload), stream=True)
        response.raise_for_status() # Raise an exception for bad status codes

        print(f"Attempting to pull model: {OLLAMA_MODEL}")

        # Process the streamed response
        for chunk in response.iter_content(chunk_size=None):
            if chunk:
                try:
                    # Decode and print each chunk of the response
                    data = json.loads(chunk.decode('utf-8'))
                    if "status" in data:
                        print(f"Status: {data['status']}")
                    if "total" in data and "completed" in data:
                        progress = (data["completed"] / data["total"]) * 100
                        print(f"Download Progress: {progress:.2f}%")
                except json.JSONDecodeError:
                    print(f"Received non-JSON chunk: {chunk.decode('utf-8')}")

        print(f"Model '{OLLAMA_MODEL}' pull complete.")

    except requests.exceptions.RequestException as e:
        print(f"Error pulling model: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Response content: {e.response.text}")

    # ============================================================================
    # STEP 3: CREATE MODEL GROUP
    # ============================================================================
    print("Step 3: Initializing OpenSearch Client and Creating Model Group...")
    client = get_os_client()
    model_group_name = f"ollama_embedding_group_{int(time.time())}"
    model_group_body = {"name": model_group_name, "description": "Model group for Ollama chat"}
    model_group_response = client.transport.perform_request('POST', '/_plugins/_ml/model_groups/_register', body=model_group_body)
    model_group_id = model_group_response['model_group_id']
    print(f"✓ Created model group '{model_group_name}' with ID: {model_group_id}\n")

    # ============================================================================
    # STEP 4: CREATE OLLAMA CONNECTOR
    # ============================================================================
    print("Step 4: Creating Ollama connector...")
    # Use the proper Ollama API format with HTTP protocol
    connector_body = {
        "name": "ollama_connector",
        "description": "Connector for Ollama API",
        "version": 1,
        "protocol": "http",
        "parameters": {
            "endpoint": OLLAMA_IP_URL,
            "model": OLLAMA_MODEL
        },
        "credential": {
            "dummy_key": "dummy"
        },
        "actions": [
            {
                "action_type": "predict",
                "method": "POST",
                "url": "http://${parameters.endpoint}/api/generate",
                "headers": {
                    "Content-Type": "application/json"
                },
                "request_body": "{ \"model\": \"${parameters.model}\", \"prompt\": \"${parameters.prompt}\", \"stream\": false }"
            }
        ]
    }
    connector_response = client.transport.perform_request('POST', '/_plugins/_ml/connectors/_create', body=connector_body)
    connector_id = connector_response['connector_id']
    print(f"✓ Created Ollama connector with ID: {connector_id}\n")

    # ============================================================================
    # STEP 5: REGISTER AND DEPLOY MODEL
    # ============================================================================
    print("Step 5: Registering and Deploying Model...")
    model_body = {
        "name": "ollama_chat_model",
        "function_name": "remote",
        "model_group_id": model_group_id,
        "description": f"Ollama {OLLAMA_MODEL} chat model",
        "connector_id": connector_id,
        "model_format": "TORCH_SCRIPT"
    }
    model_response = client.transport.perform_request('POST', '/_plugins/_ml/models/_register', body=model_body)
    model_id = model_response['model_id']
    print(f"✓ Registered model with ID: {model_id}")

    deploy_body = {"deployment_plan": [{"model_id": model_id, "workers": 1}]}
    try:
        client.transport.perform_request('POST', f'/_plugins/_ml/models/{model_id}/_deploy', body=deploy_body)
        print("✓ Model deployment initiated")
    except Exception as e:
        print(f"⚠ Error deploying model: {e}")
        return

    print("⏳ Waiting for model deployment to complete...")
    while True:
        status_response = client.transport.perform_request('GET', f'/_plugins/_ml/models/{model_id}')
        current_status = status_response['model_state']
        print(f"   Current status: {current_status}")
        if current_status == 'DEPLOYED':
            print("✓ Model deployed successfully!\n")
            break
        elif current_status == 'FAILED':
            print("✗ Model deployment failed!")
            return
        time.sleep(5)

    # ============================================================================
    # STEP 6: TEST MODEL WITH SAMPLE DATA
    # ============================================================================
    print("Step 6: Testing Model with Sample Data...")
    predict_body = {"parameters": {
        "prompt": "Why is the sky blue? Please explain in a simple way."
    }}
    
    try:
        predict_response = client.transport.perform_request('POST', f'/_plugins/_ml/models/{model_id}/_predict', body=predict_body)
        print("✓ Model prediction successful!")
        print(json.dumps(predict_response, indent=2))
    except Exception as e:
        print(f"⚠ Error during prediction: {e}\n")

    # ============================================================================
    # STEP 7: CLEANUP RESOURCES
    # ============================================================================
    print("Step 7: Cleaning Up Resources...")
    cleanup_resources(client, model_id, connector_id, model_group_id)


def cleanup_resources(client, model_id, connector_id, model_group_id):
    """
    Clean up all created resources in the correct order.
    
    Args:
        client: OpenSearch client instance
        model_id (str): ID of the model to clean up
        connector_id (str): ID of the connector to clean up
        model_group_id (str): ID of the model group to clean up
    """
    # Undeploy the model
    try:
        client.transport.perform_request('POST', f'/_plugins/_ml/models/{model_id}/_undeploy')
        print(f"✓ Undeployed model with ID: {model_id}")
    except Exception as e:
        print(f"⚠ Error undeploying model: {e}")

    # Delete the model
    try:
        client.transport.perform_request('DELETE', f'/_plugins/_ml/models/{model_id}')
        print(f"✓ Deleted model with ID: {model_id}")
    except Exception as e:
        print(f"⚠ Error deleting model: {e}")

    # Delete the connector
    try:
        client.transport.perform_request('DELETE', f'/_plugins/_ml/connectors/{connector_id}')
        print(f"✓ Deleted connector with ID: {connector_id}")
    except Exception as e:
        print(f"⚠ Error deleting connector: {e}")

    # Delete the model group
    try:
        client.transport.perform_request('DELETE', f'/_plugins/_ml/model_groups/{model_group_id}')
        print(f"✓ Deleted model group with ID: {model_group_id}")
    except Exception as e:
        print(f"⚠ Error deleting model group: {e}")
    
    print("✓ Cleanup completed!\n")


if __name__ == "__main__":
    # Run main
    main()