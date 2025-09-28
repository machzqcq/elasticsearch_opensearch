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
# STEP 2: DOWNLOAD AND PREPARE THE HUGGING FACE MODEL
# ================================================================================

print("\n=== Step 2: Preparing Hugging Face Model ===")

# Create directory for saved models
os.makedirs("saved_models", exist_ok=True)

# Model configuration
model_name = "distilbert/distilbert-base-uncased-distilled-squad"
text_to_encode = "example search query"  # Dummy input for tracing

print(f"Loading model: {model_name}")

# Load the pre-trained model and tokenizer
model = AutoModelForQuestionAnswering.from_pretrained(model_name, torchscript=True, return_dict=False)
tokenizer = AutoTokenizer.from_pretrained(model_name)
processor = AutoProcessor.from_pretrained(model_name)

print("✅ Model and tokenizer loaded successfully")

# ================================================================================
# STEP 3: CONVERT MODEL TO TORCHSCRIPT FORMAT
# ================================================================================

print("\n=== Step 3: Converting Model to TorchScript ===")

# Generate dummy input for model tracing
inputs = processor(text=text_to_encode, return_tensors="pt")
dummy_input = (inputs['input_ids'], inputs['attention_mask'])

# Trace the model and convert to TorchScript
print("Tracing model...")
traced_model = torch.jit.trace(model, dummy_input)

# Save the traced model
torch.jit.save(traced_model, "saved_models/distilbert-base-uncased-distilled-squad.pt")
print("✅ TorchScript model saved")

# ================================================================================
# STEP 4: SAVE MODEL COMPONENTS
# ================================================================================

print("\n=== Step 4: Saving Model Components ===")

# Save tokenizer
tokenizer.save_pretrained("saved_models/tokenizer")
print("✅ Tokenizer saved")

# Save model configuration
model.config.save_pretrained("saved_models/model_config")
print("✅ Model configuration saved")

# ================================================================================
# STEP 5: CREATE MODEL ZIP FILE
# ================================================================================

print("\n=== Step 5: Creating Model Zip File ===")

# Create zip file with model and tokenizer
with zipfile.ZipFile('saved_models/distilbert-base-uncased-distilled-squad.zip', 'w', zipfile.ZIP_DEFLATED) as zipf:
    # Add the TorchScript model
    zipf.write('saved_models/distilbert-base-uncased-distilled-squad.pt', 'distilbert-base-uncased-distilled-squad.pt')
    
    # Add the tokenizer
    zipf.write('saved_models/tokenizer/tokenizer.json', 'tokenizer.json')

print("✅ Model zip file created: saved_models/distilbert-base-uncased-distilled-squad.zip")

# ================================================================================
# STEP 6: CREATE ML COMMONS MODEL CONFIGURATION
# ================================================================================

print("\n=== Step 6: Creating ML Commons Configuration ===")

# Read model configuration
with open('saved_models/model_config/config.json') as f:
    all_config = json.load(f)

# Create ML Commons model configuration
mlcommons_model_config = {
    'name': "distilbert-base-uncased-distilled-squad",
    'version': '1.0.0',
    'model_format': 'TORCH_SCRIPT',
    "function_name": "QUESTION_ANSWERING",
    'model_config': {
        'model_type': 'distilbert',
        'framework_type': 'huggingface_transformers',
        'embedding_dimension': all_config.get('dim', 768)
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
# STEP 8: REGISTER AND DEPLOY QUESTION_ANSWERING MODEL IN OPENSEARCH
# ================================================================================

print("\n=== Step 7: Registering and Deploying Model ===")

model_path = "saved_models/distilbert-base-uncased-distilled-squad.zip"
model_config_path = "saved_models/mlcommons_model_config.json"

# Register the model
print("Registering model...")
model_id_file_system = ml_client.register_model(model_path, model_config_path, isVerbose=True, deploy_model=False)
print(f"✅ Model registered with ID: {model_id_file_system}")

# Deploy the model
print("Deploying model...")
ml_client.deploy_model(model_id_file_system, wait_until_deployed=True)
print("✅ Model deployed successfully")

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
                "query_text": "What are some treatments for neurodegenerative diseases",
                "model_id": model_id,  # Use the text embedding model ID from Step 7
                "k": 2
            }
        }
    },
    "highlight": {
        "fields": {
            "text": {
                "type": "semantic"
            }
        },
        "options": {
            "model_id": model_id_file_system  # Use the QA model
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
