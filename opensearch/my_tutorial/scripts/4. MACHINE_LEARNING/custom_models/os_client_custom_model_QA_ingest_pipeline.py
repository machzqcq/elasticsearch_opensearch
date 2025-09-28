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

# Check if model files already exist
model_files_exist = all([
    os.path.exists("saved_models/distilbert-base-uncased-distilled-squad.pt"),
    os.path.exists("saved_models/tokenizer/tokenizer.json"),
    os.path.exists("saved_models/model_config/config.json"),
    os.path.exists("saved_models/distilbert-base-uncased-distilled-squad.zip"),
    os.path.exists("saved_models/mlcommons_model_config.json")
])

if model_files_exist:
    print("✅ Model files already exist in saved_models directory, skipping model preparation steps...")
    print("Proceeding to read model configuration...")
else:
    print("Model files not found, proceeding with model preparation...")
    
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
# STEP 7: REGISTER AND DEPLOY TEXT EMBEDDING MODEL
# ================================================================================
# This step registers and deploys a pre-trained text embedding model from Hugging Face
# that will be used for neural search (document retrieval based on semantic similarity).
# The model converts text into dense vector representations for similarity matching.

print("\n=== Step 7: Registering and Deploying Text Embedding Model ===")

# Create a unique model group for organizing related models
model_group_name = f"local_model_group_{int(time.time())}"
print(f"Registering model group: {model_group_name}")

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

# Register the text embedding model for neural search
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

register_task_id = register_response['task_id']

# Wait for model registration to complete
while True:
    task_status = client.transport.perform_request(
            method='GET',
            url=f'/_plugins/_ml/tasks/{register_task_id}'
    )
    print(task_status)
    if task_status['state'] == 'COMPLETED':
            model_id = task_status['model_id']
            break
    time.sleep(10)

# Deploy the registered model
deploy_response = client.transport.perform_request(
    method='POST',
    url=f'/_plugins/_ml/models/{model_id}/_deploy',
    timeout=50000
)
print(deploy_response)

deploy_task_id = deploy_response['task_id']

# Wait for model deployment to complete
while True:
    deployment_status = client.transport.perform_request(
        method='GET',
        url=f'/_plugins/_ml/tasks/{deploy_task_id}'
    )
    print(deployment_status)
    if deployment_status['state'] == 'COMPLETED':
        break
    time.sleep(10)

print("✅ Text embedding model registered and deployed successfully")


# ================================================================================
# STEP 8: REGISTER AND DEPLOY CUSTOM QUESTION ANSWERING MODEL
# ================================================================================
# This step registers and deploys our custom DistilBERT QA model that was prepared
# in the earlier steps. This model will extract specific answers from the documents
# retrieved by neural search.

print("\n=== Step 8: Registering and Deploying Custom QA Model ===")

model_path = "saved_models/distilbert-base-uncased-distilled-squad.zip"
model_config_path = "saved_models/mlcommons_model_config.json"

# Register the custom QA model using ML Commons client
print("Registering custom QA model...")
model_id_file_system = ml_client.register_model(model_path, model_config_path, isVerbose=True, deploy_model=False)
print(f"✅ Model registered with ID: {model_id_file_system}")

# Deploy the custom QA model
print("Deploying custom QA model...")
ml_client.deploy_model(model_id_file_system, wait_until_deployed=True)
print("✅ Custom QA model deployed successfully")

# ================================================================================
# STEP 9: CREATE INGEST PIPELINE AND SEARCH INDEX
# ================================================================================
# This step creates an ingest pipeline that automatically generates text embeddings
# for documents as they are indexed, and sets up a search index optimized for
# both traditional text search and neural (vector) search.

print("\n=== Step 9: Creating Ingest Pipeline and Search Index ===")

# Create ingest pipeline for automatic text embedding generation
pipeline_body = {
    "description": "A pipeline to generate text embeddings using the deployed text embedding model",
    "processors": [
        {
            "text_embedding": {
                "model_id": model_id,  # Use the deployed text embedding model
                "field_map": {
                    "text": "text_embedding"  # Convert 'text' field to 'text_embedding' vector
                }
            }
        }
    ]
}
client.ingest.put_pipeline(id="nlp-ingest-pipeline", body=pipeline_body)
print("✅ Ingest pipeline created")

# Define index configuration with both text and vector search capabilities
index_config = {
    "settings": {
        "index.default_pipeline": "nlp-ingest-pipeline",  # Auto-apply embedding pipeline
        "knn": True  # Enable k-nearest neighbor search for vectors
    },
    "mappings": {
        "properties": {
            "text": {"type": "text"},  # Traditional text field for keyword search
            "text_embedding": {
                "type": "knn_vector",  # Vector field for neural search
                "dimension": 768,      # DistilBERT embedding dimension
                "method": {
                    "name": "hnsw",        # Hierarchical Navigable Small World algorithm
                    "space_type": "l2",    # Euclidean distance
                    "engine": "lucene"     # Use Lucene engine
                }
            }
        }
    }
}

try:
    # Remove existing index if it exists
    client.indices.delete(index="neural-search-index", ignore=[404])
    
    # Create new index with the configuration
    response = client.indices.create(index="neural-search-index", body=index_config)
    print("✅ Index 'neural-search-index' created successfully")
    
    # Test document indexing to verify pipeline works
    test_doc = {"text": "OpenSearch is an open-source search platform."}
    response = client.index(index="neural-search-index", id=1, body=test_doc)
    print("✅ Test document indexed successfully")
    
except Exception as e:
    print(f"❌ Index creation error: {e}")

# ================================================================================
# STEP 10: INDEX SAMPLE DOCUMENTS FOR QUESTION ANSWERING
# ================================================================================
# This step indexes sample medical documents that contain information about various
# diseases and their treatments. These documents will be used to demonstrate
# the question answering capabilities of the pipeline.

print("\n=== Step 10: Indexing Question Answering Documents ===")

# Sample medical documents covering different conditions and treatments
documents = [
    {
        "text": "Alzheimer's disease is a progressive neurodegenerative disorder characterized by accumulation of amyloid-beta plaques and neurofibrillary tangles in the brain. Early symptoms include short-term memory impairment, followed by language difficulties, disorientation, and behavioral changes. While traditional treatments such as cholinesterase inhibitors and memantine provide modest symptomatic relief, they do not alter disease progression. Recent clinical trials investigating monoclonal antibodies targeting amyloid-beta, including aducanumab, lecanemab, and donanemab, have shown promise in reducing plaque burden and slowing cognitive decline. Early diagnosis using biomarkers such as cerebrospinal fluid analysis and PET imaging may facilitate timely intervention and improved outcomes."
    },
    {
        "text": "Major depressive disorder is characterized by persistent feelings of sadness, anhedonia, and neurovegetative symptoms affecting sleep, appetite, and energy levels. First-line pharmacological treatments include selective serotonin reuptake inhibitors (SSRIs) and serotonin-norepinephrine reuptake inhibitors (SNRIs), with response rates of approximately 60-70%. Cognitive-behavioral therapy demonstrates comparable efficacy to medication for mild to moderate depression and may provide more durable benefits. Treatment-resistant depression may respond to augmentation strategies including atypical antipsychotics, lithium, or thyroid hormone. Electroconvulsive therapy remains the most effective intervention for severe or treatment-resistant depression, while newer modalities such as transcranial magnetic stimulation and ketamine infusion offer promising alternatives with fewer side effects."
    },
    {
        "text": "Cardiovascular disease remains the leading cause of mortality worldwide, accounting for approximately one-third of all deaths. Risk factors include hypertension, diabetes mellitus, smoking, obesity, and family history. Recent advancements in preventive cardiology emphasize lifestyle modifications such as Mediterranean diet, regular exercise, and stress reduction techniques. Pharmacological interventions including statins, beta-blockers, and ACE inhibitors have significantly reduced mortality rates. Emerging treatments focus on inflammation modulation and precision medicine approaches targeting specific genetic profiles associated with cardiac pathologies."
    }
]

# Index all documents with automatic embedding generation via ingest pipeline
for i, doc in enumerate(documents):
    try:
        response = client.index(index="neural-search-index", id=i+2, body=doc)
        print(f"✅ Document {i+1} indexed successfully")
    except Exception as e:
        print(f"❌ Document {i+1} indexing failed: {e}")

# Refresh index to make documents immediately searchable
client.indices.refresh(index="neural-search-index")
print("✅ All documents indexed and refreshed")

# ================================================================================
# STEP 11: NEURAL SEARCH AND QUESTION ANSWERING PIPELINE
# ================================================================================
# This section demonstrates the complete RAG (Retrieval-Augmented Generation) pipeline:
# 1. Use neural search to find relevant documents based on semantic similarity
# 2. Apply the QA model to extract specific answers from retrieved documents
# This combines the power of semantic search with precise answer extraction.

print("\n=== Step 11: Neural Search and Question Answering Pipeline ===")

# Verify both models are properly deployed before proceeding
print("🔍 Verifying Model Deployment Status...")
try:
    # Check text embedding model status
    text_embedding_model_info = client.transport.perform_request(
        method='GET',
        url=f'/_plugins/_ml/models/{model_id}'
    )
    print(f"Text Embedding Model ({model_id}):")
    print(f"  - Function: {text_embedding_model_info.get('function_name', 'Unknown')}")
    print(f"  - State: {text_embedding_model_info.get('model_state', 'Unknown')}")
    
    # Check question answering model status
    qa_model_info = client.transport.perform_request(
        method='GET',
        url=f'/_plugins/_ml/models/{model_id_file_system}'
    )
    print(f"Question Answering Model ({model_id_file_system}):")
    print(f"  - Function: {qa_model_info.get('function_name', 'Unknown')}")
    print(f"  - State: {qa_model_info.get('model_state', 'Unknown')}")
    
except Exception as e:
    print(f"⚠️ Warning: Could not verify model info: {e}")

# ================================================================================
# NEURAL SEARCH: Retrieve relevant documents using semantic similarity
# ================================================================================
# Neural search uses the text embedding model to convert the query into a vector
# and finds documents with similar vectors, enabling semantic understanding.

print("\n--- Step 11a: Neural Search for Document Retrieval ---")

# Define neural search query for semantic document retrieval
neural_search_query = {
    "_source": {
        "excludes": ["text_embedding"]  # Don't return large embedding vectors in results
    },
    "query": {
        "neural": {
            "text_embedding": {
                "query_text": "What are some treatments for neurodegenerative diseases",
                "model_id": model_id,  # Use text embedding model for semantic search
                "k": 2  # Return top 2 most similar documents
            }
        }
    }
}

print("Executing neural search query...")
print(f"Query text: 'treatments for neurodegenerative diseases'")
print(f"Using Text Embedding Model ID: {model_id}")

try:
    # Execute neural search to retrieve relevant documents
    search_response = client.search(
        index="neural-search-index",
        body=neural_search_query
    )
    
    print(f"\n✅ Neural search completed successfully!")
    print(f"Total hits: {search_response['hits']['total']['value']}")
    print(f"Max score: {search_response['hits']['max_score']}")
    
    # Display retrieved documents
    print("\n--- Retrieved Documents ---")
    for i, hit in enumerate(search_response['hits']['hits']):
        print(f"\nDocument {i+1}:")
        print(f"Relevance Score: {hit['_score']:.4f}")
        print(f"Document ID: {hit['_id']}")
        print(f"Text Preview: {hit['_source']['text'][:200]}...")  # Show first 200 characters
    
    # ================================================================================
    # QUESTION ANSWERING: Extract specific answers from retrieved documents
    # ================================================================================
    # Now use the custom DistilBERT QA model to extract precise answers from the
    # documents that were retrieved by neural search. This completes the RAG pipeline.
    
    print("\n--- Step 11b: Question Answering with Retrieved Documents ---")
    question = "What are some treatments for neurodegenerative diseases?"
    
    for i, hit in enumerate(search_response['hits']['hits']):
        context_text = hit['_source']['text']
        
        # Prepare QA request using the working format (direct parameters)
        qa_request_body = {
            "question": question,
            "context": context_text
        }
        
        try:
            # Send QA request to the deployed DistilBERT QA model
            qa_response = client.transport.perform_request(
                method='POST',
                url=f'/_plugins/_ml/models/{model_id_file_system}/_predict',
                body=qa_request_body
            )
            
            print(f"\n✅ QA Result from Document {i+1}:")
            print(f"Question: {question}")
            
            # Parse the QA model response to extract the answer
            if 'inference_results' in qa_response:
                result = qa_response['inference_results'][0]
                if 'output' in result:
                    output = result['output']
                    if isinstance(output, list) and len(output) > 0:
                        qa_result = output[0]
                        if isinstance(qa_result, dict):
                            # Extract answer from the response (model returns 'result' field)
                            answer = qa_result.get('result', qa_result.get('answer', 'No answer found'))
                            score = qa_result.get('score', qa_result.get('confidence', 'N/A'))
                            start = qa_result.get('start', 'N/A')
                            end = qa_result.get('end', 'N/A')
                            
                            print(f"Answer: {answer}")
                            if score != 'N/A':
                                print(f"Confidence Score: {score}")
                            if start != 'N/A' and end != 'N/A':
                                print(f"Answer Span: {start}-{end}")
                        else:
                            print(f"Answer: {qa_result}")
                    else:
                        print(f"Raw output: {output}")
                else:
                    print(f"No output in result: {result}")
            else:
                print(f"No inference_results in response")
                
        except Exception as qa_error:
            print(f"❌ QA Error for Document {i+1}: {qa_error}")

    # Display model information for reference
    print(f"\n📋 Pipeline Summary:")
    print(f"✅ Neural Search Model ID: {model_id}")
    print(f"✅ Question Answering Model ID: {model_id_file_system}")
    print(f"✅ RAG Pipeline: Neural search → QA extraction → Precise answers")
    
except Exception as e:
    print(f"❌ Neural search query failed: {e}")
    print(f"Error details: {str(e)}")
    
    print(f"\nDebugging Information:")
    print(f"- Text Embedding Model (neural search): {model_id}")
    print(f"- Question Answering Model (answer extraction): {model_id_file_system}")
    print(f"- Ensure both models are properly deployed before running queries")

# ================================================================================
# STEP 12: ADDITIONAL NEURAL SEARCH DEMONSTRATIONS
# ================================================================================
# This section demonstrates the versatility of the neural search system by running
# additional queries on different medical topics to show semantic understanding
# across various domains within the indexed documents.

print("\n=== Step 12: Additional Neural Search Examples ===")

# Various medical queries to test semantic search capabilities
additional_queries = [
    "depression treatment options",        # Should match the depression document
    "cardiovascular disease prevention",   # Should match the cardiovascular document
    "brain imaging techniques"            # Should match the Alzheimer's document (mentions PET imaging)
]

for query_text in additional_queries:
    print(f"\n--- Neural Search: '{query_text}' ---")
    
    # Create search query for each test case
    search_query = {
        "_source": {
            "excludes": ["text_embedding"]
        },
        "query": {
            "neural": {
                "text_embedding": {
                    "query_text": query_text,
                    "model_id": model_id,  # Use text embedding model
                    "k": 1  # Return only the top result for brevity
                }
            }
        }
    }
    
    try:
        response = client.search(index="neural-search-index", body=search_query)
        
        if response['hits']['total']['value'] > 0:
            top_hit = response['hits']['hits'][0]
            print(f"✅ Best match (Score: {top_hit['_score']:.4f}):")
            print(f"   {top_hit['_source']['text'][:150]}...")
        else:
            print("❌ No matches found")
            
    except Exception as e:
        print(f"❌ Search failed: {e}")

print("\n🎉 Neural Search and Question Answering Pipeline Demonstration Completed!")
print("\n" + "="*80)
print("PIPELINE SUMMARY:")
print("1. ✅ Custom DistilBERT QA model prepared and deployed")
print("2. ✅ Text embedding model deployed for neural search") 
print("3. ✅ Ingest pipeline created for automatic embedding generation")
print("4. ✅ Search index configured for both text and vector search")
print("5. ✅ Medical documents indexed with embeddings")
print("6. ✅ Neural search retrieves semantically similar documents")
print("7. ✅ QA model extracts precise answers from retrieved documents")
print("8. ✅ Complete RAG pipeline operational")
print("="*80)
