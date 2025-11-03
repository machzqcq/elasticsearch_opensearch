"""
RAG Conversational Flow Agent with Memory

This script demonstrates a complete RAG (Retrieval-Augmented Generation) 
conversational agent implementation with memory capabilities using OpenSearch
and OpenAI. The agent can maintain context across conversations and provide
data-driven responses based on vector similarity search.
"""

from opensearchpy import OpenSearch, RequestsHttpConnection, helpers
import time
import os
from dotenv import load_dotenv
import sys

sys.path.append('../../')
from helpers import restore_interns_all_snapshot

# Load environment variables from .env file
load_dotenv("../../.env")

# Retrieve the OpenAI API key from environment variables
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

HOST = '192.168.1.192'

# Initialize the OpenSearch client
os_client = OpenSearch(
    hosts=[{'host': HOST, 'port': 9200}],
    http_auth=('admin', 'Developer@123'),  # Replace with your credentials
    use_ssl=True,
    verify_certs=False,
    connection_class=RequestsHttpConnection
)


def setup_cluster_settings():
    """Configure cluster settings for ML operations."""
    os_client.cluster.put_settings(body={
        "persistent": {
            "plugins.ml_commons.only_run_on_ml_node": "false",
            "plugins.ml_commons.native_memory_threshold": 100,
            "plugins.ml_commons.memory_feature_enabled": "true"
        }
    })


def register_embedding_model():
    """Register and deploy the sentence transformer embedding model."""
    register_response = os_client.transport.perform_request(
        'POST', 
        '/_plugins/_ml/models/_register?deploy=true', 
        body={
            "name": "huggingface/sentence-transformers/all-MiniLM-L12-v2",
            "version": "1.0.1",
            "model_format": "TORCH_SCRIPT"
        }
    )
    
    time.sleep(3)
    register_task_id = register_response['task_id']
    
    # Monitor task status
    while True:
        task_status = os_client.transport.perform_request(
            'GET', 
            f'/_plugins/_ml/tasks/{register_task_id}'
        )
        if task_status['state'] == 'COMPLETED':
            embedding_model_id = task_status['model_id']
            break
        time.sleep(5)
    
    print(f"Embedding Model ID: {embedding_model_id}")
    return embedding_model_id


def create_ingest_pipeline(embedding_model_id):
    """Create ingest pipeline for text embedding."""
    ingest_pipeline_response = os_client.ingest.put_pipeline(
        id='test-pipeline-local-model', 
        body={
            "description": "text embedding pipeline",
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
    )
    print(f"Ingest pipeline created: {ingest_pipeline_response}")


def create_vector_index():
    """Create index with vector embeddings configuration."""
    os_client.indices.create(index='my_test_data', body={
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
                        "space_type": "l2",
                        "engine": "lucene"
                    }
                }
            }
        },
        "settings": {
            "index": {
                "default_pipeline": "test-pipeline-local-model",
                "knn": "true"
            }
        }
    })


def load_sample_data():
    """Load sample population data into the vector index."""
    sample_docs = [
        {"_index": "my_test_data", "_id": "1", "_source": {"text": "Chart and table of population level and growth rate for the Ogden-Layton metro area from 1950 to 2023. United Nations population projections are also included through the year 2035.\nThe current metro area population of Ogden-Layton in 2023 is 750,000, a 1.63% increase from 2022.\nThe metro area population of Ogden-Layton in 2022 was 738,000, a 1.79% increase from 2021.\nThe metro area population of Ogden-Layton in 2021 was 725,000, a 1.97% increase from 2020.\nThe metro area population of Ogden-Layton in 2020 was 711,000, a 2.16% increase from 2019."}},
        {"_index": "my_test_data", "_id": "2", "_source": {"text": "Chart and table of population level and growth rate for the New York City metro area from 1950 to 2023. United Nations population projections are also included through the year 2035.\nThe current metro area population of New York City in 2023 is 18,937,000, a 0.37% increase from 2022.\nThe metro area population of New York City in 2022 was 18,867,000, a 0.23% increase from 2021.\nThe metro area population of New York City in 2021 was 18,823,000, a 0.1% increase from 2020.\nThe metro area population of New York City in 2020 was 18,804,000, a 0.01% decline from 2019."}},
        {"_index": "my_test_data", "_id": "3", "_source": {"text": "Chart and table of population level and growth rate for the Chicago metro area from 1950 to 2023. United Nations population projections are also included through the year 2035.\nThe current metro area population of Chicago in 2023 is 8,937,000, a 0.4% increase from 2022.\nThe metro area population of Chicago in 2022 was 8,901,000, a 0.27% increase from 2021.\nThe metro area population of Chicago in 2021 was 8,877,000, a 0.14% increase from 2020.\nThe metro area population of Chicago in 2020 was 8,865,000, a 0.03% increase from 2019."}},
        {"_index": "my_test_data", "_id": "4", "_source": {"text": "Chart and table of population level and growth rate for the Miami metro area from 1950 to 2023. United Nations population projections are also included through the year 2035.\nThe current metro area population of Miami in 2023 is 6,265,000, a 0.8% increase from 2022.\nThe metro area population of Miami in 2022 was 6,215,000, a 0.78% increase from 2021.\nThe metro area population of Miami in 2021 was 6,167,000, a 0.74% increase from 2020.\nThe metro area population of Miami in 2020 was 6,122,000, a 0.71% increase from 2019."}},
        {"_index": "my_test_data", "_id": "5", "_source": {"text": "Chart and table of population level and growth rate for the Austin metro area from 1950 to 2023. United Nations population projections are also included through the year 2035.\nThe current metro area population of Austin in 2023 is 2,228,000, a 2.39% increase from 2022.\nThe metro area population of Austin in 2022 was 2,176,000, a 2.79% increase from 2021.\nThe metro area population of Austin in 2021 was 2,117,000, a 3.12% increase from 2020.\nThe metro area population of Austin in 2020 was 2,053,000, a 3.43% increase from 2019."}},
        {"_index": "my_test_data", "_id": "6", "_source": {"text": "Chart and table of population level and growth rate for the Seattle metro area from 1950 to 2023. United Nations population projections are also included through the year 2035.\nThe current metro area population of Seattle in 2023 is 3,519,000, a 0.86% increase from 2022.\nThe metro area population of Seattle in 2022 was 3,489,000, a 0.81% increase from 2021.\nThe metro area population of Seattle in 2021 was 3,461,000, a 0.82% increase from 2020.\nThe metro area population of Seattle in 2020 was 3,433,000, a 0.79% increase from 2019."}}
    ]
    
    helpers.bulk(os_client, actions=sample_docs)
    print("Sample data loaded successfully")


def setup_openai_connector():
    """Set up OpenAI connector and model."""
    # Register model group
    model_group_name = f"openai_model_group1_{int(time.time())}"
    response_model_group = os_client.transport.perform_request(
        'POST', 
        '/_plugins/_ml/model_groups/_register', 
        body={
            "name": model_group_name,
            "description": "A model group for open ai models"
        }
    )
    
    model_group_id = response_model_group['model_group_id']
    
    # Create connector
    connector_response = os_client.transport.perform_request(
        'POST', 
        '/_plugins/_ml/connectors/_create', 
        body={
            "name": "OpenAI Chat Connector",
            "description": "The connector to public OpenAI model service for GPT 3.5",
            "version": 1,
            "protocol": "http",
            "parameters": {
                "endpoint": "api.openai.com",
                "model": "gpt-3.5-turbo"
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
    )
    
    connector_id = connector_response['connector_id']
    
    # Register OpenAI model
    register_openai_model = os_client.transport.perform_request(
        'POST', 
        '/_plugins/_ml/models/_register?deploy=true', 
        body={
            "name": "openAI-gpt-3.5-turbo",
            "function_name": "remote",
            "model_group_id": model_group_id,
            "description": "test model",
            "connector_id": connector_id
        }
    )
    
    register_openai_task_id = register_openai_model['task_id']
    
    # Monitor task status
    while True:
        task_status = os_client.transport.perform_request(
            'GET', 
            f'/_plugins/_ml/tasks/{register_openai_task_id}'
        )
        if task_status['state'] == 'COMPLETED':
            openai_model_id = task_status['model_id']
            break
        time.sleep(5)
    
    print(f"OpenAI model ID: {openai_model_id}")
    return openai_model_id


def test_openai_model(openai_model_id):
    """Test the OpenAI model with a sample prediction."""
    sample_predict_response = os_client.transport.perform_request(
        'POST', 
        f'/_plugins/_ml/models/{openai_model_id}/_predict', 
        body={
            "parameters": {
                "messages": [
                    {
                        "role": "system",
                        "content": "You are a helpful assistant."
                    },
                    {
                        "role": "user",
                        "content": "Hello!"
                    }
                ]
            }
        }
    )
    print("OpenAI model test:")
    print(sample_predict_response)


def create_rag_agent(embedding_model_id, openai_model_id):
    """Create the RAG conversational agent with memory."""
    agent_registration_response = os_client.transport.perform_request(
        'POST', 
        '/_plugins/_ml/agents/_register', 
        body={
            "name": "population data analysis agent",
            "type": "conversational_flow",
            "description": "This is a demo agent for population data analysis",
            "app_type": "rag",
            "memory": {
                "type": "conversation_index"
            },
            "tools": [
                {
                    "type": "VectorDBTool",
                    "parameters": {
                        "model_id": embedding_model_id,
                        "index": "my_test_data",
                        "embedding_field": "embedding",
                        "source_field": [
                            "text"
                        ],
                        "input": "${parameters.question}"
                    }
                },
                {
                    "type": "MLModelTool",
                    "description": "A general tool to answer any question",
                    "parameters": {
                        "model_id": openai_model_id,
                        "messages": [
                            {
                                "role": "system",
                                "content": "You are a professional data analyst. You will always answer a question based on the given context first. If the answer is not directly shown in the context, you will analyze the data and find the answer. If you don't know the answer, just say you don't know."
                            },
                            {
                                "role": "user",
                                "content": "Context:\n${parameters.VectorDBTool.output}\n\nQuestion:${parameters.question}\n\n"
                            }
                        ]
                    }
                }
            ]
        }
    )
    
    print("Agent registration:")
    print(agent_registration_response)
    return agent_registration_response['agent_id']


def test_conversation(agent_id):
    """Test conversational capabilities with memory."""
    # First question
    question1_response = os_client.transport.perform_request(
        'POST', 
        f'/_plugins/_ml/agents/{agent_id}/_execute', 
        body={
            "parameters": {
                "question": "what's the population increase of Seattle from 2021 to 2023?"
            }
        }
    )
    
    print("First question response:")
    print(question1_response)
    
    # Extract memory details
    memory_id = question1_response['inference_results'][0]['output'][0]['result']
    parent_message_id = question1_response['inference_results'][0]['output'][1]['result']
    
    # Continue conversation with memory
    continue_conversation_response = os_client.transport.perform_request(
        'POST', 
        f'/_plugins/_ml/agents/{agent_id}/_execute', 
        body={
            "parameters": {
                "question": "then compare with Seattle population of 2023"
            },
            "memory_id": memory_id
        }
    )
    
    print("Continued conversation response:")
    print(continue_conversation_response)
    
    return memory_id, parent_message_id


def explore_memory(memory_id, parent_message_id):
    """Explore the conversation memory and traces."""
    # Get memory details
    memory_details_response = os_client.transport.perform_request(
        'GET', 
        f'/_plugins/_ml/memory/{memory_id}'
    )
    print("Memory details:")
    print(memory_details_response)
    
    # Get all messages
    all_messages_response = os_client.transport.perform_request(
        'GET', 
        f'/_plugins/_ml/memory/{memory_id}/messages'
    )
    print("All messages:")
    print(all_messages_response)
    
    # Get message details
    message_details_response = os_client.transport.perform_request(
        'GET', 
        f'/_plugins/_ml/memory/message/{parent_message_id}'
    )
    print("Message details:")
    print(message_details_response)
    
    # Get message traces
    message_traces_response = os_client.transport.perform_request(
        'GET', 
        f'/_plugins/_ml/memory/message/{parent_message_id}/traces'
    )
    print("Message traces:")
    print(message_traces_response)


def main():
    """Main execution flow for RAG conversational agent."""
    print("Setting up RAG Conversational Agent with Memory...")
    
    # Step 1: Configure cluster settings
    setup_cluster_settings()
    
    # Step 2: Register embedding model
    embedding_model_id = register_embedding_model()
    
    # Step 3: Create ingest pipeline
    create_ingest_pipeline(embedding_model_id)
    
    # Step 4: Create vector index
    create_vector_index()
    
    # Step 5: Load sample data
    load_sample_data()
    
    # Step 6: Setup OpenAI connector and model
    openai_model_id = setup_openai_connector()
    
    # Step 7: Test OpenAI model
    test_openai_model(openai_model_id)
    
    # Step 8: Create RAG agent
    agent_id = create_rag_agent(embedding_model_id, openai_model_id)
    
    # Step 9: Test conversation
    memory_id, parent_message_id = test_conversation(agent_id)
    
    # Step 10: Explore memory
    explore_memory(memory_id, parent_message_id)
    
    print("RAG Conversational Agent demo completed!")


if __name__ == "__main__":
    main()
