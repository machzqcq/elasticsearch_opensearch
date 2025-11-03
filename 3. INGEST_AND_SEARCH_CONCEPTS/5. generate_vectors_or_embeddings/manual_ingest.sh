# Tried with docker-compose-opensearch-ml2.17.0.yml
POST /_plugins/_ml/model_groups/_register
{
  "name": "NLP_model_group",
  "description": "A model group for NLP models",
  "access_mode": "public"
}

POST /_plugins/_ml/models/_register
{
  "name": "huggingface/sentence-transformers/msmarco-distilbert-base-tas-b",
  "version": "1.0.1",
  "model_group_id": "Bi87WJIBD7vSR-tWXPEA",
  "model_format": "TORCH_SCRIPT"
}

GET /_plugins/_ml/tasks/Ci87WJIBD7vSR-tWr_HI

POST /_plugins/_ml/models/sJQ7WJIB_R9sSTWYtZhx/_deploy

GET /_plugins/_ml/tasks/Iy89WJIBD7vSR-tWo_Gj

PUT /_ingest/pipeline/nlp-ingest-pipeline
{
  "description": "An NLP ingest pipeline",
  "processors": [
    {
      "text_embedding": {
        "model_id": "sJQ7WJIB_R9sSTWYtZhx",
        "field_map": {
          "text": "passage_embedding"
        }
      }
    }
  ]
}

PUT /my-nlp-index
{
  "settings": {
    "index.knn": true,
    "default_pipeline": "nlp-ingest-pipeline"
  },
  "mappings": {
    "properties": {
      "id": {
        "type": "text"
      },
      "passage_embedding": {
        "type": "knn_vector",
        "dimension": 768,
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

PUT /my-nlp-index/_doc/1
{
  "text": "A West Virginia university women 's basketball team , officials , and a small gathering of fans are in a West Virginia arena .",
  "id": "4319130149.jpg"
}

PUT /my-nlp-index/_doc/2
{
  "text": "A wild animal races across an uncut field with a minimal amount of trees .",
  "id": "1775029934.jpg"
}

PUT /my-nlp-index/_doc/3
{
  "text": "People line the stands which advertise Freemont 's orthopedics , a cowboy rides a light brown bucking bronco .",
  "id": "2664027527.jpg"
}

PUT /my-nlp-index/_doc/4
{
  "text": "A man who is riding a wild horse in the rodeo is very near to falling off .",
  "id": "4427058951.jpg"
}

PUT /my-nlp-index/_doc/5
{
  "text": "A rodeo cowboy , wearing a cowboy hat , is being thrown off of a wild white horse .",
  "id": "2691147709.jpg"
}

GET /my-nlp-index/_doc/1

GET /my-nlp-index/_search
{
  "_source": {
    "excludes": [
      "passage_embedding"
    ]
  },
  "query": {
    "match": {
      "text": {
        "query": "wild west"
      }
    }
  }
}