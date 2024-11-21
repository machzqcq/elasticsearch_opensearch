from opensearchpy import OpenSearch, RequestsHttpConnection
import time
import sys
sys.path.append('../../')
from helpers import create_embedding_model
from opensearchpy.helpers import bulk

# Initialize the OpenSearch client
client = OpenSearch(
    hosts=[{'host': '192.168.0.111', 'port': 9200}],
    http_auth=('admin', 'Developer@123'),  # Replace with your credentials
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
embedding_model_id = create_embedding_model(os_client=client,model_group_name=None,model_body=embedding_model_body)
print(f"Model ID: {embedding_model_id}")

# Create an ingestion pipeline
ingest_pipeline_body ={
  "description": "An NLP ingest pipeline",
  "processors": [
    {
      "text_embedding": {
        "model_id": embedding_model_id,
        "field_map": {
          "text": "passage_embedding"
        }
      }
    }
  ]
}
client.ingest.put_pipeline(id="nlp-ingest-pipeline", body=ingest_pipeline_body)

# Create index
index_body = {
  "settings": {
    "index.knn": True,
    "default_pipeline": "nlp-ingest-pipeline"
  },
  "mappings": {
    "properties": {
      "id": {
        "type": "text"
      },
      "passage_embedding": {
        "type": "knn_vector",
        "dimension": 384,
        "method": {
          "engine": "lucene",
          "space_type": "l2",
          "name": "hnsw",
          "parameters": {}
        }
      },
      "text": {
        "type": "text"
      }
    }
  }
}
response = client.indices.create(index="my-nlp-index", body=index_body)
print("Index created:", response)

documents = [
    {
        "text": "A wild animal races across an uncut field with a minimal amount of trees .",
        "id": "1775029934.jpg"
    },
    {
        "text": "People line the stands which advertise Freemont 's orthopedics , a cowboy rides a light brown bucking bronco .",
        "id": "2664027527.jpg"
    },
    {
        "text": "A man who is riding a wild horse in the rodeo is very near to falling off .",
        "id": "4427058951.jpg"
    },
    {
        "text": "A rodeo cowboy , wearing a cowboy hat , is being thrown off of a wild white horse .",
        "id": "2691147709.jpg"
    }
]

actions = [
    {
        "_op_type": "index",
        "_index": "my-nlp-index",
        "_id": i +1,
        "_source": doc
    }
    for i, doc in enumerate(documents)
]

response = bulk(client, actions)
print("Documents indexed:", response)

# Get a sample document and display
doc_id = 1
response = client.get(index="my-nlp-index", id=doc_id)
print(f"Document {doc_id}:", response['_source'])

# Search using text query
search_query = {
    "_source": {
        "excludes": ["passage_embedding"]
    },
    "query": {
        "match": {
            "text": {
                "query": "wild west"
            }
        }
    }
}
response = client.search(index="my-nlp-index", body=search_query)
print("Text query search results:", response['hits']['hits'])

# Semantic Search
semantic_search_query = {
    "_source": {
        "excludes": ["passage_embedding"]
    },
    "query": {
        "neural": {
            "passage_embedding": {
                "query_text": "wild west",
                "model_id": embedding_model_id,
                "k": 5
            }
        }
    }
}
response = client.search(index="my-nlp-index", body=semantic_search_query)
print("Semantic search results:", response['hits']['hits'])

# Hybrid Search - create normalizer pipeline
normalizer_pipeline_body = {
    "description": "Post processor for hybrid search",
    "phase_results_processors": [
        {
            "normalization-processor": {
                "normalization": {
                    "technique": "min_max"
                },
                "combination": {
                    "technique": "arithmetic_mean",
                    "parameters": {
                        "weights": [0.3, 0.7]
                    }
                }
            }
        }
    ]
}
client.transport.perform_request('PUT', '/_search/pipeline/nlp-search-pipeline', body=normalizer_pipeline_body)

# Hybrid search query
hybrid_search_query = {
    "_source": {
        "excludes": ["passage_embedding"]
    },
    "query": {
        "hybrid": {
            "queries": [
                {
                    "match": {
                        "text": {
                            "query": "cowboy rodeo bronco"
                        }
                    }
                },
                {
                    "neural": {
                        "passage_embedding": {
                            "query_text": "wild west",
                            "model_id": embedding_model_id,
                            "k": 5
                        }
                    }
                }
            ]
        }
    }
}
response = client.search(index="my-nlp-index", body=hybrid_search_query, search_pipeline="nlp-search-pipeline")
print("Hybrid search results:", response['hits']['hits'])
