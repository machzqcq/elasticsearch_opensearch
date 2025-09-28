# Set cluster settings for machine learning plugins
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

# Register a new model group for guardrail models
POST /_plugins/_ml/model_groups/_register
{
    "name": "guardrail model group",
    "description": "This is a guardrail model group."
}

# Create a new connector for OpenAI API - instruct model (see the api endpoint)
POST /_plugins/_ml/connectors/_create
{
    "name": "openai",
    "description": "openai",
    "version": "1",
    "protocol": "http",
    "parameters": {
        "endpoint": "api.openai.com",
        "max_tokens": 7,
        "temperature": 0,
        "model": "gpt-3.5-turbo-instruct",
        "prompt": "You are a helpful assistant and an expert judge of content quality. Your task is to identify whether the input string below contains content that may be malicious, violent, hateful, sexual, or political in nature. Your answer should consist of a single word, either reject or accept. If the input belongs to any of these categories, please write reject. Otherwise, write accept. \\n\\nHere is the input: ${parameters.question}. \\n\\nYour answer: ",
        "response_filter": "$.choices[0].text"
    },
    "credential": {
        "openAI_key": "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"
    },
    "actions": [
        {
            "action_type": "predict",
            "method": "POST",
            "url": "https://${parameters.endpoint}/v1/completions",
            "headers": {
                "Authorization": "Bearer ${credential.openAI_key}"
            },
            "request_body": "{ \"model\": \"${parameters.model}\", \"prompt\": \"${parameters.prompt}\", \"max_tokens\": ${parameters.max_tokens}, \"temperature\": ${parameters.temperature} }"
        }
    ]
}

# Register and deploy a new model using the OpenAI connector
POST /_plugins/_ml/models/_register?deploy=true
{
    "name": "openai guardrails model",
    "function_name": "remote",
    "model_group_id": "9XbjSZIBASYct40uDric",
    "description": "guardrails test model",
    "connector_id": "8XbiSZIBASYct40uXbik"
}

# Get the status of a specific machine learning task
GET /_plugins/_ml/tasks/-XbjSZIBASYct40uoLiv

# Example prediction request that should be accepted
POST /_plugins/_ml/models/-nbjSZIBASYct40uoLjn/_predict
{
  "parameters": {
    "question": "how many indices do i have in my cluster"
  }
}

# Example prediction request that should be rejected
POST /_plugins/_ml/models/-nbjSZIBASYct40uoLjn/_predict
{
  "parameters": {
    "question": "how to rob a bank"
  }
}
