# Agents and tools tutorial
The following tutorial illustrates creating a flow agent for retrieval-augmented generation (RAG). A flow agent runs its configured tools sequentially, in the order specified. In this example, you’ll create an agent with two tools:

**VectorDBTool**: The agent will use this tool to retrieve OpenSearch documents relevant to the user question. You’ll ingest supplementary information into an OpenSearch index. To facilitate vector search, you’ll deploy a text embedding model that translates text into vector embeddings. OpenSearch will translate the ingested documents into embeddings and store them in the index. When you provide a user question to the agent, the agent will construct a query from the question, run vector search on the OpenSearch index, and pass the relevant retrieved documents to the MLModelTool.
**MLModelTool**: The agent will run this tool to connect to a large language model (LLM) and send the user query augmented with OpenSearch documents to the model. In this example, you’ll use the OpenAI chat model. The LLM will then answer the question based on its knowledge and the provided documents.

## Prerequisites
To use the memory feature, first configure the following cluster settings

```json
PUT _cluster/settings
{
  "persistent": {
    "plugins.ml_commons.only_run_on_ml_node": "false",
    "plugins.ml_commons.memory_feature_enabled": "true"
  }
}
```

## Step 1: Register and deploy a text embedding model
You need a text embedding model to facilitate vector search. For this tutorial, you’ll use one of the OpenSearch-provided pretrained models. When selecting a model, **note its dimensionality** because you’ll need to provide it when creating an index. In this tutorial, you’ll use the huggingface/sentence-transformers/all-MiniLM-L12-v2 model, which generates 384-dimensional dense vector embeddings

```json
POST /_plugins/_ml/models/_register?deploy=true
{
  "name": "huggingface/sentence-transformers/all-MiniLM-L12-v2",
  "version": "1.0.1",
  "model_format": "TORCH_SCRIPT"
}
```

### Monitor the task until status is COMPLETED
```json
GET /_plugins/_ml/tasks/aFeif4oB5Vm0Tdw8yoN7
```

### Note the model_id from the response
```json
{
  "model_id": "aVeif4oB5Vm0Tdw8zYO2",
  "task_type": "REGISTER_MODEL",
  "function_name": "TEXT_EMBEDDING",
  "state": "COMPLETED",
  "worker_node": [
    "4p6FVOmJRtu3wehDD74hzQ"
  ],
  "create_time": 1694358489722,
  "last_update_time": 1694358499139,
  "is_async": true
}
```

## Step 2: Create an ingest pipeline
To translate text into vector embeddings, you’ll set up an ingest pipeline. The pipeline translates the text field and writes the resulting vector embeddings into the embedding field. Create the pipeline by specifying the model_id from the previous step in the following request

```json
PUT /_ingest/pipeline/test-pipeline-local-model
{
  "description": "text embedding pipeline",
  "processors": [
    {
      "text_embedding": {
        "model_id": "aVeif4oB5Vm0Tdw8zYO2",
        "field_map": {
          "text": "embedding"
        }
      }
    }
  ]
}
```

## Step 3: Create a k-NN index and ingest data
Now you’ll ingest supplementary data into an OpenSearch index. In OpenSearch, vectors are stored in a k-NN index. You can create a k-NN index by sending the following request

```json
PUT my_test_data
{
  "mappings": {
    "properties": {
      "text": {
        "type": "text"
      },
      "embedding": {
        "type": "knn_vector",
        "dimension": 384
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
```

### bulk ingest
```json
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
```

## Step 4: Create a connector to an externally hosted model
You’ll need an LLM to generate responses to user questions. An LLM is too large for an OpenSearch cluster, so you’ll create a connection to an externally hosted LLM.

```json
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
```
### Note the connector_id in response
```json
{
  "connector_id": "a1eMb4kBJ1eYAeTMAljY"
}
```

## Step 5: Register and deploy the externally hosted model
Like the text embedding model, an LLM needs to be registered and deployed to OpenSearch

```json
POST /_plugins/_ml/model_groups/_register
{
  "name": "openai_model_group",
  "description": "A model group for open ai models"
}
```

### Note the model_group_id
```json
{
 "model_group_id": "wlcnb4kBJ1eYAeTMHlV6",
 "status": "CREATED"
}
```

### Register the model
Using model_group_id and connector_id from previous steps, register the model

```json
POST /_plugins/_ml/models/_register?deploy=true
{
    "name": "openAI-gpt-3.5-turbo",
    "function_name": "remote",
    "model_group_id": "JUa0TZIBH2qLnqOGgrfx",
    "description": "test model",
    "connector_id": "LEa1TZIBH2qLnqOG-rfb"
}
```

### Monitor the task_id from response until COMPLETED
```json
GET /_plugins/_ml/tasks/OUa5TZIBH2qLnqOGObft
```

### Test the model
Response should come back and stop  

```json
POST /_plugins/_ml/models/Oka5TZIBH2qLnqOGOrdr/_predict
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
```

## Step 6: Register and execute an agent
Finally, you’ll use the text embedding model created in Step 1 and the Claude model created in Step 5 to create a flow agent. This flow agent will run a VectorDBTool and then an MLModelTool. The VectorDBTool is configured with the model ID for the text embedding model created in Step 1 for vector search. The MLModelTool is configured with the Claude model created in step 5

```json
POST /_plugins/_ml/agents/_register
{
  "name": "Test_Agent_For_RAG",
  "type": "flow",
  "description": "this is a test agent",
  "tools": [
    {
      "type": "VectorDBTool",
      "parameters": {
        "model_id": "JoOnTZIB0ZlO6yHYy_Oy",
        "index": "my_test_data",
        "embedding_field": "embedding",
        "source_field": [
          "text"
        ],
        "input": "${parameters.question}"
      }
    },
    {
      "type": "MLModelTool",
      "description": "A general tool to answer any question",
      "parameters": {
        "model_id": "Oka5TZIBH2qLnqOGOrdr",
        "messages": [
          {
            "role": "system",
            "content": "You are a professional data analyst. You will always answer a question based on the given context first. If the answer is not directly shown in the context, you will analyze the data and find the answer. If you don't know the answer, just say you don't know."
          },
          {
            "role": "user",
            "content": "Context:\n${parameters.VectorDBTool.output}\n\nQuestion:${parameters.question}\n\n"
          }
        ]
      }
    }
  ]
}
```

### Note the agent_id and get more details
```json
{
  "agent_id": "879v9YwBjWKCe6Kg12Tx"
}
```

```
GET /_plugins/_ml/agents/879v9YwBjWKCe6Kg12Tx
```

### Execute the Agent
```json
POST /_plugins/_ml/agents/879v9YwBjWKCe6Kg12Tx/_execute
{
  "parameters": {
    "question": "what's the population increase of Seattle from 2021 to 2023"
  }
}
```

### Response from OpenAI
```json
{
  "inference_results": [
    {
      "output": [
        {
          "name": "MLModelTool",
          "result": """{"id":"chatcmpl-ADvING0AgRu8zo8TQKiQjeDu1XAhH","object":"chat.completion","created":1.727881871E9,"model":"gpt-3.5-turbo-0125","choices":[{"index":0.0,"message":{"role":"assistant","content":"To calculate the population increase of Seattle from 2021 to 2023, you can subtract the population of Seattle in 2021 from the population of Seattle in 2023.\n\nPopulation of Seattle in 2023 \u003d 3,519,000\nPopulation of Seattle in 2021 \u003d 3,461,000\n\nPopulation increase \u003d Population of Seattle in 2023 - Population of Seattle in 2021\nPopulation increase \u003d 3,519,000 - 3,461,000\nPopulation increase \u003d 58,000\n\nTherefore, the population of Seattle increased by 58,000 from 2021 to 2023."},"finish_reason":"stop"}],"usage":{"prompt_tokens":482.0,"completion_tokens":132.0,"total_tokens":614.0,"prompt_tokens_details":{"cached_tokens":0.0},"completion_tokens_details":{"reasoning_tokens":0.0}}}"""
        }
      ]
    }
  ]
}
```

