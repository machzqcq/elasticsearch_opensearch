"""
Reranking Cross-Encoder MS-MARCO Model Demo

This script demonstrates how to register, deploy, predict, undeploy and delete 
a reranking model using OpenSearch Python client without MLCommons client.

The model calculates the similarity score of query_text and each document in 
text_docs and returns a list of scores for each document in the order they 
were provided in text_docs.
"""

from opensearchpy import OpenSearch, RequestsHttpConnection
import time
import sys

sys.path.append('../../')
from helpers import restore_interns_all_snapshot

HOST = '192.168.1.192'  # OpenSearch host

# Initialize the OpenSearch client
client = OpenSearch(
    hosts=[{'host': HOST, 'port': 9200}],
    http_auth=('admin', 'Developer@123'),  # Replace with your credentials
    use_ssl=True,
    verify_certs=False,
    connection_class=RequestsHttpConnection
)


def update_cluster_settings():
    """Update cluster settings to allow model registration."""
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


def create_model_group():
    """Create a model group for organizing models."""
    model_group_name = f"local_model_group_{int(time.time())}"
    model_group_response = client.transport.perform_request(
        method='POST',
        url='/_plugins/_ml/model_groups/_register',
        body={
            "name": model_group_name,
            "description": "A model group for local models"
        }
    )
    
    model_group_id = model_group_response['model_group_id']
    print(f"Model group ID: {model_group_id}")
    return model_group_id


def register_model(model_group_id):
    """Register the cross-encoder reranking model."""
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
    
    register_task_id = register_response['task_id']
    
    # Wait for registration to complete
    while True:
        task_status = client.transport.perform_request(
                method='GET',
                url=f'/_plugins/_ml/tasks/{register_task_id}'
        )
        print(task_status)
        if task_status['state'] == 'COMPLETED':
                model_id = task_status['model_id']
                break
        time.sleep(10)  # Wait for 10 seconds before checking again
    
    return model_id


def deploy_model(model_id):
    """Deploy the registered model."""
    deploy_response = client.transport.perform_request(
        method='POST',
        url=f'/_plugins/_ml/models/{model_id}/_deploy'
    )
    print(deploy_response)
    
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


def test_prediction(model_id):
    """Test the model with sample predictions."""
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


def setup_role_mapping():
    """Map the manage_snapshots role to the current user."""
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


def create_reranking_pipeline(model_id):
    """Create a reranking pipeline using the deployed model."""
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


def test_search_with_reranking():
    """Test search with reranking pipeline."""
    search_body = {
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
        "_source": False,
        "fields": ["JOB_TITLE", "COMPANY", "LOCATION"]
    }
    
    # Test with reranking pipeline
    search_response_pipeline = client.transport.perform_request(
        method='GET',
        url='/interns/_search?search_pipeline=reranking_pipeline',
        body=search_body
    )
    print("Search with reranking:")
    print(search_response_pipeline)
    
    # Test without reranking pipeline
    search_response_without_reranking = client.transport.perform_request(
        method='GET',
        url='/interns/_search',
        body=search_body
    )
    print("Search without reranking:")
    print(search_response_without_reranking)


def cleanup(model_id, model_group_id):
    """Clean up resources: pipeline, model, and model group."""
    # Delete the reranking pipeline
    client.transport.perform_request(
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


def main():
    """Main execution flow."""
    # Step 1: Update cluster settings
    update_cluster_settings()
    
    # Step 2: Create model group
    model_group_id = create_model_group()
    
    # Step 3: Register model
    model_id = register_model(model_group_id)
    
    # Step 4: Deploy model
    deploy_model(model_id)
    
    # Step 5: Test prediction
    test_prediction(model_id)
    
    # Step 6: Setup role mapping
    setup_role_mapping()
    
    # Step 7: Restore snapshot
    if restore_interns_all_snapshot(client):
        print("Snapshot restored successfully")
    else:
        print("Error restoring snapshot")
    
    # Step 8: Create reranking pipeline
    create_reranking_pipeline(model_id)
    
    # Step 9: Test search with and without reranking
    test_search_with_reranking()
    
    # Step 10: Cleanup
    cleanup(model_id, model_group_id)


if __name__ == "__main__":
    main()