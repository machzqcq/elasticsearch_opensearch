# ================================================================================
# IMPORTS
# ================================================================================
import base64
import json
import os
import sys
import time
import warnings
from dotenv import load_dotenv
from opensearchpy import OpenSearch

# Add helpers to path
sys.path.append('../../')
from helpers import encode_image

# ================================================================================
# CONFIGURATION AND SETUP
# ================================================================================

# Suppress warnings for cleaner output
warnings.filterwarnings("ignore", message="Unverified HTTPS request")
warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", message="using SSL with verify_certs=False is insecure.")

# Load environment variables from .env file
load_dotenv("../../../.env")

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
IMAGE_PATH = "diapers.png"

# ================================================================================
# HELPER FUNCTIONS
# ================================================================================

def get_os_client(cluster_url=CLUSTER_URL, username=DEFAULT_USERNAME, password=DEFAULT_PASSWORD, use_auth=USE_AUTHENTICATION):
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

# ================================================================================
# MAIN EXECUTION WORKFLOW
# ================================================================================

def main():
    """
    Main function to demonstrate OpenAI Chat Completions integration with OpenSearch.
    
    This function performs the following steps:
    1. Initialize OpenSearch client and configure cluster settings
    2. Create model group for organizing ML models
    3. Create OpenAI connector for chat completions API
    4. Register and deploy the chat completion model
    5. Test the model with image analysis
    6. Clean up resources (optional - commented out for persistence)
    """
    
    print("=== OpenAI Chat Completions Model Integration with OpenSearch ===\n")
    
    # ============================================================================
    # STEP 1: INITIALIZE CLIENT AND CONFIGURE CLUSTER
    # ============================================================================
    
    print("Step 1: Initializing OpenSearch Client and Configuring Cluster...")
    client = get_os_client()
    
    # Configure cluster settings to accept OpenAI as trusted connector endpoint
    cluster_settings = {
        "persistent": {
            "plugins.ml_commons.trusted_connector_endpoints_regex": "^https://api\\.openai\\.com/.*$",
            "plugins.ml_commons.only_run_on_ml_node": "false",
            "plugins.ml_commons.memory_feature_enabled": "true"
        }
    }
    client.cluster.put_settings(body=cluster_settings)
    print("✓ Cluster settings configured successfully\n")
    
    # ============================================================================
    # STEP 2: CREATE MODEL GROUP
    # ============================================================================
    
    model_group_name = f"openai_model_group_{int(time.time())}"
    print("Step 2: Creating Model Group...")
    llm_model_group_body = {
        "name": model_group_name,
        "description": "A model group for OpenAI chat completion models"
    }
    
    response = client.transport.perform_request('POST', '/_plugins/_ml/model_groups/_register', body=llm_model_group_body)
    llm_model_group_id = response['model_group_id']
    print(f"✓ Created model group with ID: {llm_model_group_id}\n")
    
    # ============================================================================
    # STEP 3: CREATE OPENAI CHAT CONNECTOR
    # ============================================================================
    
    print("Step 3: Creating OpenAI Chat Completions Connector...")
    llm_connector_body = {
        "name": "OpenAI Chat Connector",
        "description": "The connector to public OpenAI model service for GPT-4o-mini",
        "version": 1,
        "protocol": "http",
        "parameters": {
            "endpoint": "api.openai.com",
            "model": "gpt-4o-mini"
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
    llm_connector_id = response['connector_id']
    print(f"✓ Created OpenAI chat connector with ID: {llm_connector_id}\n")
    
    # ============================================================================
    # STEP 4: REGISTER AND DEPLOY MODEL
    # ============================================================================
    
    print("Step 4: Registering and Deploying Chat Completion Model...")
    
    # Register the model
    llm_model_body = {
        "name": "openAI-gpt-4o-mini",
        "function_name": "remote",
        "model_group_id": llm_model_group_id,
        "description": "OpenAI GPT-4o-mini chat completion model",
        "connector_id": llm_connector_id
    }
    
    response = client.transport.perform_request('POST', '/_plugins/_ml/models/_register', body=llm_model_body)
    llm_model_id = response['model_id']
    print(f"✓ Registered model with ID: {llm_model_id}")
    
    # Deploy the model
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
        print("✓ Model deployment initiated")
    except Exception as e:
        print(f"⚠ Error deploying model: {e}")
        return
    
    # Wait for deployment to complete
    print("⏳ Waiting for model deployment to complete...")
    while True:
        status_response = client.transport.perform_request('GET', f'/_plugins/_ml/models/{llm_model_id}')
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
    # STEP 5: TEST MODEL WITH IMAGE ANALYSIS
    # ============================================================================
    
    print("Step 5: Testing Chat Completion Model with Image Analysis...")
    
    # Encode the image
    try:
        base64_image = encode_image(IMAGE_PATH)
        print(f"✓ Successfully encoded image: {IMAGE_PATH}")
    except Exception as e:
        print(f"⚠ Error encoding image: {e}")
        print("Continuing without image analysis...")
        base64_image = None
    
    # Prepare the prediction request
    if base64_image:
        test_llm_predict_body = {
            "parameters": {
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": "What's in this image?"
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64_image}"
                                }
                            }
                        ]
                    }
                ]
            }
        }
    else:
        # Fallback to text-only request
        test_llm_predict_body = {
            "parameters": {
                "messages": [
                    {
                        "role": "user",
                        "content": "Hello! Can you help me understand how OpenSearch ML works?"
                    }
                ]
            }
        }
    
    try:
        predict_response = client.transport.perform_request(
            'POST',
            f'/_plugins/_ml/models/{llm_model_id}/_predict',
            body=test_llm_predict_body
        )
        print("✓ Model prediction successful!")
        print("Response:")
        print(json.dumps(predict_response, indent=2))
        print()
    except Exception as e:
        print(f"⚠ Error during prediction: {e}\n")
    
    print("✓ Chat completion model integration completed successfully!")
    print("\nNote: Resources are left active for continued use.")
    print("To clean up resources, you would need to implement cleanup functions similar to the embedding script.\n")


# ================================================================================
# OPTIONAL CLEANUP FUNCTIONS
# ================================================================================

def cleanup_resources(client, model_id, connector_id, model_group_id):
    """
    Clean up all created resources in the correct order.
    
    Args:
        client: OpenSearch client instance
        model_id (str): ID of the model to clean up
        connector_id (str): ID of the connector to clean up
        model_group_id (str): ID of the model group to clean up
    
    Note: This function is provided for reference but not called in main()
    to keep resources active for continued use.
    """
    print("Cleaning up resources...")
    
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
    main()