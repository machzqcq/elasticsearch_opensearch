# Clustering Setting prequisite
PUT _cluster/settings
{
  "persistent": {
    "plugins": {
      "ml_commons": {
        "allow_registering_model_via_url": "true",
        "only_run_on_ml_node": "false",
        "model_access_control_enabled": "true",
        "native_memory_threshold": "99"
      }
    }
  }
}

# Create stop words index
PUT /words0
{
  "mappings": {
    "properties": {
      "title": {
        "type": "text"
      },
      "query": {
        "type": "percolator"
      }
    }
  }
}

# Create stop words
PUT /words0/_doc/1?refresh
{
  "query": {
    "query_string": {
      "query": "title: blacklist"
    }
  }
}

# Create stop words
PUT /words0/_doc/2?refresh
{
  "query": {
    "query_string": {
      "query": "title: \"Master slave architecture\""
    }
  }
}

# Create model group
POST /_plugins/_ml/model_groups/_register
{
  "name": "remote_model_group",
  "description": "A model group for external models"
}

# Create connecter - for chat model
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

# Register and deploy model
POST /_plugins/_ml/models/_register?deploy=true
{
  "name": "Open ai ",
  "function_name": "remote",
  "model_group_id": "qnbRSZIBASYct40ubLgA",
  "description": "test model",
  "connector_id": "rnbRSZIBASYct40u47iK",
  "guardrails": {
    "type": "local_regex",
    "input_guardrail": {
      "stop_words": [
        {
          "index_name": "words0",
          "source_fields": [
            "title"
          ]
        }
      ],
      "regex": [
        ".*abort.*",
        ".*kill.*"
      ]
    },
    "output_guardrail": {
      "stop_words": [
        {
          "index_name": "words0",
          "source_fields": [
            "title"
          ]
        }
      ],
      "regex": [
        ".*abort.*",
        ".*kill.*"
      ]
    }
  }
}

# Monitor the task until COMPLETED
GET /_plugins/_ml/tasks/tXbTSZIBASYct40uUrhz

# Predict - positive expected result
POST /_plugins/_ml/models/tnbTSZIBASYct40uVbgh/_predict
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

# Predict - negative expected result
POST /_plugins/_ml/models/tnbTSZIBASYct40uVbgh/_predict
{
  "parameters": {
    "messages": [
      {
        "role": "system",
        "content": "You are a helpful assistant."
      },
      {
        "role": "user",
        "content": "How to kill a chicken"
      }
    ]
  }
}

# Predict - negative expected result
POST /_plugins/_ml/models/tnbTSZIBASYct40uVbgh/_predict
{
  "parameters": {
    "messages": [
      {
        "role": "system",
        "content": "You are a helpful assistant."
      },
      {
        "role": "user",
        "content": "Test for master slave architecture"
      }
    ]
  }
}