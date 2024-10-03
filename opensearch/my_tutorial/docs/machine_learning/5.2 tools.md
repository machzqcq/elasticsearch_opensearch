# Tools
## MLModel Tool
The MLModelTool runs a machine learning (ML) model and returns inference results.

### Step 1: Create a connector for a model
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
        "openAI_key": "<openAI_key>"
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

### Step 2: Register and deploy the model

```json
POST /_plugins/_ml/models/_register?deploy=true
{
  "name": "remote-inference",
  "function_name": "remote",
  "description": "test model",
  "connector_id": "eJATWo0BkIylWTeYToTn"
}
```

Response
```json
{
  "task_id": "7X7pWI0Bpc3sThaJ4I8R",
  "status": "CREATED",
  "model_id": "h5AUWo0BkIylWTeYT4SU"
}
```

### Step 3: Register a flow agent that will run the MLModelTool

A flow agent runs a sequence of tools in order and returns the last tool’s output. To create a flow agent, send the following register agent request, providing the model ID in the model_id parameter:

```json
POST /_plugins/_ml/agents/_register
{
  "name": "Test agent for embedding model",
  "type": "flow",
  "description": "this is a test agent",
  "tools": [
    {
      "type": "MLModelTool",
      "description": "A general tool to answer any question",
      "parameters": {
        "model_id": "h5AUWo0BkIylWTeYT4SU",
        "prompt": "\n\nHuman:You are a professional data analyst. You will always answer question based on the given context first. If the answer is not directly shown in the context, you will analyze the data and find the answer. If you don't know the answer, just say don't know. \n\nHuman:${parameters.question}\n\nAssistant:"
      }
    }
  ]
}
```

Response

```json
{
  "agent_id": "9X7xWI0Bpc3sThaJdY9i"
}
```

### Step 4: Run the agent

```json
POST /_plugins/_ml/agents/9X7xWI0Bpc3sThaJdY9i/_execute
{
  "parameters": {
    "question": "what's the population increase of Seattle from 2021 to 2023"
  }
}
```

Results

```json
{
  "inference_results": [
    {
      "output": [
        {
          "name": "response",
          "result": " I do not have direct data on the population increase of Seattle from 2021 to 2023 in the context provided. As a data analyst, I would need to research population statistics from credible sources like the US Census Bureau to analyze population trends and make an informed estimate. Without looking up actual data, I don't have enough information to provide a specific answer to the question."
        }
      ]
    }
  ]
}
```

## AgentTool
The AgentTool runs any agent. So we can chain agents and build complex logic

### Step 1: Set up an agent for AgentTool to run
Set up any agent. For example, set up a flow agent that runs an MLModelTool for e.g.

```json
{
  "agent_id": "9X7xWI0Bpc3sThaJdY9i"
}
```

# Step 2: Register a flow agent that will run the AgentTool
A flow agent runs a sequence of tools in order and returns the last tool’s output. To create a flow agent, send the following register agent request, providing the agent ID from the previous step

```json
POST /_plugins/_ml/agents/_register
{
  "name": "Test agent tool",
  "type": "flow",
  "description": "this is a test agent",
  "tools": [
    {
      "type": "AgentTool",
      "description": "A general agent to answer any question",
      "parameters": {
        "agent_id": "9X7xWI0Bpc3sThaJdY9i"
      }
    }
  ]
}
```
OpenSearch responds with an agent ID:

```json
{
  "agent_id": "EQyyZ40BT2tRrkdmhT7_"
}
```

### Step 3: Run the agent

```json
POST /_plugins/_ml/agents/EQyyZ40BT2tRrkdmhT7_/_execute
{
  "parameters": {
    "question": "what's the population increase of Seattle from 2021 to 2023"
  }
}
```

OpenSearch returns the inference results:
```json
{
  "inference_results": [
    {
      "output": [
        {
          "name": "response",
          "result": " I do not have direct data on the population increase of Seattle from 2021 to 2023 in the context provided. As a data analyst, I would need to research population statistics from credible sources like the US Census Bureau to analyze population trends and make an informed estimate. Without looking up actual data, I don't have enough information to provide a specific answer to the question."
        }
      ]
    }
  ]
}
```

## CAT Index tool
The CatIndexTool retrieves index information for the OpenSearch cluster, similarly to the CAT Indices API.

### Step 1: Register a flow agent that will run the CatIndexTool
A flow agent runs a sequence of tools in order and returns the last tool’s output. To create a flow agent, send the following register agent request:

```json
POST /_plugins/_ml/agents/_register
{
  "name": "Test_Agent_For_CatIndex_tool",
  "type": "flow",
  "description": "this is a test agent for the CatIndexTool",
  "tools": [
    {
      "type": "CatIndexTool",
      "name": "DemoCatIndexTool",
      "parameters": {
        "input": "${parameters.question}"
      }
    }
  ]
}
```

OpenSearch responds with an agent ID:
```
{
  "agent_id": "9X7xWI0Bpc3sThaJdY9i"
}
```

### Step 2: Run the agent
Then, run the agent by sending the following request:

```json
POST /_plugins/_ml/agents/9X7xWI0Bpc3sThaJdY9i/_execute
{
  "parameters": {
    "question": "How many indices do I have?"
  }
}
```

Results
```json
{
  "inference_results": [
    {
      "output": [
        {
          "name": "response",
          "result": """row,health,status,index,uuid,pri(number of primary shards),rep(number of replica shards),docs.count(number of available documents),docs.deleted(number of deleted documents),store.size(store size of primary and replica shards),pri.store.size(store size of primary shards)
1,green,open,.plugins-ml-model-group,0Bv0LlvAQeOct2qnuzHvhg,1,1,6,0,64.5kb,35.9kb
2,green,open,.plugins-ml-config,JAR6yfAURIKaZE1N2ewQGg,1,1,1,0,7.8kb,3.9kb
3,green,open,.opensearch-observability,2m177caWSxWFvcqeOZCyyA,1,1,0,0,416b,208b
4,green,open,security-auditlog-2024.10.03,eNdc8xCkR5GHShcvozhBhg,1,1,138,0,455.6kb,176.4kb
5,green,open,interns,OrCzSM5CQg697INfdrEblw,1,1,3972,0,460mb,230mb
6,green,open,.plugins-ml-model,rfcaRsRfQ5eGbZ0VmfbxUw,1,1,30,0,678.7mb,339.3mb
7,green,open,.plugins-ml-agent,JASRo6ymT3CY59Tawq2J1Q,1,1,2,0,37.6kb,18.8kb
8,green,open,.plugins-ml-task,5Jj-rQBRQiWVU5bZOC_33g,1,1,5,0,110.6kb,55.3kb
9,green,open,.plugins-ml-connector,zFYst94zQMy_oAIL8BDw7w,1,1,2,0,69.4kb,34.7kb
10,green,open,.opendistro_security,n0BgPIU3ReGDx16lJq_n6A,1,1,10,2,155kb,68.7kb
11,green,open,.kibana_1,LLmHM-ZISeSwEjGcWkn18Q,1,1,0,0,416b,208b
"""
        }
      ]
    }
  ]
}
```

## Connector tool
The ConnectorTool uses a connector to call any REST API function. For example, you can use a ConnectorTool to call a Lambda function through its REST API interface

### Step 1: Register a connector with an execute action
The ConnectorTool can only run an execute action within a connector. Before you can create a ConnectorTool, you need to configure a connector and provide an execute action in the actions array. The execute action is used to invoke a function at a REST API endpoint. It is similar to the predict action, which is used to invoke a machine learning (ML) model.

```json
POST _plugins/_ml/connectors/_create
{
  "name": "Lambda connector of simple calculator",
  "description": "Demo connector of lambda function",
  "version": 1,
  "protocol": "aws_sigv4",
  "parameters": {
    "region": "YOUR AWS REGION",
    "service_name": "lambda"
  },
  "credential": {
    "access_key": "YOUR ACCESS KEY",
    "secret_key": "YOUR SECRET KEY",
    "session_token": "YOUR SESSION TOKEN"
  },
  "actions": [
    {
      "action_type": "execute",
      "method": "POST",
      "url": "YOUR LAMBDA FUNCTION URL",
      "headers": {
        "content-type": "application/json"
      },
      "request_body": "{ \"number1\":\"${parameters.number1}\", \"number2\":\"${parameters.number2}\" }"
    }
  ]
}
```

### Step 2: Register a flow agent that will run the ConnectorTool
By default, the ConnectorTool expects the response from the Lambda function to contain a field named response. However, in this example the Lambda function response doesn’t include a response field. To retrieve the result from the result field instead, you need to provide a response_filter, specifying the JSON path to the result field ($.result). Using the response_filter, the ConnectorTool will retrieve the result with the specified JSON path and return it in the response field.

To configure the Lambda function workflow, create a flow agent. A flow agent runs a sequence of tools in order and returns the last tool’s output. To create a flow agent, send the following register agent request, providing the connector ID from the previous step and a response_filter

```json
POST /_plugins/_ml/agents/_register
{
  "name": "Demo agent of Lambda connector",
  "type": "flow",
  "description": "This is a demo agent",
  "app_type": "demo",
  "tools": [
    {
      "type": "ConnectorTool",
      "name": "lambda_function",
      "parameters": {
        "connector_id": "YOUR CONNECTOR ID",
        "response_filter": "$.result"
      }
    }
  ]
}
```
OpenSearch responds with an agent ID:

```
{
  "agent_id": "az1XEJABXWrLmr4miAFj"
}
```

### Step 3: Run the agent
Then, run the agent by sending the following request:

```json
POST /_plugins/_ml/agents/9X7xWI0Bpc3sThaJdY9i/_execute
{
  "parameters": {
    "number1": 2,
    "number2": 3
  }
}
```
OpenSearch returns the output of the Lambda function execution. In the output, the field name is response, and the result field contains the Lambda function result:

```json
{
  "inference_results": [
    {
      "output": [
        {
          "name": "response",
          "result": 5
        }
      ]
    }
  ]
}
```
## Index Mapping tool
The IndexMappingTool retrieves mapping and setting information for indexes in your cluster
### Step 1: Register a flow agent that will run the IndexMappingTool
A flow agent runs a sequence of tools in order and returns the last tool’s output. To create a flow agent, send the following register agent request:

```json
POST /_plugins/_ml/agents/_register
{
  "name": "Test_Agent_For_IndexMapping_tool",
  "type": "flow",
  "description": "this is a test agent for the IndexMappingTool",
  "tools": [
      {
      "type": "IndexMappingTool",
      "name": "DemoIndexMappingTool",
      "parameters": {
        "index": "${parameters.index}",
        "input": "${parameters.question}"
      }
    }
  ]
}
```

### Step 2: Run the agent

```json
POST /_plugins/_ml/agents/aecnU5IBsVzlZAslYYhw/_execute
{
  "parameters": {
    "index": [ "interns" ],
    "question": "What fields are in the sample-ecommerce index?"
  }
}
```

## Neural Sparse Search tool
The NeuralSparseSearchTool performs sparse vector retrieval

### Step 1: Register and deploy a sparse encoding model

```json
POST /_plugins/_ml/models/_register?deploy=true
{
  "name": "amazon/neural-sparse/opensearch-neural-sparse-encoding-v2-distill",
  "version": "1.0.0",
  "model_format": "TORCH_SCRIPT"
}
```
OpenSearch responds with a task ID for the model registration and deployment task:
```
{
  "task_id": "M_9KY40Bk4MTqirc5lP8",
  "status": "CREATED"
}
```

You can monitor the status of the task by calling the Tasks API:

`GET _plugins/_ml/tasks/M_9KY40Bk4MTqirc5lP8`

Once the model is registered and deployed, the task state changes to COMPLETED and OpenSearch returns a model ID for the model:

```json
{
  "model_id": "Nf9KY40Bk4MTqirc6FO7",
  "task_type": "REGISTER_MODEL",
  "function_name": "SPARSE_ENCODING",
  "state": "COMPLETED",
  "worker_node": [
    "UyQSTQ3nTFa3IP6IdFKoug"
  ],
  "create_time": 1706767869692,
  "last_update_time": 1706767935556,
  "is_async": true
}
```
### Step 2: Ingest data into an index
First, you’ll set up an ingest pipeline to encode documents using the sparse encoding model set up in the previous step:

```json
PUT /_ingest/pipeline/pipeline-sparse
{
  "description": "An sparse encoding ingest pipeline",
  "processors": [
    {
      "sparse_encoding": {
        "model_id": "Nf9KY40Bk4MTqirc6FO7",
        "field_map": {
          "passage_text": "passage_embedding"
        }
      }
    }
  ]
}
```

Next, create an index specifying the pipeline as the default pipeline:

```json
PUT index_for_neural_sparse
{
  "settings": {
    "default_pipeline": "pipeline-sparse"
  },
  "mappings": {
    "properties": {
      "passage_embedding": {
        "type": "rank_features"
      },
      "passage_text": {
        "type": "text"
      }
    }
  }
}
```
Last, ingest data into the index by sending a bulk request:
```json
POST _bulk
{ "index" : { "_index" : "index_for_neural_sparse", "_id" : "1" } }
{ "passage_text" : "company AAA has a history of 123 years" }
{ "index" : { "_index" : "index_for_neural_sparse", "_id" : "2" } }
{ "passage_text" : "company AAA has over 7000 employees" }
{ "index" : { "_index" : "index_for_neural_sparse", "_id" : "3" } }
{ "passage_text" : "Jack and Mark established company AAA" }
{ "index" : { "_index" : "index_for_neural_sparse", "_id" : "4" } }
{ "passage_text" : "company AAA has a net profit of 13 millions in 2022" }
{ "index" : { "_index" : "index_for_neural_sparse", "_id" : "5" } }
{ "passage_text" : "company AAA focus on the large language models domain" }
```

### Step 3: Register a flow agent that will run the NeuralSparseSearchTool
A flow agent runs a sequence of tools in order and returns the last tool’s output. To create a flow agent, send the following request, providing the model ID for the model set up in Step 1. This model will encode your queries into sparse vector embeddings

```json
POST /_plugins/_ml/agents/_register
{
  "name": "Test_Neural_Sparse_Agent_For_RAG",
  "type": "flow",
  "tools": [
    {
      "type": "NeuralSparseSearchTool",
      "parameters": {
        "description":"use this tool to search data from the knowledge base of company AAA",
        "model_id": "Nf9KY40Bk4MTqirc6FO7",
        "index": "index_for_neural_sparse",
        "embedding_field": "passage_embedding",
        "source_field": ["passage_text"],
        "input": "${parameters.question}",
        "doc_size":2
      }
    }
  ]
}
```

OpenSearch responds with an agent ID:
```
{
  "agent_id": "9X7xWI0Bpc3sThaJdY9i"
}
```

### Step 4: Run the agent

Then, run the agent by sending the following request:

```json
POST /_plugins/_ml/agents/9X7xWI0Bpc3sThaJdY9i/_execute
{
  "parameters": {
    "question":"how many employees does AAA have?"
  }
}
```

Sample response

```
{
  "inference_results": [
    {
      "output": [
        {
          "name": "response",
          "result": """{"_index":"index_for_neural_sparse","_source":{"passage_text":"company AAA has over 7000 employees"},"_id":"2","_score":41.003227}
{"_index":"index_for_neural_sparse","_source":{"passage_text":"company AAA has a net profit of 13 millions in 2022"},"_id":"4","_score":20.835928}
"""
        }
      ]
    }
  ]
}
```

## PPL tool
PPL (Piped Processing Language) is a query language used in OpenSearch that allows you to query and analyze data using a series of commands connected by pipes (|).

[Read More](https://opensearch.org/docs/latest/ml-commons-plugin/agents-tools/tools/ppl-tool/)

## RAG tool
The RAGTool performs retrieval-augmented generation (RAG)
RAG calls a large language model (LLM) and supplements its knowledge by providing relevant OpenSearch documents along with the user question. To retrieve relevant documents from an OpenSearch index, you’ll need a text embedding model that facilitates vector search.

The RAG tool supports the following search methods:

Neural search: Dense vector retrieval, which uses a text embedding model.
Neural sparse search: Sparse vector retrieval, which uses a sparse encoding model.

### Step 1: Register a flow agent that will run the RAGTool
A flow agent runs a sequence of tools in order and returns the last tool’s output. To create a flow agent, send the following request, providing the text embedding model ID in the embedding_model_id parameter and the LLM model ID in the inference_model_id parameter

```json
POST /_plugins/_ml/agents/_register
{
  "name": "Test_Agent_For_RagTool",
  "type": "flow",
  "description": "this is a test flow agent",
  "tools": [
  {
    "type": "RAGTool",
    "description": "A description of the tool",
    "parameters": {
      "embedding_model_id": "Hv_PY40Bk4MTqircAVmm",
      "inference_model_id": "SNzSY40B_1JGmyB0WbfI",
      "index": "my_test_data",
      "embedding_field": "embedding",
      "query_type": "neural",
      "source_field": [
        "text"
      ],
      "input": "${parameters.question}",
      "prompt": "\n\nHuman:You are a professional data analyst. You will always answer question based on the given context first. If the answer is not directly shown in the context, you will analyze the data and find the answer. If you don't know the answer, just say don't know. \n\n Context:\n${parameters.output_field}\n\nHuman:${parameters.question}\n\nAssistant:"
    }
  }
]
}
```

OpenSearch responds with an agent ID:
```
{
  "agent_id": "9X7xWI0Bpc3sThaJdY9i"
}
```

### Step 2: Run the agent

```json
POST /_plugins/_ml/agents/9X7xWI0Bpc3sThaJdY9i/_execute
{
  "parameters": {
    "question": "what's the population increase of Seattle from 2021 to 2023"
  }
}
```

## Search Alerts tool

[Read here](https://opensearch.org/docs/latest/ml-commons-plugin/agents-tools/tools/search-alerts-tool/)


### AnomalyDetectorTools
- Experimental Feature as of 10/3/2024
- [Create Anomaly Detector Tool](https://opensearch.org/docs/latest/ml-commons-plugin/agents-tools/tools/create-anomaly-detector/)
- [Read more](https://opensearch.org/docs/latest/ml-commons-plugin/agents-tools/tools/create-anomaly-detector/)
- [Search Anomaly Detector Tools on your cluster](https://opensearch.org/docs/latest/ml-commons-plugin/agents-tools/tools/search-anomaly-detectors/)
- [Search Anomaly Results](https://opensearch.org/docs/latest/ml-commons-plugin/agents-tools/tools/search-anomaly-results/)

## Search
- [Search Index Tool](https://opensearch.org/docs/latest/ml-commons-plugin/agents-tools/tools/search-index-tool/)
- [Search Monitors Tool](https://opensearch.org/docs/latest/ml-commons-plugin/agents-tools/tools/search-monitors-tool/)

## Vector DB tool
The VectorDBTool performs dense vector retrieval

### Step 1: Register and deploy a sparse encoding model

```json
POST /_plugins/_ml/models/_register?deploy=true
{
  "name": "huggingface/sentence-transformers/all-MiniLM-L12-v2",
  "version": "1.0.1",
  "model_format": "TORCH_SCRIPT"
}
```
OpenSearch responds with a task ID for the model registration and deployment task:
```
{
  "task_id": "M_9KY40Bk4MTqirc5lP8",
  "status": "CREATED"
}
```

You can monitor the status of the task by calling the Tasks API:

`GET _plugins/_ml/tasks/M_9KY40Bk4MTqirc5lP8`

### Step 2: Ingest data into an index

```json
PUT /_ingest/pipeline/test-pipeline-local-model
{
  "description": "text embedding pipeline",
  "processors": [
    {
      "text_embedding": {
        "model_id": "Hv_PY40Bk4MTqircAVmm",
        "field_map": {
          "text": "embedding"
        }
      }
    }
  ]
}
```

Next, create a k-NN index specifying the pipeline as the default pipeline:


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

Last, ingest data into the index by sending a bulk request:

```
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

### Step 3: Register a flow agent that will run the VectorDBTool
A flow agent runs a sequence of tools in order and returns the last tool’s output. To create a flow agent, send the following request, providing the model ID for the model set up in Step 1. This model will encode your queries into vector embeddings:

```
POST /_plugins/_ml/agents/_register
{
  "name": "Test_Agent_For_VectorDB",
  "type": "flow",
  "description": "this is a test agent",
  "tools": [
    {
      "type": "VectorDBTool",
      "parameters": {
        "model_id": "Hv_PY40Bk4MTqircAVmm",
        "index": "my_test_data",
        "embedding_field": "embedding",
        "source_field": ["text"],
        "input": "${parameters.question}"
      }
    }
  ]
}
```

OpenSearch responds with an agent ID:
```
{
  "agent_id": "9X7xWI0Bpc3sThaJdY9i"
}
```

### Step 4: Run the agent
```json
POST /_plugins/_ml/agents/9X7xWI0Bpc3sThaJdY9i/_execute
{
  "parameters": {
    "question": "what's the population increase of Seattle from 2021 to 2023"
  }
}
```

## Visualization tool
Use the VisualizationTool to find visualizations relevant to a question

### Step 1: Register a flow agent that will run the VisualizationTool
A flow agent runs a sequence of tools in order and returns the last tool’s output. To create a flow agent, send the following register agent request:

```json
POST /_plugins/_ml/agents/_register
{
  "name": "Test_Agent_For_Visualization_tool",
  "type": "flow",
  "description": "this is a test agent for the VisuailizationTool",
  "tools": [
      {
      "type": "VisualizationTool",
      "name": "DemoVisualizationTool",
      "parameters": {
        "index": ".kibana",
        "input": "${parameters.question}",
        "size": 3
      }
    }
  ]
}
```
OpenSearch responds with an agent ID:
```
{
  "agent_id": "9X7xWI0Bpc3sThaJdY9i"
}
```

### Step 2: Run the agent
```json
POST /_plugins/_ml/agents/9X7xWI0Bpc3sThaJdY9i/_execute
{
  "parameters": {
    "question": "what's the revenue for today?"
  }
}
```

By default, OpenSearch returns the top three matching visualizations. You can use the size parameter to specify the number of results returned. The output is returned in CSV format. The output includes two columns: Title (the visualization title displayed in OpenSearch Dashboards) and Id (a unique ID for this visualization):

```json
{
  "inference_results": [
    {
      "output": [
        {
          "name": "response",
          "result": """Title,Id
[eCommerce] Total Revenue,10f1a240-b891-11e8-a6d9-e546fe2bba5f
"""
        }
      ]
    }
  ]
}
```










