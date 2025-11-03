from opensearchpy import OpenSearch, RequestsHttpConnection, helpers
import time, os
from dotenv import load_dotenv
import sys
import pandas as pd
import json

sys.path.append("../../")
from helpers import restore_interns_all_snapshot

# suppress warnings
import warnings

warnings.filterwarnings("ignore")

# 1. Load environment variables from .env file
load_dotenv("../../.env")

# 2. Retrieve the OpenAI API key from environment variables
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

HOST = '192.168.1.192'
# Initialize the OpenSearch client
os_client = OpenSearch(
    hosts=[{"host": HOST, "port": 9200}],
    http_auth=("admin", "Developer@123"),  # Replace with your credentials
    use_ssl=True,
    verify_certs=False,
    connection_class=RequestsHttpConnection,
)

# Cluster settings
os_client.cluster.put_settings(
    body={
        "persistent": {
            "plugins.ml_commons.only_run_on_ml_node": "false",
            "plugins.ml_commons.native_memory_threshold": 100,
            "plugins.ml_commons.memory_feature_enabled": "true",
        }
    }
)

# Register model
register_response = os_client.transport.perform_request(
    "POST",
    "/_plugins/_ml/models/_register",
    body={
        "name": "huggingface/sentence-transformers/all-MiniLM-L12-v2",
        "version": "1.0.1",
        "model_format": "TORCH_SCRIPT",
    },
)

# Wait for 3 seconds
time.sleep(3)

# Extract task_id from the response
register_task_id = register_response["task_id"]


# Monitor task status
while True:
    task_status = os_client.transport.perform_request(
        "GET", f"/_plugins/_ml/tasks/{register_task_id}"
    )
    if task_status["state"] == "COMPLETED":
        # Extract model_id from the response
        embedding_model_id = task_status["model_id"]
        break
    time.sleep(5)

print(f"Model ID: {embedding_model_id}")

# Deploy the model
deploy_response = os_client.transport.perform_request(
    method="POST", url=f"/_plugins/_ml/models/{embedding_model_id}/_deploy"
)
print(deploy_response)


# Extract deployment task_id from the response
deploy_task_id = deploy_response["task_id"]

# Wait until the deployment status becomes completed
while True:
    deployment_status = os_client.transport.perform_request(
        method="GET", url=f"/_plugins/_ml/tasks/{deploy_task_id}"
    )
    print(deployment_status)
    if deployment_status["state"] == "COMPLETED":
        break
    time.sleep(10)  # Wait for 10 seconds before checking again


# Delete pipeline if exists before creating
try:
    os_client.ingest.delete_pipeline(id="test-pipeline-local-model")
except Exception as e:
    pass  # Ignore if pipeline does not exist

# Create ingest pipeline
ingest_pipeline_response = os_client.ingest.put_pipeline(
    id="test-pipeline-local-model",
    body={
        "description": "text embedding pipeline",
        "processors": [
            {
                "text_embedding": {
                    "model_id": embedding_model_id,
                    "field_map": {"text": "embedding"},
                }
            }
        ],
    },
)

print(f"Ingest pipeline ID: {ingest_pipeline_response}")

# Delete index if exists before creating
try:
    os_client.indices.delete(index="my_test_data")
except Exception:
    pass  # Ignore if index does not exist

# Create index with mappings and settings
os_client.indices.create(
    index="my_test_data",
    body={
        "mappings": {
            "properties": {
                "text": {"type": "text"},
                "embedding": {
                    "type": "knn_vector",
                    "dimension": 384,
                    "method": {"name": "hnsw", "space_type": "l2", "engine": "lucene"},
                },
            }
        },
        "settings": {
            "index": {
                "default_pipeline": "test-pipeline-local-model",
                "knn": "true",
            }
        },
    },
)

# Bulk insert data
# opensearch helpers bulk insert data

helpers.bulk(
    os_client,
    actions=[
        {
            "_index": "my_test_data",
            "_id": "1",
            "_source": {
                "text": "Chart and table of population level and growth rate for the Ogden-Layton metro area from 1950 to 2023. United Nations population projections are also included through the year 2035.\nThe current metro area population of Ogden-Layton in 2023 is 750,000, a 1.63% increase from 2022.\nThe metro area population of Ogden-Layton in 2022 was 738,000, a 1.79% increase from 2021.\nThe metro area population of Ogden-Layton in 2021 was 725,000, a 1.97% increase from 2020.\nThe metro area population of Ogden-Layton in 2020 was 711,000, a 2.16% increase from 2019."
            },
        },
        {
            "_index": "my_test_data",
            "_id": "2",
            "_source": {
                "text": "Chart and table of population level and growth rate for the New York City metro area from 1950 to 2023. United Nations population projections are also included through the year 2035.\nThe current metro area population of New York City in 2023 is 18,937,000, a 0.37% increase from 2022.\nThe metro area population of New York City in 2022 was 18,867,000, a 0.23% increase from 2021.\nThe metro area population of New York City in 2021 was 18,823,000, a 0.1% increase from 2020.\nThe metro area population of New York City in 2020 was 18,804,000, a 0.01% decline from 2019."
            },
        },
        {
            "_index": "my_test_data",
            "_id": "3",
            "_source": {
                "text": "Chart and table of population level and growth rate for the Chicago metro area from 1950 to 2023. United Nations population projections are also included through the year 2035.\nThe current metro area population of Chicago in 2023 is 8,937,000, a 0.4% increase from 2022.\nThe metro area population of Chicago in 2022 was 8,901,000, a 0.27% increase from 2021.\nThe metro area population of Chicago in 2021 was 8,877,000, a 0.14% increase from 2020.\nThe metro area population of Chicago in 2020 was 8,865,000, a 0.03% increase from 2019."
            },
        },
        {
            "_index": "my_test_data",
            "_id": "4",
            "_source": {
                "text": "Chart and table of population level and growth rate for the Miami metro area from 1950 to 2023. United Nations population projections are also included through the year 2035.\nThe current metro area population of Miami in 2023 is 6,265,000, a 0.8% increase from 2022.\nThe metro area population of Miami in 2022 was 6,215,000, a 0.78% increase from 2021.\nThe metro area population of Miami in 2021 was 6,167,000, a 0.74% increase from 2020.\nThe metro area population of Miami in 2020 was 6,122,000, a 0.71% increase from 2019."
            },
        },
        {
            "_index": "my_test_data",
            "_id": "5",
            "_source": {
                "text": "Chart and table of population level and growth rate for the Austin metro area from 1950 to 2023. United Nations population projections are also included through the year 2035.\nThe current metro area population of Austin in 2023 is 2,228,000, a 2.39% increase from 2022.\nThe metro area population of Austin in 2022 was 2,176,000, a 2.79% increase from 2021.\nThe metro area population of Austin in 2021 was 2,117,000, a 3.12% increase from 2020.\nThe metro area population of Austin in 2020 was 2,053,000, a 3.43% increase from 2019."
            },
        },
        {
            "_index": "my_test_data",
            "_id": "6",
            "_source": {
                "text": "Chart and table of population level and growth rate for the Seattle metro area from 1950 to 2023. United Nations population projections are also included through the year 2035.\nThe current metro area population of Seattle in 2023 is 3,519,000, a 0.86% increase from 2022.\nThe metro area population of Seattle in 2022 was 3,489,000, a 0.81% increase from 2021.\nThe metro area population of Seattle in 2021 was 3,461,000, a 0.82% increase from 2020.\nThe metro area population of Seattle in 2020 was 3,433,000, a 0.79% increase from 2019."
            },
        },
    ],
)

model_group_name = f"openai_model_group1_{int(time.time())}"
response_model_group = os_client.transport.perform_request(
    "POST",
    "/_plugins/_ml/model_groups/_register",
    body={
        "name": model_group_name,
        "description": "A model group for open ai models",
    },
)

# Retrieve model group ID from the response
model_group_id = response_model_group["model_group_id"]

# Create connector
connector_response = os_client.transport.perform_request(
    "POST",
    "/_plugins/_ml/connectors/_create",
    body={
        "name": "OpenAI Chat Connector",
        "description": "The connector to public OpenAI model service for GPT 3.5",
        "version": 1,
        "protocol": "http",
        "parameters": {"endpoint": "api.openai.com", "model": "gpt-3.5-turbo"},
        "credential": {"openAI_key": OPENAI_API_KEY},
        "actions": [
            {
                "action_type": "predict",
                "method": "POST",
                "url": "https://${parameters.endpoint}/v1/chat/completions",
                "headers": {"Authorization": "Bearer ${credential.openAI_key}"},
                "request_body": '{ "model": "${parameters.model}", "messages": ${parameters.messages} }',
            }
        ],
    },
)

# Retrieve connector ID
connector_id = connector_response["connector_id"]

# Register OpenAI model
register_openai_model = os_client.transport.perform_request(
    "POST",
    "/_plugins/_ml/models/_register?deploy=true",
    body={
        "name": "openAI-gpt-3.5-turbo",
        "function_name": "remote",
        "model_group_id": model_group_id,
        "description": "test model",
        "connector_id": connector_id,
    },
)

# Retrieve task id
register_openai_task_id = register_openai_model["task_id"]

# Monitor task status
while True:
    task_status = os_client.transport.perform_request(
        "GET", f"/_plugins/_ml/tasks/{register_openai_task_id}"
    )
    if task_status["state"] == "COMPLETED":
        # Extract model_id from the response
        openai_model_id = task_status["model_id"]
        break
    time.sleep(5)

print(f"OpenAI model ID: {openai_model_id}")


# Predict using OpenAI model
sample_predict_response = os_client.transport.perform_request(
    "POST",
    f"/_plugins/_ml/models/{openai_model_id}/_predict",
    body={
        "parameters": {
            "messages": [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Hello!"},
            ]
        }
    },
)

print(sample_predict_response)

# Register agent with multiple knowledge bases aka. tools
agent_registration_response = os_client.transport.perform_request(
    "POST",
    "/_plugins/_ml/agents/_register",
    body={
        "name": "population data analysis agent",
        "type": "conversational_flow",
        "description": "This is a demo agent for population data analysis",
        "app_type": "rag",
        "memory": {"type": "conversation_index"},
        "tools": [
            {
                "type": "SearchIndexTool",
                "parameters": {
                    "input": '{"index": "${parameters.index}", "query": ${parameters.query} }'
                },
            },
            {
                "type": "MLModelTool",
                "description": "A general tool to answer any question",
                "parameters": {
                    "model_id": openai_model_id,
                    "messages": [
                        {
                            "role": "system",
                            "content": "You are a professional data analyst. You will always answer a question based on the given context first. If the answer is not directly shown in the context, you will analyze the data and find the answer. If you don't know the answer, just say you don't know.",
                        },
                        {
                            "role": "user",
                            "content": "Context:\n${parameters.SearchIndexTool.output:-}\n\nQuestion:${parameters.question}\n\n",
                        },
                    ],
                },
            },
        ],
    },
)

print(agent_registration_response)

# Retrieve agent ID
agent_id = agent_registration_response["agent_id"]

# Define common query for consistent comparison
SEARCH_QUERY = "what's the population increase of Seattle from 2021 to 2023?"

# Run BM25 query
bm25_response = os_client.transport.perform_request(
    "POST",
    f"/_plugins/_ml/agents/{agent_id}/_execute",
    body={
        "parameters": {
            "question": SEARCH_QUERY,
            "index": "my_test_data",
            "query": {
                "query": {"match": {"text": "${parameters.question}"}},
                "size": 2,
                "_source": "text",
            },
        }
    },
)

print(f"Bm25 response --> {bm25_response}")

# Run neural search
neural_response = os_client.transport.perform_request(
    "POST",
    f"/_plugins/_ml/agents/{agent_id}/_execute",
    body={
    "parameters": {
        "question": SEARCH_QUERY,
        "index": "my_test_data",
        "query": {
            "query": {
                "neural": {
                    "embedding": {
                        "query_text": "${parameters.question}",
                        "model_id": embedding_model_id,
                        "k": 10
                    }
                }
            },
            "size": 2,
            "_source": ["text"]
        }
    }
},
)

print(f"Neural response --> {neural_response}")

# Hybrid Query with RRF (Reciprocal Rank Fusion)

# RRF processor to combine BM25 and neural search results using correct OpenSearch syntax
hybrid_rrf_pipeline = os_client.transport.perform_request(
    "PUT",
    f"/_search/pipeline/rrf-search-pipeline",
    body={
        "description": "Post processor for hybrid RRF search",
        "phase_results_processors": [
            {
                "score-ranker-processor": {
                    "combination": {
                        "technique": "rrf",
                        "rank_constant": 40,
                        "parameters": {
                            "weights": [
                                0.7,  # Weight for BM25 query (first query)
                                0.3   # Weight for Neural query (second query)
                            ]
                        }
                    }
                }
            }
        ]
    }
)

print(f"Hybrid RRF pipeline --> {hybrid_rrf_pipeline}")

# Alternative RRF pipeline with equal weights and default rank_constant
hybrid_rrf_pipeline_equal = os_client.transport.perform_request(
    "PUT",
    f"/_search/pipeline/rrf-equal-search-pipeline",
    body={
        "description": "Post processor for hybrid RRF search with equal weights",
        "phase_results_processors": [
            {
                "score-ranker-processor": {
                    "combination": {
                        "technique": "rrf",
                        "rank_constant": 60  # Default value
                        # No weights parameter means equal weights (1.0, 1.0)
                    }
                }
            }
        ]
    }
)

print(f"Hybrid RRF Equal pipeline --> {hybrid_rrf_pipeline_equal}")

# Run hybrid query with RRF
hybrid_response = os_client.transport.perform_request(
    "GET",
    "/my_test_data/_search?search_pipeline=rrf-search-pipeline",
    body={
        "_source": {
            "exclude": [
                "embedding"
            ]
        },
        "size": 2,
        "query": {
            "hybrid": {
                "queries": [
                    {
                        "match": {
                            "text": {
                                "query": SEARCH_QUERY
                            }
                        }
                    },
                    {
                        "neural": {
                            "embedding": {
                                "query_text": SEARCH_QUERY,
                                "model_id": embedding_model_id,
                                "k": 10
                            }
                        }
                    }
                ]
            }
        }
    }
)

print(f"Hybrid response --> {hybrid_response}")

# Run hybrid query with RRF (Equal Weights)
hybrid_rrf_equal_response = os_client.transport.perform_request(
    "GET",
    "/my_test_data/_search?search_pipeline=rrf-equal-search-pipeline",
    body={
        "_source": {
            "exclude": [
                "embedding"
            ]
        },
        "size": 2,
        "query": {
            "hybrid": {
                "queries": [
                    {
                        "match": {
                            "text": {
                                "query": SEARCH_QUERY
                            }
                        }
                    },
                    {
                        "neural": {
                            "embedding": {
                                "query_text": SEARCH_QUERY,
                                "model_id": embedding_model_id,
                                "k": 10
                            }
                        }
                    }
                ]
            }
        }
    }
)

print(f"Hybrid RRF Equal response --> {hybrid_rrf_equal_response}")

# Direct BM25 Search (without agent)
direct_bm25_response = os_client.transport.perform_request(
    "GET",
    "/my_test_data/_search",
    body={
        "query": {
            "match": {
                "text": SEARCH_QUERY
            }
        },
        "size": 2,
        "_source": ["text"]
    }
)

print(f"Direct BM25 response --> {direct_bm25_response}")

# Direct Neural Search (without agent)
direct_neural_response = os_client.transport.perform_request(
    "GET",
    "/my_test_data/_search",
    body={
        "query": {
            "neural": {
                "embedding": {
                    "query_text": SEARCH_QUERY,
                    "model_id": embedding_model_id,
                    "k": 10
                }
            }
        },
        "size": 2,
        "_source": ["text"]
    }
)

print(f"Direct Neural response --> {direct_neural_response}")

# Expose only `question` parameter to the user query
agent_registration_response_dynamic = os_client.transport.perform_request(
    "POST",
    "/_plugins/_ml/agents/_register",
    body={
        "name": "population data analysis agent",
        "type": "conversational_flow",
        "description": "This is a demo agent for population data analysis",
        "app_type": "rag",
        "memory": {"type": "conversation_index"},
        "tools": [
            {
                "type": "SearchIndexTool",
                "parameters": {
                    "input": '{"index": "${parameters.index}", "query": ${parameters.query} }',
                    "query": {
                        "query": {"match": {"text": "${parameters.question}"}},
                        "size": 2,
                        "_source": "text",
                    },
                },
            },
            {
                "type": "MLModelTool",
                "description": "A general tool to answer any question",
                "parameters": {
                    "model_id": openai_model_id,
                    "messages": [
                        {
                            "role": "system",
                            "content": "You are a professional data analyst. You will always answer a question based on the given context first. If the answer is not directly shown in the context, you will analyze the data and find the answer. If you don't know the answer, just say you don't know.",
                        },
                        {
                            "role": "user",
                            "content": "Context:\n${parameters.SearchIndexTool.output:-}\n\nQuestion:${parameters.question}\n\n",
                        },
                    ],
                },
            },
        ],
    },
)

print(f"Agent registration response dynamic --> {agent_registration_response_dynamic}")
agent_id1 = agent_registration_response_dynamic["agent_id"]

neural_response_dynamic = os_client.transport.perform_request(
    "POST",
    f"/_plugins/_ml/agents/{agent_id1}/_execute",
    body={
    "parameters": {
        "question": SEARCH_QUERY,
        "index": "my_test_data",
        "query": {
            "query": {
                "neural": {
                    "embedding": {
                        "query_text": "${parameters.question}",
                        "model_id": embedding_model_id,
                        "k": 10
                    }
                }
            },
            "size": 2,
            "_source": ["text"]
        }
    }
},
)

print(f"Neural response dynamic --> {neural_response_dynamic}")


def extract_search_results(response, query_type):
    """Extract relevant information from search response."""
    try:
        if query_type == "agent":
            # For agent responses, extract from inference_results
            if 'inference_results' in response and len(response['inference_results']) > 0:
                outputs = response['inference_results'][0]['output']
                
                # Look for MLModelTool result which contains the actual response
                for output in outputs:
                    if output.get('name') == 'MLModelTool':
                        # Parse the JSON string in the result
                        ml_result = json.loads(output['result'])
                        if 'choices' in ml_result and len(ml_result['choices']) > 0:
                            content = ml_result['choices'][0]['message']['content']
                            # Clean up the content but don't truncate
                            content = content.replace('\\n', '\n').replace('\\u0027', "'").replace('\\u003d', '=')
                            return content
                
                # Fallback to first result if MLModelTool not found
                return f"Agent response: {outputs[0]['result']}"
        else:
            # For direct search responses
            if 'hits' in response and 'hits' in response['hits']:
                hits = response['hits']['hits']
                if hits:
                    # Get top result
                    top_hit = hits[0]
                    score = top_hit.get('_score', 'N/A')
                    source = top_hit.get('_source', {})
                    text = source.get('text', 'No text found')
                    # Return full text without truncation
                    return f"Score: {score}, Text: {text}"
            return "No results found"
    except Exception as e:
        return f"Error extracting results: {str(e)}"


def create_results_table():
    """Create a comparison table of different search approaches."""
    
    # Extract results from each search type
    bm25_agent_result = extract_search_results(bm25_response, "agent")
    neural_agent_result = extract_search_results(neural_response, "agent")
    hybrid_rrf_result = extract_search_results(hybrid_response, "direct")
    hybrid_rrf_equal_result = extract_search_results(hybrid_rrf_equal_response, "direct")
    direct_bm25_result = extract_search_results(direct_bm25_response, "direct")
    direct_neural_result = extract_search_results(direct_neural_response, "direct")
    agent_result = extract_search_results(neural_response_dynamic, "agent")
    
    # Create table data
    table_data = [
        ["BM25 Agent Search", bm25_agent_result],
        ["Neural Agent Search", neural_agent_result],
        ["Direct BM25 Search", direct_bm25_result],
        ["Direct Neural Search", direct_neural_result],
        ["Hybrid RRF Weighted (0.7/0.3)", hybrid_rrf_result],
        ["Hybrid RRF Equal Weights", hybrid_rrf_equal_result],
        ["Dynamic Agent Response", agent_result]
    ]
    
    # Print table
    print("\n" + "="*160)
    print("SEARCH RESULTS COMPARISON TABLE")
    print("="*160)
    print(f"Input Query: {SEARCH_QUERY}")
    print("-"*160)
    print(f"{'Search Type':<30} | {'Response/Result'}")
    print("-"*160)
    
    for search_type, result in table_data:
        print(f"{search_type:<30} | {result}")
    
    print("="*160)
    
    # Also create a pandas DataFrame for better formatting
    try:
        import pandas as pd
        df = pd.DataFrame(table_data, columns=['Search Type', 'Response/Result'])
        df['Input Query'] = SEARCH_QUERY
        df = df[['Input Query', 'Search Type', 'Response/Result']]  # Reorder columns
        
        print("\nPANDAS DATAFRAME VIEW:")
        print("-"*160)
        pd.set_option('display.max_columns', None)
        pd.set_option('display.max_colwidth', 120)
        pd.set_option('display.width', None)
        print(df.to_string(index=False))
        
        # Save to CSV
        df.to_csv('search_comparison_results.csv', index=False)
        print(f"\nResults saved to: search_comparison_results.csv")
        
    except ImportError:
        print("\nPandas not available for DataFrame view")
    
    # Print detailed comparison summary
    print("\n" + "="*160)
    print("SEARCH COMPARISON SUMMARY")
    print("="*160)
    print("• BM25 Agent Search: Uses agent framework with BM25 matching")
    print("• Neural Agent Search: Uses agent framework with semantic vector search")
    print("• Direct BM25 Search: Raw BM25 keyword matching without agent")
    print("• Direct Neural Search: Raw semantic vector search without agent")
    print("• Hybrid RRF Weighted (0.7/0.3): Combines BM25 + Neural using RRF with 70% BM25 / 30% Neural weighting")
    print("• Hybrid RRF Equal Weights: Combines BM25 + Neural using RRF with equal 50/50 weighting")
    print("• Dynamic Agent Response: Agent with dynamic indexing capabilities")
    print("")
    print("RRF CONFIGURATION DETAILS:")
    print("• Weighted RRF: rank_constant=40, weights=[0.7, 0.3] (favors BM25)")
    print("• Equal RRF: rank_constant=60, weights=[1.0, 1.0] (equal treatment)")
    print("="*160)


# Generate the comparison table
create_results_table()