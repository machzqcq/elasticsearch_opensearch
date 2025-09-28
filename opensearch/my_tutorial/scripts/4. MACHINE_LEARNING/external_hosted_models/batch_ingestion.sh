POST /_plugins/_ml/model_groups/_register
{
  "name": "remote_model_group",
  "description": "A model group for external models"
}


POST /_plugins/_ml/connectors/_create
{
  "name": "openai_connector",
  "description": "Connector for OpenAI API",
  "version": 1,
  "protocol": "http",
  "parameters": {
    "endpoint": "api.openai.com",
    "model": "text-embedding-ada-002"
  },
  "credential": {
    "openAI_key": "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"
  },
  "actions": [
    {
      "action_type": "predict",
      "method": "POST",
      "url": "https://${parameters.endpoint}/v1/embeddings",
      "headers": {
        "Authorization": "Bearer ${credential.openAI_key}"
      },
      "request_body": """{ "input": ${parameters.input}, "model": "${parameters.model}" }""",
      "pre_process_function": "connector.pre_process.openai.embedding",
      "post_process_function": "connector.post_process.openai.embedding"
    }
  ]
}


POST /_plugins/_ml/models/_register
{
    "name": "openAI-gpt-3.5-turbo",
    "function_name": "remote",
    "model_group_id": "QqOjSpIB9XVjosYGow7b",
    "description": "test model",
    "connector_id": "x6O-SpIB9XVjosYGhA4x"
}

POST /_plugins/_ml/models/zKO-SpIB9XVjosYG8g42/_deploy

GET /_plugins/_ml/tasks/y6O-SpIB9XVjosYG8Q6-

# Starting in OpenSearch version 2.13, externally hosted models are deployed automatically when you send a Predict API request for the first time. To disable automatic deployment for an externally hosted model, set plugins.ml_commons.model_auto_deploy.enable to false:
PUT _cluster/settings
{
  "persistent": {
    "plugins.ml_commons.model_auto_deploy.enable" : "false"
  }
}

PUT /_ingest/pipeline/nlp-ingest-pipeline2
{
  "description": "A text embedding pipeline",
  "processors": [
    {
      "text_embedding": {
        "model_id": "zKO-SpIB9XVjosYG8g42",
        "field_map": {
          "passage_text": "passage_embedding"
        },
        "batch_size": 5
      }
    }
  ]
}

PUT testindex

POST _bulk?batch_size=5&pipeline=nlp-ingest-pipeline2
{ "create": { "_index": "testindex", "_id": "2" } }
{ "passage_text": "hello world" }
{ "create": { "_index": "testindex", "_id": "3" } }
{ "passage_text": "big apple" }
{ "create": { "_index": "testindex", "_id": "4" } }
{ "passage_text": "golden gate bridge" }
{ "create": { "_index": "testindex", "_id": "5" } }
{ "passage_text": "fine tune" }
{ "create": { "_index": "testindex", "_id": "6" } }
{ "passage_text": "random test" }
{ "create": { "_index": "testindex", "_id": "7" } }
{ "passage_text": "sun and moon" }
{ "create": { "_index": "testindex", "_id": "8" } }
{ "passage_text": "windy" }
{ "create": { "_index": "testindex", "_id": "9" } }
{ "passage_text": "new york" }
{ "create": { "_index": "testindex", "_id": "10" } }
{ "passage_text": "fantastic" }



GET testindex/_search
{
   "query" : {
      "match_all": {}
   }
}