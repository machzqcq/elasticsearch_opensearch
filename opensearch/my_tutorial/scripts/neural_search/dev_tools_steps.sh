POST /_plugins/_ml/model_groups/_register
{
  "name": "my_model_group",
  "description": "My model group for text embedding",
  "access_mode": "public"
}

# Retrieve the model group ID

POST /_plugins/_ml/models/_register
{
  "name": "huggingface/sentence-transformers/msmarco-distilbert-base-tas-b",
  "version": "1.0.1",
  "model_group_id": "pCnqD5IB6r2c901zBpon",
  "model_format": "TORCH_SCRIPT",
  "description": "Sentence transformer model for embeddings"
}

GET /_plugins/_ml/tasks/qCnqD5IB6r2c901zOpon

POST /_plugins/_ml/models/0Gm-D5IB3Tgmjj73pIun/_deploy

GET /_plugins/_ml/tasks/IWnCD5IB3Tgmjj73fIyv

PUT /_ingest/pipeline/my_embedding_pipeline
{
  "description": "Text embedding pipeline",
  "processors": [
    {
      "text_embedding": {
        "model_id": "0Gm-D5IB3Tgmjj73pIun",
        "field_map": {
          "text_field": "embedding_vector"
        }
      }
    }
  ]
}


PUT /my_index
{
  "settings": {
    "index.knn": true,
    "default_pipeline": "my_embedding_pipeline"
  },
  "mappings": {
    "properties": {
      "text_field": { "type": "text" },
      "embedding_vector": {
        "type": "knn_vector",
        "dimension": 768,
        "method": {
          "name": "hnsw",
          "space_type": "l2",
          "engine": "nmslib"
        }
      }
    }
  }
}


PUT /my_index/_doc/1
{
  "text_field": "This is a sample text for embedding",
  "id": 1
}

POST my_index/_search
{
  "query": {"match_all": {}}
}