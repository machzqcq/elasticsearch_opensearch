from opensearchpy import OpenSearch, RequestsHttpConnection
import time
import sys
sys.path.append('../../')
from helpers import create_embedding_model
from opensearchpy.helpers import bulk

# Initialize the OpenSearch client
client = OpenSearch(
    hosts=[{'host': '192.168.0.111', 'port': 9200}],
    http_auth=('admin', 'Developer123'),  # Replace with your credentials
    use_ssl=True,
    verify_certs=False,
    connection_class=RequestsHttpConnection
)

# Create an embedding model
embedding_model_body = {
        "name": "huggingface/sentence-transformers/all-MiniLM-L6-v2",
        "version": "1.0.1",
        "model_format": "TORCH_SCRIPT"
    }
# embedding_model_id = create_embedding_model(os_client=client,model_group_name=None,model_body=embedding_model_body)
embedding_model_id = "3Aq7U5IBH38uXGW4dlV4"
print(f"Model ID: {embedding_model_id}")

# Create ecommerce index
index_body = {
    "settings": {
        "index.knn": True,
        "default_pipeline": "ecommerce_foreach_pipeline"
    },
      "mappings": {
    "properties": {
      "products": {
        "type": "nested",
        "properties": {
          "product_name_embedding": {
            "type": "knn_vector",
            "dimension": 384,
            "method": {
                    "name": "hnsw",
                    "space_type": "l2",
                    "engine": "lucene"
                }
          },
          "product_name": {
            "type": "text"
          }
        }
      }
    }
  }
}
response = client.indices.create(index="ecommerce", body=index_body)
print("Index created:", response)

# Create an ingestion pipeline
ingest_pipeline_body ={
  "processors": [
    {
      "set": {
        "field": "product_name_tmp",
        "value": ""
      }
    },
    {
      "text_embedding": {
        "model_id": embedding_model_id,
        "field_map": {
          "product_name_tmp": "_ingest._value.product_name_embedding"
        }
      }
    },
    {
      "remove": {
        "field": "product_name_tmp"
      }
    }
  ]
}
client.ingest.put_pipeline(id="ecommerce_pipeline", body=ingest_pipeline_body)

# Create for each ingestion pipeline
foreach_pipeline_body = {
  "description": "Test nested embeddings",
  "processors": [
    {
      "foreach": {
        "field": "products",
        "processor": {
          "pipeline": {
            "name": "ecommerce_pipeline"
          }
        },
        "ignore_failure": True
      }
    }
  ]
}

client.ingest.put_pipeline(id="ecommerce_foreach_pipeline", body=foreach_pipeline_body)

# Ingest data
BASE_DIR = "../../../data"
data = []
with open(f"{BASE_DIR}/ecommerce_lite.json", 'r') as file:
    for line in file:
        data.append(line.strip() + '\n')

# Use the bulk helper to index the data
bulk(client, actions=data, index='ecommerce', refresh=True)