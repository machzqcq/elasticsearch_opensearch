# SEE erros.md file
from opensearchpy import OpenSearch
from opensearch_py_ml.ml_commons import MLCommonClient
import time

IS_AUTH = False

if IS_AUTH:
    # Initialize the OpenSearch client
    client = OpenSearch(
        hosts=[{'host': '192.168.0.111', 'port': 9200}],
        http_auth=('admin', 'Padmasini10'),  # Replace with your credentials
        use_ssl=True,
        verify_certs=False,
        ssl_show_warn=False
    )
else:
    # Initialize the OpenSearch client without authentication
    client = OpenSearch(
        hosts=[{'host': '192.168.0.111', 'port': 9200}],
        use_ssl=False,
        verify_certs=False,
        ssl_assert_hostname = False,
        ssl_show_warn=False
    )

# Initialize ML Commons client
ml_client = MLCommonClient(client)

# Step 2: Register sentence transformer model
model_response = ml_client.register_pretrained_model(
    model_name="huggingface/sentence-transformers/msmarco-distilbert-base-tas-b",
    model_version="1.0.1",
    model_format="TORCH_SCRIPT",
    deploy_model=True,
    wait_until_deployed=True
)
model_id = model_response
print(f"Model ID: {model_id}")

# Wait for model to be fully deployed
while True:
    model_info = ml_client.get_model_info(model_id)
    if model_info['model_state'] == 'DEPLOYED':
        break
    time.sleep(5)

print("Model deployed successfully")

# Step 3: Create ingest pipeline
pipeline_body = {
    "description": "Text embedding pipeline",
    "processors": [
        {
            "text_embedding": {
                "model_id": model_id,
                "field_map": {
                    "text_field": "embedding_vector"
                }
            }
        }
    ]
}
client.ingest.put_pipeline(id="my_embedding_pipeline", body=pipeline_body)
print("Ingest pipeline created")

# Step 4: Create index
index_body = {
    "settings": {
        "index.knn": True,
        "default_pipeline": "my_embedding_pipeline"
    },
    "mappings": {
        "properties": {
            "text_field": {"type": "text"},
            "embedding_vector": {
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
client.indices.create(index="my_index", body=index_body)
print("Index created")

# Step 5: Load sample documents
sample_docs = [
    {"text_field": "This is a sample text for embedding"},
    {"text_field": "Another example sentence for vector search"}
]

for doc in sample_docs:
    client.index(index="my_index", body=doc)

print("Sample documents loaded")