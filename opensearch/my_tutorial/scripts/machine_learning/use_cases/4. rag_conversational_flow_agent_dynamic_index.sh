
PUT _cluster/settings
{
  "persistent": {
    "plugins.ml_commons.only_run_on_ml_node": "false",
    "plugins.ml_commons.native_memory_threshold": 100,
    "plugins.ml_commons.memory_feature_enabled": "true"
  }
}

POST /_plugins/_ml/models/_register?deploy=true
{
  "name": "huggingface/sentence-transformers/all-MiniLM-L12-v2",
  "version": "1.0.1",
  "model_format": "TORCH_SCRIPT"
}

GET /_plugins/_ml/tasks/bBLwY5IBe067QSVzv_h4


PUT /_ingest/pipeline/test-pipeline-local-model
{
  "description": "text embedding pipeline",
  "processors": [
    {
      "text_embedding": {
        "model_id": "cBLwY5IBe067QSVzxPjH",
        "field_map": {
          "text": "embedding"
        }
      }
    }
  ]
}


PUT my_test_data
{
  "mappings": {
    "properties": {
      "text": {
        "type": "text"
      },
      "embedding": {
        "type": "knn_vector",
        "dimension": 384,
        "method": {
          "name": "hnsw",
          "space_type": "l2",
          "engine": "lucene"
        }
      }
    }
  },
  "settings": {
    "index": {
      "knn.space_type": "cosinesimil",
      "default_pipeline": "test-pipeline-local-model",
      "knn": "true"
    }
  }
}

POST _bulk
{"index": {"_index": "my_test_data", "_id": "1"}}
{"text": "Chart and table of population level and growth rate for the Ogden-Layton metro area from 1950 to 2023. United Nations population projections are also included through the year 2035.\nThe current metro area population of Ogden-Layton in 2023 is 750,000, a 1.63% increase from 2022.\nThe metro area population of Ogden-Layton in 2022 was 738,000, a 1.79% increase from 2021.\nThe metro area population of Ogden-Layton in 2021 was 725,000, a 1.97% increase from 2020.\nThe metro area population of Ogden-Layton in 2020 was 711,000, a 2.16% increase from 2019."}
{"index": {"_index": "my_test_data", "_id": "2"}}
{"text": "Chart and table of population level and growth rate for the New York City metro area from 1950 to 2023. United Nations population projections are also included through the year 2035.\\nThe current metro area population of New York City in 2023 is 18,937,000, a 0.37% increase from 2022.\\nThe metro area population of New York City in 2022 was 18,867,000, a 0.23% increase from 2021.\\nThe metro area population of New York City in 2021 was 18,823,000, a 0.1% increase from 2020.\\nThe metro area population of New York City in 2020 was 18,804,000, a 0.01% decline from 2019."}
{"index": {"_index": "my_test_data", "_id": "3"}}
{"text": "Chart and table of population level and growth rate for the Chicago metro area from 1950 to 2023. United Nations population projections are also included through the year 2035.\\nThe current metro area population of Chicago in 2023 is 8,937,000, a 0.4% increase from 2022.\\nThe metro area population of Chicago in 2022 was 8,901,000, a 0.27% increase from 2021.\\nThe metro area population of Chicago in 2021 was 8,877,000, a 0.14% increase from 2020.\\nThe metro area population of Chicago in 2020 was 8,865,000, a 0.03% increase from 2019."}
{"index": {"_index": "my_test_data", "_id": "4"}}
{"text": "Chart and table of population level and growth rate for the Miami metro area from 1950 to 2023. United Nations population projections are also included through the year 2035.\\nThe current metro area population of Miami in 2023 is 6,265,000, a 0.8% increase from 2022.\\nThe metro area population of Miami in 2022 was 6,215,000, a 0.78% increase from 2021.\\nThe metro area population of Miami in 2021 was 6,167,000, a 0.74% increase from 2020.\\nThe metro area population of Miami in 2020 was 6,122,000, a 0.71% increase from 2019."}
{"index": {"_index": "my_test_data", "_id": "5"}}
{"text": "Chart and table of population level and growth rate for the Austin metro area from 1950 to 2023. United Nations population projections are also included through the year 2035.\\nThe current metro area population of Austin in 2023 is 2,228,000, a 2.39% increase from 2022.\\nThe metro area population of Austin in 2022 was 2,176,000, a 2.79% increase from 2021.\\nThe metro area population of Austin in 2021 was 2,117,000, a 3.12% increase from 2020.\\nThe metro area population of Austin in 2020 was 2,053,000, a 3.43% increase from 2019."}
{"index": {"_index": "my_test_data", "_id": "6"}}
{"text": "Chart and table of population level and growth rate for the Seattle metro area from 1950 to 2023. United Nations population projections are also included through the year 2035.\\nThe current metro area population of Seattle in 2023 is 3,519,000, a 0.86% increase from 2022.\\nThe metro area population of Seattle in 2022 was 3,489,000, a 0.81% increase from 2021.\\nThe metro area population of Seattle in 2021 was 3,461,000, a 0.82% increase from 2020.\\nThe metro area population of Seattle in 2020 was 3,433,000, a 0.79% increase from 2019."}



POST /_plugins/_ml/model_groups/_register
{
  "name": "openai_model_group",
  "description": "A model group for open ai models"
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

POST /_plugins/_ml/models/_register?deploy=true
{
    "name": "openAI-gpt-3.5-turbo",
    "function_name": "remote",
    "model_group_id": "jxLzY5IBe067QSVzNPiM",
    "description": "test model",
    "connector_id": "kxLzY5IBe067QSVz2fhr"
}

GET /_plugins/_ml/tasks/lxL0Y5IBe067QSVzGPht


POST /_plugins/_ml/models/mBL0Y5IBe067QSVzGPjU/_predict
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

POST /_plugins/_ml/agents/_register
{
    "name": "population data analysis agent",
    "type": "conversational_flow",
    "description": "This is a demo agent for population data analysis",
    "app_type": "rag",
    "memory": {
        "type": "conversation_index"
    },
    "tools": [
        {
            "type": "SearchIndexTool",
            "parameters": {
                "input": "{\"index\": \"${parameters.index}\", \"query\": ${parameters.query} }"
            }
        },
        {
            "type": "MLModelTool",
            "description": "A general tool to answer any question",
            "parameters": {
                "model_id": "mBL0Y5IBe067QSVzGPjU",
                "messages": [
                    {
                        "role": "system",
                        "content": "You are a professional data analyst. You will always answer a question based on the given context first. If the answer is not directly shown in the context, you will analyze the data and find the answer. If you don't know the answer, just say you don't know."
                    },
                    {
                        "role": "user",
                        "content": "Context:\n${parameters.SearchIndexTool.output:-}\n\nQuestion:${parameters.question}\n\n"
                    }
                ]
            }
        }
    ]
}


POST /_plugins/_ml/agents/phL2Y5IBe067QSVzl_i2/_execute
{
    "parameters": {
        "question": "what's the population increase of Seattle from 2021 to 2023?",
        "index": "my_test_data",
        "query": {
            "query": {
                "match": {
                    "text": "${parameters.question}"
                }
            },
            "size": 2,
            "_source": "text"
        }
    }
}
