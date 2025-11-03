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

# OpenSearch cluster configuration
HOST = 'localhost'
ANTHROPIC_MODEL = 'claude-3-opus-20240229'  # Change to your desired anthropic model if needed
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

def get_anthropic_models():
    """
    Fetch available models from the Anthropic.
    
    Returns:
        list: List of available anthropic models
    """
    from anthropic import Anthropic
    client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
    models = client.models.list()
    model_names = [model.id for model in models.data]
    return model_names

# ================================================================================
# MAIN EXECUTION WORKFLOW
# ================================================================================

def main():
    """
    Main function to demonstrate anthropic connector integration with OpenSearch.
    
    This function performs the following steps:
    1. Initialize OpenSearch client and configure cluster settings
    2. Create model group for organizing ML models
    3. Create anthropic connector for API communication
    4. Register and deploy the chat model
    5. Test the model with sample data
    6. Clean up resources
    """
    
    
    # ============================================================================
    # STEP 1: INITIALIZE CLIENT AND CONFIGURE CLUSTER
    # ============================================================================
    print("Step 1: Initializing OpenSearch Client and Configuring Cluster...")
    client = get_os_client()
    
    # Configure cluster settings to accept anthropic as trusted connector endpoint
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

    print(f"Listing all Anthropic models (for reference):")
    try:
        models = get_anthropic_models()
        print(models)
    except Exception as e:
        print(f"⚠ Error fetching Anthropic models: {e}")
    print("\n")
    
    # ============================================================================
    # STEP 2: CREATE MODEL GROUP
    # ============================================================================
    print("Step 2: Initializing OpenSearch Client and Creating Model Group...")
    client = get_os_client()
    model_group_name = f"anthropic_chat_group_{int(time.time())}"
    model_group_body = {"name": model_group_name, "description": "Model group for anthropic chat"}
    model_group_response = client.transport.perform_request('POST', '/_plugins/_ml/model_groups/_register', body=model_group_body)
    model_group_id = model_group_response['model_group_id']
    print(f"✓ Created model group '{model_group_name}' with ID: {model_group_id}\n")

    # ============================================================================
    # STEP 3: CREATE ANTHROPIC CONNECTOR
    # ============================================================================
    print("Step 3: Creating Anthropic connector...")
    # Use the proper Anthropic API format with HTTPS protocol
    connector_body = {
        "name": "Anthropic Chat",
        "description": "Connector for Anthropic Chat API",
        "version": "1",
        "protocol": "http",
        "parameters": {
            "endpoint": "api.anthropic.com",
            "model": ANTHROPIC_MODEL
        },
        "credential": {
            "anthropic_key": os.getenv("ANTHROPIC_API_KEY")
        },
        "actions": [
            {
                "action_type": "predict",
                "method": "POST",
                "url": "https://${parameters.endpoint}/v1/messages",
                "headers": {
                    "accept": "application/json",
                    "anthropic-version": "2023-06-01",
                    "content-type": "application/json",
                    "x-api-key": "${credential.anthropic_key}"
                },
                "request_body": "{ \"model\": \"${parameters.model}\", \"max_tokens\": 1000, \"system\": \"${parameters.system}\", \"messages\": ${parameters.messages} }"
            }
        ]
    }
    connector_response = client.transport.perform_request('POST', '/_plugins/_ml/connectors/_create', body=connector_body)
    connector_id = connector_response['connector_id']
    print(f"✓ Created Anthropic connector with ID: {connector_id}\n")

    # ============================================================================
    # STEP 4: REGISTER AND DEPLOY MODEL
    # ============================================================================
    print("Step 4: Registering and Deploying Model...")
    model_body = {
        "name": "anthropic_chat_model",
        "function_name": "remote",
        "model_group_id": model_group_id,
        "description": f"{ANTHROPIC_MODEL} chat model",
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
    # STEP 5: TEST MODEL WITH SAMPLE DATA
    # ============================================================================
    print("Step 5: Testing Model with Sample Data...")
    predict_body = {"parameters": {
        "system": "You are a helpful assistant.",
        "messages": [
          {"role": "user", "content": "Why is the sky blue?"}
        ]
    }}
    
    try:
        predict_response = client.transport.perform_request('POST', f'/_plugins/_ml/models/{model_id}/_predict', body=predict_body)
        print("✓ Model prediction successful!")
        print(json.dumps(predict_response, indent=2))
    except Exception as e:
        print(f"⚠ Error during prediction: {e}\n")

    # ============================================================================
    # STEP 6: CLEANUP RESOURCES
    # ============================================================================
    print("Step 6: Cleaning Up Resources...")
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