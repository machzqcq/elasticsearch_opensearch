PUT /_cluster/settings
{
    "persistent": {
        "plugins.ml_commons.trusted_connector_endpoints_regex": [
          "^https://runtime\\.sagemaker\\..*[a-z0-9-]\\.amazonaws\\.com/.*$",
          "^https://api\\.openai\\.com/.*$",
          "^https://api\\.cohere\\.ai/.*$",
          "^https://bedrock-runtime\\..*[a-z0-9-]\\.amazonaws\\.com/.*$"
        ]
    }
}

POST /_plugins/_ml/model_groups/_register
{
  "name": "remote_model_group",
  "description": "A model group for external models"
}

POST /_plugins/_ml/connectors/_create
{
    "name": "OpenAI Chat Connector",
    "description": "The connector to public OpenAI model service for GPT 3.5",
    "version": 1,
    "protocol": "http",
    "parameters": {
        "endpoint": "api.openai.com",
        "model": "gpt-3.5-turbo"
    },
    "credential": {
        "openAI_key": "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"
    },
    "actions": [
        {
            "action_type": "predict",
            "method": "POST",
            "url": "https://${parameters.endpoint}/v1/chat/completions",
            "headers": {
                "Authorization": "Bearer ${credential.openAI_key}"
            },
            "request_body": "{ \"model\": \"${parameters.model}\", \"messages\": ${parameters.messages} }"
        }
    ]
}

POST /_plugins/_ml/models/_register
{
    "name": "openAI-gpt-3.5-turbo",
    "function_name": "remote",
    "model_group_id": "jkPXLpIB9TX4z539sp-G",
    "description": "test model",
    "connector_id": "mEPaLpIB9TX4z539A58u"
}

GET /_plugins/_ml/tasks/n0PbLpIB9TX4z539vJ-c

POST /_plugins/_ml/models/oEPbLpIB9TX4z539v58S/_deploy

GET /_plugins/_ml/tasks/v0PiLpIB9TX4z539_5-u

POST /_plugins/_ml/models/oEPbLpIB9TX4z539v58S/_predict
{
  "parameters": {
    "messages": [
      {
        "role": "system",
        "content": "You are a helpful assistant."
      },
      {
        "role": "user",
        "content": "Hello!"
      }
    ]
  }
}

DELETE /_plugins/_ml/model_groups/gkOgL5IB9TX4z539HKLm

POST /_plugins/_ml/models/hUOgL5IB9TX4z539HaKY/_undeploy
GET /_plugins/_ml/models/hUOgL5IB9TX4z539HaKY
DELETE /_plugins/_ml/models/hUOgL5IB9TX4z539HaKY

DELETE /_plugins/_ml/models/

GET /_plugins/_ml/model_groups/8UOFL5IB9TX4z539_6GJ