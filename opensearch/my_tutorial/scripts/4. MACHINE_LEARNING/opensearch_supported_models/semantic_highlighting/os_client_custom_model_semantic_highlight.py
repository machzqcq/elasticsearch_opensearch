import requests
import torch
import opensearch_py_ml as oml
from opensearch_py_ml.ml_commons import MLCommonClient
from opensearchpy import OpenSearch
import zipfile
import os, time
import json
from transformers import AutoModelForQuestionAnswering, AutoProcessor, AutoTokenizer
import warnings

# ================================================================================
# CONFIGURATION AND SETUP
# ================================================================================

# Suppress warnings for cleaner output
warnings.filterwarnings("ignore", message="Unverified HTTPS request")
warnings.filterwarnings('ignore', category=DeprecationWarning)
warnings.filterwarnings('ignore', category=FutureWarning)
warnings.filterwarnings("ignore", message="TracerWarning: torch.tensor")
warnings.filterwarnings("ignore", message="using SSL with verify_certs=False is insecure.")

# OpenSearch cluster configuration
HOST = 'localhost'
CLUSTER_URL = {'host': HOST, 'port': 9200}

def get_os_client(cluster_url=CLUSTER_URL, username='admin', password='Developer@123'):
    """
    Get OpenSearch client with SSL configuration
    """
    client = OpenSearch(
        hosts=[cluster_url],
        http_auth=(username, password),
        verify_certs=False,
        ssl_assert_hostname=False,
        ssl_show_warn=False,
        use_ssl=True,
        timeout=300  # Increased timeout to 300 seconds for request timeout errors during registering models
    )
    return client

# ================================================================================
# STEP 1: INITIALIZE OPENSEARCH CLIENT AND CONFIGURE CLUSTER
# ================================================================================

print("=== Step 1: Initializing OpenSearch Client ===")
client = get_os_client()

# Configure cluster settings to allow local model registration
print("Configuring cluster settings for ML Commons...")
client.cluster.put_settings(body={
    "persistent": {
        "plugins": {
            "ml_commons": {
                "allow_registering_model_via_url": "true",
                "allow_registering_model_via_local_file": "true",
                "only_run_on_ml_node": "false",
                "model_access_control_enabled": "true",
                "native_memory_threshold": "99"
            }
        }
    }
})

# Initialize ML Commons client
ml_client = MLCommonClient(client)
print("✅ OpenSearch and ML Commons clients initialized")

# ================================================================================
# STEP 2: DOWNLOAD AND PREPARE THE SEMANTIC HIGHLIGHT MODEL
# ================================================================================

print("\n=== Step 2: Preparing Semantic Highlight Model ===")

# Create directory for saved models
os.makedirs("saved_models", exist_ok=True)


# ================================================================================
# STEP 5: DOWNLOAD SEMANTIC HIGHLIGHT ZIPPED MODEL
# ================================================================================

print("\n=== Step 5: Downloading Semantic Highlight Zipped Model ===")

DOWNLOAD_URL = "https://artifacts.opensearch.org/models/ml-models/amazon/sentence-highlighting/opensearch-semantic-highlighter-v1/1.0.0/torch_script/sentence-highlighting_opensearch-semantic-highlighter-v1-1.0.0-torch_script.zip"

# Download the zip file
response = requests.get(DOWNLOAD_URL)
with open("saved_models/sentence-highlighting_opensearch-semantic-highlighter-v1-1.0.0-torch_script.zip", "wb") as f:
    f.write(response.content)

print("✅ Semantic Highlight Zipped Model downloaded")


# ================================================================================
# STEP 6: CREATE ML COMMONS MODEL CONFIGURATION
# ================================================================================

# Create ML Commons model configuration
mlcommons_model_config = {
    'name': "opensearch-semantic-highlighter-v1",
    'version': '1.0.0',
    'model_format': 'TORCH_SCRIPT',
    "function_name": "QUESTION_ANSWERING",
    "description": "A semantic highlighter model that identifies relevant sentences in a document given a query.",
    'model_config': {
        'model_type': 'sentence_highlighting',
        'framework_type': 'huggingface_transformers'
    }
}

# Save ML Commons configuration
with open('saved_models/mlcommons_model_config.json', 'w') as f:
    json.dump(mlcommons_model_config, f)

print("✅ ML Commons configuration created")
print("Configuration:", json.dumps(mlcommons_model_config, indent=2))

# ================================================================================
# STEP 7: REGISTER AND DEPLOY TEXT_EMBEDDING MODEL IN OPENSEARCH
# ================================================================================

model_group_name = f"local_model_group_{int(time.time())}"
print(f"Registering model group: {model_group_name}")
# Register a model group
model_group_response = client.transport.perform_request(
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
register_response = client.transport.perform_request(
    method='POST',
    url='/_plugins/_ml/models/_register',
    body={
        "name": "huggingface/sentence-transformers/msmarco-distilbert-base-tas-b",
        "version": "1.0.2",
        "model_group_id": model_group_id,
        "model_format": "TORCH_SCRIPT",
        "function_name": "TEXT_EMBEDDING",
    }
)

# Extract task_id from the response
register_task_id = register_response['task_id']

# Get task status
while True:
    task_status = client.transport.perform_request(
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
deploy_response = client.transport.perform_request(
    method='POST',
    url=f'/_plugins/_ml/models/{model_id}/_deploy',
    timeout=50000  # Set timeout to 5 minutes
)
print(deploy_response)


# Extract deployment task_id from the response
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


# ================================================================================
# STEP 8: REGISTER AND DEPLOY SEMANTIC HIGHLIGHTING MODEL IN OPENSEARCH
# ================================================================================

print("\n=== Step 8: Registering and Deploying Semantic Highlighting Model ===")

model_path = "saved_models/sentence-highlighting_opensearch-semantic-highlighter-v1-1.0.0-torch_script.zip"
model_config_path = "saved_models/mlcommons_model_config.json"

# Check if files exist before proceeding
if not os.path.exists(model_path):
    print(f"❌ Model file not found: {model_path}")
    exit(1)
    
if not os.path.exists(model_config_path):
    print(f"❌ Config file not found: {model_config_path}")
    exit(1)

# Get file sizes for debugging
model_size = os.path.getsize(model_path) / (1024 * 1024)  # Size in MB
print(f"📊 Model file size: {model_size:.2f} MB")

# Alternative method: Register model using direct API calls instead of ml_client
# This provides better error handling and timeout control
print("Registering model using direct API method...")

try:
    # Read the model config
    with open(model_config_path, 'r') as f:
        model_config = json.load(f)
    
    # Method 1: Try using ml_client with retry logic
    max_retries = 3
    retry_count = 0
    model_id_file_system = None
    
    while retry_count < max_retries and model_id_file_system is None:
        try:
            print(f"Attempt {retry_count + 1}/{max_retries} - Registering model...")
            
            # Create a new client with extended timeout for this operation
            extended_timeout_client = OpenSearch(
                hosts=[CLUSTER_URL],
                http_auth=('admin', 'Developer@123'),
                verify_certs=False,
                ssl_assert_hostname=False,
                ssl_show_warn=False,
                use_ssl=True,
                timeout=600,  # 10 minutes timeout
                max_retries=3,
                retry_on_timeout=True
            )
            
            # Create extended timeout ml_client
            extended_ml_client = MLCommonClient(extended_timeout_client)
            
            model_id_file_system = extended_ml_client.register_model(
                model_path, 
                model_config_path, 
                isVerbose=True, 
                deploy_model=False
            )
            print(f"✅ Model registered with ID: {model_id_file_system}")
            break
            
        except Exception as e:
            retry_count += 1
            print(f"❌ Attempt {retry_count} failed: {str(e)}")
            
            if retry_count < max_retries:
                print(f"⏳ Waiting 30 seconds before retry...")
                time.sleep(30)
            else:
                print(f"❌ All registration attempts failed. Trying alternative method...")
                
                # Method 2: Try using the direct transport API
                try:
                    print("🔄 Trying direct API registration method...")
                    
                    # Register using transport API directly
                    register_body = {
                        "name": model_config["name"],
                        "version": model_config["version"], 
                        "model_group_id": model_group_id,
                        "model_format": model_config["model_format"],
                        "function_name": model_config["function_name"],
                        "model_config": model_config.get("model_config", {}),
                        "description": model_config.get("description", "")
                    }
                    
                    # First register the model metadata
                    register_response = client.transport.perform_request(
                        method='POST',
                        url='/_plugins/_ml/models/_register',
                        body=register_body,
                        timeout=600
                    )
                    
                    register_task_id = register_response['task_id']
                    print(f"📋 Registration task ID: {register_task_id}")
                    
                    # Wait for registration to complete
                    while True:
                        task_status = client.transport.perform_request(
                            method='GET',
                            url=f'/_plugins/_ml/tasks/{register_task_id}'
                        )
                        print(f"Registration status: {task_status['state']}")
                        
                        if task_status['state'] == 'COMPLETED':
                            model_id_file_system = task_status['model_id']
                            print(f"✅ Model registered with ID: {model_id_file_system}")
                            break
                        elif task_status['state'] == 'FAILED':
                            raise Exception(f"Registration failed: {task_status.get('error', 'Unknown error')}")
                        
                        time.sleep(10)
                        
                except Exception as api_error:
                    print(f"❌ Direct API method also failed: {api_error}")
                    print("💡 Suggestions to resolve SSL issues:")
                    print("1. Check if OpenSearch cluster is running and accessible")
                    print("2. Verify network connectivity and firewall settings")
                    print("3. Try restarting the OpenSearch cluster")
                    print("4. Check cluster logs for SSL-related errors")
                    print("5. Consider using a smaller model file for testing")
                    raise

    if model_id_file_system:
        print(f"✅ Model registration successful! Model ID: {model_id_file_system}")
        
        # Deploy the model with error handling
        print("Deploying model...")
        try:
            deploy_response = client.transport.perform_request(
                method='POST',
                url=f'/_plugins/_ml/models/{model_id_file_system}/_deploy',
                timeout=300
            )
            
            deploy_task_id = deploy_response['task_id']
            print(f"📋 Deployment task ID: {deploy_task_id}")
            
            # Wait for deployment to complete
            while True:
                deployment_status = client.transport.perform_request(
                    method='GET',
                    url=f'/_plugins/_ml/tasks/{deploy_task_id}'
                )
                print(f"Deployment status: {deployment_status['state']}")
                
                if deployment_status['state'] == 'COMPLETED':
                    print("✅ Model deployed successfully")
                    break
                elif deployment_status['state'] == 'FAILED':
                    print(f"❌ Deployment failed: {deployment_status.get('error', 'Unknown error')}")
                    break
                    
                time.sleep(10)
                
        except Exception as deploy_error:
            print(f"❌ Deployment failed: {deploy_error}")
            print("⚠️ Model registered but deployment failed. You can try deploying manually later.")
    
except Exception as e:
    print(f"❌ Model registration completely failed: {e}")
    print(f"Error type: {type(e).__name__}")
    
    # Provide troubleshooting information
    print("\n🔧 Troubleshooting SSL Issues:")
    print("1. Verify OpenSearch is running: curl -ku admin:Developer@123 https://localhost:9200")
    print("2. Check OpenSearch logs for SSL errors")
    print("3. Try reducing timeout or using HTTP instead of HTTPS")
    print("4. Ensure no firewall is blocking the connection")
    print("5. Check if the model file is corrupted")
    
    # Don't exit - continue with the rest of the script
    model_id_file_system = None

# ================================================================================
# STEP 9: CREATE AND CONFIGURE INGEST PIPELINE & INDEX
# ================================================================================

pipeline_body = {
    "description": "A pipeline to generate text embeddings",
    "processors": [
        {
            "text_embedding": {
                "model_id": model_id,
                "field_map": {
                    "text": "text_embedding"
                }
            }
        }
    ]
}
client.ingest.put_pipeline(id="nlp-ingest-pipeline", body=pipeline_body)
print("Ingest pipeline created")

print("\n=== Step 8: Creating Search Index ===")

# Define index configuration
index_config = {
    "settings": {"index.default_pipeline": "nlp-ingest-pipeline", "knn": True},
    "mappings": {
        "properties": {
            "text": {"type": "text"},
            "text_embedding": {
                "type": "knn_vector",
                "dimension": 768,
                "method": {
                    "name": "hnsw",
                    "space_type": "l2",
                    "engine": "lucene"
                }
            }
        }
    }
}

try:
    # Delete existing index if it exists
    client.indices.delete(index="neural-search-index", ignore=[404])
    
    # Create new index
    response = client.indices.create(index="neural-search-index", body=index_config)
    print("✅ Index 'neural-search-index' created successfully")
    
    # Test document indexing
    test_doc = {"text": "OpenSearch is an open-source search platform."}
    response = client.index(index="neural-search-index", id=1, body=test_doc)
    print("✅ Test document indexed successfully")
    
except Exception as e:
    print(f"❌ Index creation error: {e}")

# ================================================================================
# STEP 10: INDEX QUESTION ANSWERING DOCUMENTS
# ================================================================================

print("\n=== Step 9: Indexing Question Answering Documents ===")

# Sample documents for question answering
documents = [
    {"text": "Alzheimer's disease is a progressive neurodegenerative disorder characterized by accumulation of amyloid-beta plaques and neurofibrillary tangles in the brain. Early symptoms include short-term memory impairment, followed by language difficulties, disorientation, and behavioral changes. While traditional treatments such as cholinesterase inhibitors and memantine provide modest symptomatic relief, they do not alter disease progression. Recent clinical trials investigating monoclonal antibodies targeting amyloid-beta, including aducanumab, lecanemab, and donanemab, have shown promise in reducing plaque burden and slowing cognitive decline. Early diagnosis using biomarkers such as cerebrospinal fluid analysis and PET imaging may facilitate timely intervention and improved outcomes."},
    {"text": "Major depressive disorder is characterized by persistent feelings of sadness, anhedonia, and neurovegetative symptoms affecting sleep, appetite, and energy levels. First-line pharmacological treatments include selective serotonin reuptake inhibitors (SSRIs) and serotonin-norepinephrine reuptake inhibitors (SNRIs), with response rates of approximately 60-70%. Cognitive-behavioral therapy demonstrates comparable efficacy to medication for mild to moderate depression and may provide more durable benefits. Treatment-resistant depression may respond to augmentation strategies including atypical antipsychotics, lithium, or thyroid hormone. Electroconvulsive therapy remains the most effective intervention for severe or treatment-resistant depression, while newer modalities such as transcranial magnetic stimulation and ketamine infusion offer promising alternatives with fewer side effects."},
    {"text" : "Cardiovascular disease remains the leading cause of mortality worldwide, accounting for approximately one-third of all deaths. Risk factors include hypertension, diabetes mellitus, smoking, obesity, and family history. Recent advancements in preventive cardiology emphasize lifestyle modifications such as Mediterranean diet, regular exercise, and stress reduction techniques. Pharmacological interventions including statins, beta-blockers, and ACE inhibitors have significantly reduced mortality rates. Emerging treatments focus on inflammation modulation and precision medicine approaches targeting specific genetic profiles associated with cardiac pathologies."}
]

# Index all documents
for i, doc in enumerate(documents):
    try:
        response = client.index(index="neural-search-index", id=i+2, body=doc)
        print(f"✅ Document {i+1} indexed successfully")
    except Exception as e:
        print(f"❌ Document {i+1} indexing failed: {e}")

# Refresh index to make documents searchable
client.indices.refresh(index="neural-search-index")
print("✅ All documents indexed and refreshed")

# ================================================================================
# STEP 11: PERFORM NEURAL SEARCH QUERY
# ================================================================================

print("\n=== Step 11: Performing Neural Search Query ===")

# Verify model types before proceeding
print("🔍 Verifying Model Types...")
try:
    # Check text embedding model
    text_embedding_model_info = client.transport.perform_request(
        method='GET',
        url=f'/_plugins/_ml/models/{model_id}'
    )
    print(f"Text Embedding Model ({model_id}):")
    print(f"  - Function: {text_embedding_model_info.get('function_name', 'Unknown')}")
    print(f"  - State: {text_embedding_model_info.get('model_state', 'Unknown')}")
    
    # Check question answering model
    qa_model_info = client.transport.perform_request(
        method='GET',
        url=f'/_plugins/_ml/models/{model_id_file_system}'
    )
    print(f"Question Answering Model ({model_id_file_system}):")
    print(f"  - Function: {qa_model_info.get('function_name', 'Unknown')}")
    print(f"  - State: {qa_model_info.get('model_state', 'Unknown')}")
    
except Exception as e:
    print(f"⚠️ Warning: Could not verify model info: {e}")

# Define the neural search query
neural_search_query = {
    "_source": {
        "excludes": ["text_embedding"]  # Exclude the large embedding from the source
    },
    "query": {
        "neural": {
            "text_embedding": {
                "query_text": "treatments for neurodegenerative diseases",
                "model_id": model_id,  # Use the text embedding model ID from Step 7
                "k": 2
            }
        }
    }
}

# Only add semantic highlighting if the model was successfully registered
if model_id_file_system:
    neural_search_query["highlight"] = {
        "fields": {
            "text": {
                "type": "semantic"
            }
        },
        "options": {
            "model_id": model_id_file_system  # Use the semantic highlighting model
        }
    }
    print(f"Using semantic highlighting model: {model_id_file_system}")
else:
    print("⚠️ Semantic highlighting model not available - using standard highlighting")
    # Fall back to standard highlighting
    neural_search_query["highlight"] = {
        "fields": {
            "text": {
                "fragment_size": 150,
                "number_of_fragments": 3
            }
        }
    }

print("Executing neural search query...")
print(f"Query text: 'treatments for neurodegenerative diseases'")
print(f"Using Text Embedding Model ID: {model_id}")

try:
    # Execute the neural search query
    search_response = client.search(
        index="neural-search-index",
        body=neural_search_query
    )
    
    print("\n✅ Neural search query executed successfully!")
    print(f"Total hits: {search_response['hits']['total']['value']}")
    print(f"Max score: {search_response['hits']['max_score']}")
    
    # Display search results
    print("\n--- Search Results ---")
    for i, hit in enumerate(search_response['hits']['hits']):
        print(f"\nResult {i+1}:")
        print(f"Score: {hit['_score']}")
        print(f"Document ID: {hit['_id']}")
        print(f"Text: {hit['_source']['text'][:200]}...")  # Show first 200 characters
        
        # Display highlights if available
        if 'highlight' in hit:
            print("Highlights:")
            for field, highlights in hit['highlight'].items():
                for highlight in highlights:
                    print(f"  - {highlight}")
    
    # Store model IDs for future use
    print(f"\n📋 Model Information:")
    print(f"Text Embedding Model ID: {model_id}")
    print(f"Question Answering Model ID: {model_id_file_system}")
    
except Exception as e:
    print(f"❌ Neural search query failed: {e}")
    print(f"Error details: {str(e)}")
    
    # Additional debugging information
    print(f"\nDebugging Information:")
    print(f"- Text Embedding Model (for neural search): {model_id}")
    print(f"- Question Answering Model (for QA tasks): {model_id_file_system}")
    print(f"- Make sure you're using the TEXT_EMBEDDING model for neural search queries")

# ================================================================================
# STEP 12: ADDITIONAL NEURAL SEARCH EXAMPLES
# ================================================================================

print("\n=== Step 12: Additional Neural Search Examples ===")

# Additional search queries to demonstrate different use cases
additional_queries = [
    "depression treatment options",
    "cardiovascular disease prevention",
    "brain imaging techniques"
]

for query_text in additional_queries:
    print(f"\n--- Searching for: '{query_text}' ---")
    
    search_query = {
        "_source": {
            "excludes": ["text_embedding"]
        },
        "query": {
            "neural": {
                "text_embedding": {
                    "query_text": query_text,
                    "model_id": model_id,
                    "k": 1  # Return top 1 result for brevity
                }
            }
        }
    }
    
    try:
        response = client.search(index="neural-search-index", body=search_query)
        
        if response['hits']['total']['value'] > 0:
            top_hit = response['hits']['hits'][0]
            print(f"Best match (Score: {top_hit['_score']:.4f}):")
            print(f"{top_hit['_source']['text'][:150]}...")
        else:
            print("No matches found")
            
    except Exception as e:
        print(f"Search failed: {e}")

print("\n🎉 Neural search demonstration completed!")
