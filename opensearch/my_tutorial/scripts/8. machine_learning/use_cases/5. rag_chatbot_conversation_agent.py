from opensearchpy import OpenSearch, RequestsHttpConnection, helpers
import time, os
from dotenv import load_dotenv
import sys

sys.path.append("../../")
from helpers import restore_interns_all_snapshot

# suppress warnings
import warnings

warnings.filterwarnings("ignore")

# 1. Load environment variables from .env file
load_dotenv("../../.env")

# 2. Retrieve the OpenAI API key from environment variables
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Initialize the OpenSearch client
os_client = OpenSearch(
    hosts=[{"host": "192.168.0.111", "port": 9200}],
    http_auth=("admin", "Developer@123"),  # Replace with your credentials
    use_ssl=True,
    verify_certs=False,
    connection_class=RequestsHttpConnection,
)

# Cluster settings
os_client.cluster.put_settings(
    body={
        "persistent": {
            "plugins.ml_commons.only_run_on_ml_node": "false",
            "plugins.ml_commons.native_memory_threshold": 100,
            "plugins.ml_commons.memory_feature_enabled": "true",
        }
    }
)

# Register model
register_response = os_client.transport.perform_request(
    "POST",
    "/_plugins/_ml/models/_register",
    body={
        "name": "huggingface/sentence-transformers/all-MiniLM-L12-v2",
        "version": "1.0.1",
        "model_format": "TORCH_SCRIPT",
    },
)

# Wait for 3 seconds
time.sleep(3)

# Extract task_id from the response
register_task_id = register_response["task_id"]


# Monitor task status
while True:
    task_status = os_client.transport.perform_request(
        "GET", f"/_plugins/_ml/tasks/{register_task_id}"
    )
    if task_status["state"] == "COMPLETED":
        # Extract model_id from the response
        embedding_model_id = task_status["model_id"]
        break
    time.sleep(5)

print(f"Model ID: {embedding_model_id}")

# Deploy the model
deploy_response = os_client.transport.perform_request(
    method="POST", url=f"/_plugins/_ml/models/{embedding_model_id}/_deploy"
)
print(deploy_response)


# Extract deployment task_id from the response
deploy_task_id = deploy_response["task_id"]

# Wait until the deployment status becomes completed
while True:
    deployment_status = os_client.transport.perform_request(
        method="GET", url=f"/_plugins/_ml/tasks/{deploy_task_id}"
    )
    print(deployment_status)
    if deployment_status["state"] == "COMPLETED":
        break
    time.sleep(10)  # Wait for 10 seconds before checking again

# Create ingest pipeline
ingest_pipeline_response = os_client.ingest.put_pipeline(
    id="test-pipeline-local-model",
    body={
        "description": "text embedding pipeline",
        "processors": [
            {
                "text_embedding": {
                    "model_id": embedding_model_id,
                    "field_map": {"text": "embedding"},
                }
            },
                        {
                "text_embedding": {
                    "model_id": embedding_model_id,
                    "field_map": {"passage": "passage_embedding"},
                }
            }
        ],
    },
)

print(f"Ingest pipeline ID: {ingest_pipeline_response}")

# Create index with mappings and settings
os_client.indices.create(
    index="population_data_knowledge_base",
    body={
        "mappings": {
            "properties": {
                "text": {"type": "text"},
                "embedding": {
                    "type": "knn_vector",
                    "dimension": 384,
                    "method": {"name": "hnsw", "space_type": "l2", "engine": "lucene"},
                },
            }
        },
        "settings": {
            "index": {
                "knn.space_type": "cosinesimil",
                "default_pipeline": "test-pipeline-local-model",
                "knn": "true",
            }
        },
    },
)

time.sleep(4)

# Bulk insert data
# opensearch helpers bulk insert data

helpers.bulk(
    os_client,
    actions=[
        {
            "_index": "population_data_knowledge_base",
            "_id": "1",
            "_source": {
                "text": "Chart and table of population level and growth rate for the Ogden-Layton metro area from 1950 to 2023. United Nations population projections are also included through the year 2035.\nThe current metro area population of Ogden-Layton in 2023 is 750,000, a 1.63% increase from 2022.\nThe metro area population of Ogden-Layton in 2022 was 738,000, a 1.79% increase from 2021.\nThe metro area population of Ogden-Layton in 2021 was 725,000, a 1.97% increase from 2020.\nThe metro area population of Ogden-Layton in 2020 was 711,000, a 2.16% increase from 2019."
            },
        },
        {
            "_index": "population_data_knowledge_base",
            "_id": "2",
            "_source": {
                "text": "Chart and table of population level and growth rate for the New York City metro area from 1950 to 2023. United Nations population projections are also included through the year 2035.\nThe current metro area population of New York City in 2023 is 18,937,000, a 0.37% increase from 2022.\nThe metro area population of New York City in 2022 was 18,867,000, a 0.23% increase from 2021.\nThe metro area population of New York City in 2021 was 18,823,000, a 0.1% increase from 2020.\nThe metro area population of New York City in 2020 was 18,804,000, a 0.01% decline from 2019."
            },
        },
        {
            "_index": "population_data_knowledge_base",
            "_id": "3",
            "_source": {
                "text": "Chart and table of population level and growth rate for the Chicago metro area from 1950 to 2023. United Nations population projections are also included through the year 2035.\nThe current metro area population of Chicago in 2023 is 8,937,000, a 0.4% increase from 2022.\nThe metro area population of Chicago in 2022 was 8,901,000, a 0.27% increase from 2021.\nThe metro area population of Chicago in 2021 was 8,877,000, a 0.14% increase from 2020.\nThe metro area population of Chicago in 2020 was 8,865,000, a 0.03% increase from 2019."
            },
        },
        {
            "_index": "population_data_knowledge_base",
            "_id": "4",
            "_source": {
                "text": "Chart and table of population level and growth rate for the Miami metro area from 1950 to 2023. United Nations population projections are also included through the year 2035.\nThe current metro area population of Miami in 2023 is 6,265,000, a 0.8% increase from 2022.\nThe metro area population of Miami in 2022 was 6,215,000, a 0.78% increase from 2021.\nThe metro area population of Miami in 2021 was 6,167,000, a 0.74% increase from 2020.\nThe metro area population of Miami in 2020 was 6,122,000, a 0.71% increase from 2019."
            },
        },
        {
            "_index": "population_data_knowledge_base",
            "_id": "5",
            "_source": {
                "text": "Chart and table of population level and growth rate for the Austin metro area from 1950 to 2023. United Nations population projections are also included through the year 2035.\nThe current metro area population of Austin in 2023 is 2,228,000, a 2.39% increase from 2022.\nThe metro area population of Austin in 2022 was 2,176,000, a 2.79% increase from 2021.\nThe metro area population of Austin in 2021 was 2,117,000, a 3.12% increase from 2020.\nThe metro area population of Austin in 2020 was 2,053,000, a 3.43% increase from 2019."
            },
        },
        {
            "_index": "population_data_knowledge_base",
            "_id": "6",
            "_source": {
                "text": "Chart and table of population level and growth rate for the Seattle metro area from 1950 to 2023. United Nations population projections are also included through the year 2035.\nThe current metro area population of Seattle in 2023 is 3,519,000, a 0.86% increase from 2022.\nThe metro area population of Seattle in 2022 was 3,489,000, a 0.81% increase from 2021.\nThe metro area population of Seattle in 2021 was 3,461,000, a 0.82% increase from 2020.\nThe metro area population of Seattle in 2020 was 3,433,000, a 0.79% increase from 2019."
            },
        },
    ],
)

# Create index with mappings and settings
os_client.indices.create(
    index="test_tech_news",
    body={
        "mappings": {
            "properties": {
                "passage": {"type": "text"},
                "passage_embedding": {
                    "type": "knn_vector",
                    "dimension": 384,
                    "method": {"name": "hnsw", "space_type": "l2", "engine": "lucene"},
                },
            }
        },
        "settings": {
            "index": {
                "knn.space_type": "cosinesimil",
                "default_pipeline": "test-pipeline-local-model",
                "knn": "true",
            }
        },
    },
)

time.sleep(4)

# opensearch helpers bulk insert data

helpers.bulk(
    os_client,
    actions=[
        {
            "_index": "test_tech_news",
            "_id": "1",
            "_source": {
                "passage": "Apple Vision Pro is a mixed-reality headset developed by Apple Inc. It was announced on June 5, 2023, at Apple's Worldwide Developers Conference, and pre-orders began on January 19, 2024. It became available for purchase on February 2, 2024, in the United States.[10] A worldwide launch has yet to be scheduled. The Vision Pro is Apple's first new major product category since the release of the Apple Watch in 2015.[11]\n\nApple markets the Vision Pro as a \"spatial computer\" where digital media is integrated with the real world. Physical inputs—such as motion gestures, eye tracking, and speech recognition—can be used to interact with the system.[10] Apple has avoided marketing the device as a virtual reality headset, along with the use of the terms \"virtual reality\" and \"augmented reality\" when discussing the product in presentations and marketing.[12]\n\nThe device runs visionOS,[13] a mixed-reality operating system derived from iOS frameworks using a 3D user interface; it supports multitasking via windows that appear to float within the user's surroundings,[14] as seen by cameras built into the headset. A dial on the top of the headset can be used to mask the camera feed with a virtual environment to increase immersion. The OS supports avatars (officially called \"Personas\"), which are generated by scanning the user's face; a screen on the front of the headset displays a rendering of the avatar's eyes (\"EyeSight\"), which are used to indicate the user's level of immersion to bystanders, and assist in communication.[15]"
            },
        },
        {
            "_index": "test_tech_news",
            "_id": "2",
            "_source": {
                "passage": "LLaMA (Large Language Model Meta AI) is a family of autoregressive large language models (LLMs), released by Meta AI starting in February 2023.\n\nFor the first version of LLaMA, four model sizes were trained: 7, 13, 33, and 65 billion parameters. LLaMA's developers reported that the 13B parameter model's performance on most NLP benchmarks exceeded that of the much larger GPT-3 (with 175B parameters) and that the largest model was competitive with state of the art models such as PaLM and Chinchilla.[1] Whereas the most powerful LLMs have generally been accessible only through limited APIs (if at all), Meta released LLaMA's model weights to the research community under a noncommercial license.[2] Within a week of LLaMA's release, its weights were leaked to the public on 4chan via BitTorrent.[3]\n\nIn July 2023, Meta released several models as Llama 2, using 7, 13 and 70 billion parameters.\n\nLLaMA-2\n\nOn July 18, 2023, in partnership with Microsoft, Meta announced LLaMA-2, the next generation of LLaMA. Meta trained and released LLaMA-2 in three model sizes: 7, 13, and 70 billion parameters.[4] The model architecture remains largely unchanged from that of LLaMA-1 models, but 40% more data was used to train the foundational models.[5] The accompanying preprint[5] also mentions a model with 34B parameters that might be released in the future upon satisfying safety targets.\n\nLLaMA-2 includes both foundational models and models fine-tuned for dialog, called LLaMA-2 Chat. In further departure from LLaMA-1, all models are released with weights, and are free for many commercial use cases. However, due to some remaining restrictions, the description of LLaMA as open source has been disputed by the Open Source Initiative (known for maintaining the Open Source Definition).[6]\n\nIn November 2023, research conducted by Patronus AI, an artificial intelligence startup company, compared performance of LLaMA-2, OpenAI's GPT-4 and GPT-4-Turbo, and Anthropic's Claude2 on two versions of a 150-question test about information in SEC filings (e.g. Form 10-K, Form 10-Q, Form 8-K, earnings reports, earnings call transcripts) submitted by public companies to the agency where one version of the test required the generative AI models to use a retrieval system to locate the specific SEC filing to answer the questions while the other version provided the specific SEC filing to the models to answer the question (i.e. in a long context window). On the retrieval system version, GPT-4-Turbo and LLaMA-2 both failed to produce correct answers to 81% of the questions, while on the long context window version, GPT-4-Turbo and Claude-2 failed to produce correct answers to 21% and 24% of the questions respectively.[7][8]"
            },
        },
        {
            "_index": "test_tech_news",
            "_id": "3",
            "_source": {
                "passage": "Amazon Bedrock is a fully managed service that offers a choice of high-performing foundation models (FMs) from leading AI companies like AI21 Labs, Anthropic, Cohere, Meta, Stability AI, and Amazon via a single API, along with a broad set of capabilities you need to build generative AI applications with security, privacy, and responsible AI. Using Amazon Bedrock, you can easily experiment with and evaluate top FMs for your use case, privately customize them with your data using techniques such as fine-tuning and Retrieval Augmented Generation (RAG), and build agents that execute tasks using your enterprise systems and data sources. Since Amazon Bedrock is serverless, you don't have to manage any infrastructure, and you can securely integrate and deploy generative AI capabilities into your applications using the AWS services you are already familiar with."
            },
        },
    ],
)

# Register model group
response_model_group = os_client.transport.perform_request('POST', '/_plugins/_ml/model_groups/_register', body={
    "name": "openai_model_group",
    "description": "A model group for open ai models"
})

# Retrieve model group ID from the response
model_group_id = response_model_group['model_group_id']

# Create connector
connector_response = os_client.transport.perform_request('POST', '/_plugins/_ml/connectors/_create', body={
    "name": "OpenAI Chat Connector",
    "description": "The connector to public OpenAI model service for GPT 3.5",
    "version": 1,
    "protocol": "http",
    "parameters": {
        "endpoint": "api.openai.com",
        "model": "gpt-3.5-turbo",
        "response_filter": "$.choices[0].message.content",
        "stop": ["\n\nHuman:","\nObservation:","\n\tObservation:","\n\tObservation","\n\nQuestion"],
        "system_instruction": "You are an Assistant which can answer kinds of questions."
    },
    "credential": {
        "openAI_key": OPENAI_API_KEY
    },
    "actions": [
        {
            "action_type": "predict",
            "method": "POST",
            "url": "https://${parameters.endpoint}/v1/chat/completions",
            "headers": {
                "Authorization": "Bearer ${credential.openAI_key}"
            },
            "request_body": "{ \"model\": \"${parameters.model}\", \"messages\": [{\"role\":\"system\",\"content\":\"${parameters.system_instruction}\"},{\"role\":\"user\",\"content\":\"${parameters.question}\"}] }"
        }
    ]
})

# Retrieve connector ID
connector_id = connector_response['connector_id']

# Register OpenAI model
register_openai_model = os_client.transport.perform_request('POST', '/_plugins/_ml/models/_register?deploy=true', body={
    "name": "openAI-gpt-3.5-turbo",
    "function_name": "remote",
    "model_group_id": model_group_id,
    "description": "test model",
    "connector_id": connector_id
})

# Retrieve task id
register_openai_task_id = register_openai_model['task_id']

# Monitor task status
while True:
    task_status = os_client.transport.perform_request('GET', f'/_plugins/_ml/tasks/{register_openai_task_id}')
    if task_status['state'] == 'COMPLETED':
        # Extract model_id from the response
        openai_model_id = task_status['model_id']
        break
    time.sleep(5)

print(f"OpenAI model ID: {openai_model_id}")


# Predict using OpenAI model
sample_predict_response = os_client.transport.perform_request('POST', f'/_plugins/_ml/models/{openai_model_id}/_predict', body={
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
        ],
        "question": "How are you?"
    }
})

print(sample_predict_response)

# Register conversational agent

# - "max_iteration": 5: The agent runs the LLM a maximum of five times.
# - "response_filter": "$.completion": Needed to retrieve the LLM answer from the Amazon Bedrock Claude model response.
# - "doc_size": 3 (in population_data_knowledge_base): Specifies to return the top three documents.

agent_registration_response = os_client.transport.perform_request('POST', '/_plugins/_ml/agents/_register', body={
    "name": "Chat Agent with RAG",
    "type": "conversational",
    "description": "this is a test agent",
    "app_type": "chat_with_rag",
      "llm": {
    "model_id": openai_model_id,
    "parameters": {
      "max_iteration": 3,
    "response_filter": "$.choices[0].message.content",
    }
  },
    "memory": {
        "type": "conversation_index"
    },
    "tools": [
        {
            "type": "VectorDBTool",
            "name": "population_knowledge_base",
            "description": "This tool provides population data of US cities.",
            "parameters": {
                "model_id": embedding_model_id,
                "index": "population_data_knowledge_base",
                "embedding_field": "embedding",
                "doc_size": 3,
                "source_field": [
                    "text"
                ],
                "input": "${parameters.question}"
            }
        },
        {
            "type": "VectorDBTool",
            "name": "tech_news_knowledge_base",
            "description": "This tool provides tech news data.",
            "parameters": {
                "model_id": embedding_model_id,
                "index": "test_tech_news",
                "embedding_field": "passage_embedding",
                "doc_size": 2,
                "source_field": [
                    "passage"
                ],
                "input": "${parameters.question}"
            }
        },
    ]
})

print(agent_registration_response)

# Retrieve agent ID
agent_id = agent_registration_response['agent_id']

# Test the agent
# Predict using OpenAI model
q1_predict_response = os_client.transport.perform_request(
    "POST",
    f"/_plugins/_ml/agents/{agent_id}/_execute",
    body={
  "parameters": {
    "question": "What's vision pro",
    "verbose": True
  }
},
)

print(q1_predict_response)

q2_predict_response = os_client.transport.perform_request(
    "POST",
    f"/_plugins/_ml/agents/{agent_id}/_execute",
    body={
  "parameters": {
    "question": "What's the population increase of Seattle from 2021 to 2023?",
    "verbose": True
  }
},
)

print(q2_predict_response)