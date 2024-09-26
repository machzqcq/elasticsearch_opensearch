# SEE erros.md file
from opensearchpy import OpenSearch
from opensearch_py_ml.ml_commons import MLCommonClient
import time
import pandas as pd
import sys
sys.path.append('../')
from helpers import opensearch_bulk_async, dataframe_to_actions
from opensearchpy import OpenSearch, helpers

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
    "description": "interns embedding pipeline",
    "processors": [
        {
            "text_embedding": {
                "model_id": model_id,
                "field_map": {
                    "COMPANY": "company_embedding_vector",
                    "JOB_TITLE": "job_title_embedding_vector",
                    "JOB_CONTENT_TEXT": "job_content_text_embedding_vector"
                }
            }
        }
    ]
}
client.ingest.put_pipeline(id="interns_embedding_pipeline", body=pipeline_body)
print("Ingest pipeline created")

# Step 4: Create index
index_body = {
    "settings": {
        "index.knn": True,
        "default_pipeline": "interns_embedding_pipeline"
    },
    "mappings": {
        "properties": {
            "COMPANY": {"type": "text"},
            "JOB_TITLE": {"type": "text"},
            "JOB_CONTENT_TEXT": {"type": "text"},
            "company_embedding_vector": {
                "type": "knn_vector",
                "dimension": 768,
                "method": {
                    "name": "hnsw",
                    "space_type": "l2",
                    "engine": "lucene"
                }
            },
            "job_title_embedding_vector": {
                "type": "knn_vector",
                "dimension": 768,
                "method": {
                    "name": "hnsw",
                    "space_type": "l2",
                    "engine": "lucene"
                }
        },
        "job_content_text_embedding_vector": {
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
client.indices.create(index="interns", body=index_body)
print("Index created")

# Step 5: Load sample documents
BASE_DIR = "../../data"
df = pd.read_parquet(f"{BASE_DIR}/interns_sample.parquet")

data = dataframe_to_actions(df.iloc[0:10], "interns")
success, failed = helpers.bulk(client=client, actions=data)

print(f"Successfully indexed {success} documents.")

print("Sample documents loaded")