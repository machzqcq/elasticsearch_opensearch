#!/bin/bash

# Wait for OpenSearch to be ready
until curl -k -s https://opensearch-node1:9200 -u admin:Padmasini10 > /dev/null; do
    echo "Waiting for OpenSearch to start..."
    sleep 5
done

echo "OpenSearch is up and running!"

# Register model group
echo "Registering model group..."
MODEL_GROUP_ID=$(curl -k -s -X POST "https://opensearch-node1:9200/_plugins/_ml/model_groups/_register" -H 'Content-Type: application/json' -u admin:Padmasini10 -d'
{
  "name": "my_model_group",
  "description": "My model group for text embedding",
  "access_mode": "public"
}' | jq -r '.model_group_id')

echo "Model Group ID: $MODEL_GROUP_ID"

# Sleep for 5 seconds
echo "Sleeping for 5 seconds..."
sleep 5

# Register the model
echo "Registering the model..."
RESPONSE=$(curl -k -s -X POST "https://opensearch-node1:9200/_plugins/_ml/models/_register" -H 'Content-Type: application/json' -u admin:Padmasini10 -d'{
    "name": "huggingface/sentence-transformers/msmarco-distilbert-base-tas-b",
    "version": "1.0.1",
    "model_group_id": "'"$MODEL_GROUP_ID"'",
    "model_format": "TORCH_SCRIPT",
    "description": "Sentence transformer model for embeddings"
}')
echo $RESPONSE
MODEL_ID=$(echo $RESPONSE | jq -r '.model_id')
REGISTER_TASK_ID=$(echo $RESPONSE | jq -r '.task_id')

echo "Model ID: $MODEL_ID"
echo "Task ID: $REGISTER_TASK_ID"

# Wait for the model registration to complete
echo "Waiting for model registration to complete..."
until [[ "$(curl -k -s -X GET "https://opensearch-node1:9200/_plugins/_ml/tasks/$REGISTER_TASK_ID" -H 'Content-Type: application/json' -u admin:Padmasini10 | jq -r '.state')" == "COMPLETED" ]]; do
    STATE=$(curl -k -s -X GET "https://opensearch-node1:9200/_plugins/_ml/tasks/$REGISTER_TASK_ID" -H 'Content-Type: application/json' -u admin:Padmasini10 | jq -r '.state')
    echo "Model Group ID: $MODEL_GROUP_ID"
    echo "Model ID: $MODEL_ID"
    echo "Register Task ID: $REGISTER_TASK_ID"
    echo "Current state: $STATE"
    echo "Model registration in progress..."
    sleep 5
done

echo "Model registration completed!"

# Deploy the model
echo "Deploying the model..."
DEPLOY_RESPONSE=$(curl -k -s -X POST "https://opensearch-node1:9200/_plugins/_ml/models/$MODEL_ID/_deploy" -H 'Content-Type: application/json' -u "admin:Padmasini10")
DEPLOY_TASK_ID=$(echo $DEPLOY_RESPONSE | jq -r '.task_id')

echo "Deploy Task ID: $DEPLOY_TASK_ID"

# Wait for the model deployment to complete
echo "Waiting for model deployment to complete..."
until [[ "$(curl -k -s -X GET "https://opensearch-node1:9200/_plugins/_ml/tasks/$DEPLOY_TASK_ID" -H 'Content-Type: application/json' -u "admin:Padmasini10" | jq -r '.state')" == "DEPLOYED" ]]; do
    echo "Model deployment in progress..."
    sleep 5
done

echo "Model deployment completed!"

# Create ingest pipeline
echo "Creating ingest pipeline..."
curl -k -X PUT "https://opensearch-node1:9200/_ingest/pipeline/my_embedding_pipeline" -H 'Content-Type: application/json' -u "admin:Padmasini10" -d'{
  "description": "Text embedding pipeline",
  "processors": [
    {
      "text_embedding": {
        "model_id": "'"$MODEL_ID"'",
        "field_map": {
          "text_field": "embedding_vector"
        }
      }
    }
  ]
}'

# Create kNN index
echo "Creating kNN index..."
curl -k -X PUT "https://opensearch-node1:9200/my_index" -H 'Content-Type: application/json' -u "admin:Padmasini10" -d'{
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
          "engine": "lucene"
        }
      }
    }
  }
}'

# Index sample data
echo "Indexing sample data..."
curl -k -X POST "https://opensearch-node1:9200/my_index/_doc" -H 'Content-Type: application/json' -u "admin:Padmasini10" -d'{
  "text_field": "This is a sample text for embedding"
}'

echo "Setup complete!"