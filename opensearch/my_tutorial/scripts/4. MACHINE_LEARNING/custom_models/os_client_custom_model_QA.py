import torch
import opensearch_py_ml as oml
from opensearch_py_ml.ml_commons import MLCommonClient
from opensearchpy import OpenSearch
import zipfile
import os
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
        timeout=300  # Increased timeout to 300 seconds
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
# STEP 7: REGISTER AND DEPLOY MODEL IN OPENSEARCH
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
ml_client.deploy_model(model_id_file_system)
print("✅ Model deployed successfully")

# ================================================================================
# STEP 8: CREATE AND CONFIGURE INDEX
# ================================================================================

print("\n=== Step 8: Creating Search Index ===")

# Define index configuration
index_config = {
    "settings": {"number_of_shards": 2},
    "mappings": {"properties": {"text": {"type": "text"}}}
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
# STEP 9: INDEX QUESTION ANSWERING DOCUMENTS
# ================================================================================

print("\n=== Step 9: Indexing Question Answering Documents ===")

# Sample documents for question answering
documents = [
    {"text": "OpenSearch is a community-driven, open source search and analytics suite derived from Elasticsearch 7.10.2 and Kibana 7.10.2."},
    {"text": "OpenSearch was developed by Amazon Web Services (AWS) after the fork of Elasticsearch and Kibana."},
    {"text": "OpenSearch offers features like full-text search, real-time indexing, distributed search, and analytics capabilities."},
    {"text": "OpenSearch is compatible with Elasticsearch 7.10.2 APIs, but it has diverged in later versions."},
    {"text": "OpenSearch is licensed under the Apache 2.0 License."}
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
# STEP 10: PERFORM QUESTION ANSWERING
# ================================================================================

print("\n=== Step 10: Question Answering Demo ===")

# Retrieve all documents as context
search_response = client.search(
    index="neural-search-index",
    body={"query": {"match_all": {}}, "size": 10}
)

# Combine all documents into a single context
context = " ".join([hit["_source"]["text"] for hit in search_response["hits"]["hits"]])
print(f"Context prepared (length: {len(context)} characters)")

# Test questions
questions = ["What is OpenSearch?", "Who developed OpenSearch?"]

for question in questions:
    print(f"\n📝 Question: {question}")
    
    # Prepare question answering input
    qa_input = {
        "question": question,
        "context": context
    }
    
    try:
        # Get answer from the deployed model
        result = ml_client.predict(model_id_file_system, qa_input)
        print(f"✅ Answer: {result}")
    except Exception as e:
        print(f"⚠ Prediction error: {e}")
        
        # Check model status for debugging
        try:
            model_info = ml_client.get_model_info(model_id_file_system)
            print(f"Model state: {model_info.get('model_state', 'Unknown')}")
        except Exception as e2:
            print(f"Cannot retrieve model info: {e2}")

print("\n=== Question Answering Pipeline Complete ===")