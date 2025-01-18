from opensearchpy import OpenSearch, RequestsHttpConnection, helpers
import json, os, time
from dotenv import load_dotenv
import sys
sys.path.append('../../')
from helpers import (
    create_openai_connector,
    register_openai_model,
    deploy_openai_model,
    create_conversational_agent,
    execute_agent,
    execute_agent_tools,
    create_root_agent
)

# 1. Load environment variables from .env file
load_dotenv("../../.env")

# 2. Retrieve the OpenAI API key from environment variables
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

# OpenSearch connection setup
client = OpenSearch(
    hosts=[{'host': '192.168.0.111', 'port': 9200}],
    http_auth=('admin', 'Developer@123'),  # Replace with your credentials
    use_ssl=True,
    verify_certs=False,
    connection_class=RequestsHttpConnection
)

# Cluster settings
client.cluster.put_settings(
    body={
        "persistent": {
            "plugins.ml_commons.only_run_on_ml_node": "false",
            "plugins.ml_commons.native_memory_threshold": 100,
            "plugins.ml_commons.memory_feature_enabled": "true",
        }
    }
)

# Register model
register_response = client.transport.perform_request(
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
    task_status = client.transport.perform_request(
        "GET", f"/_plugins/_ml/tasks/{register_task_id}"
    )
    if task_status["state"] == "COMPLETED":
        # Extract model_id from the response
        embedding_model_id = task_status["model_id"]
        break
    time.sleep(5)

print(f"Model ID: {embedding_model_id}")

# Deploy the model
deploy_response = client.transport.perform_request(
    method="POST", url=f"/_plugins/_ml/models/{embedding_model_id}/_deploy"
)
print(deploy_response)


# Extract deployment task_id from the response
deploy_task_id = deploy_response["task_id"]

# Wait until the deployment status becomes completed
while True:
    deployment_status = client.transport.perform_request(
        method="GET", url=f"/_plugins/_ml/tasks/{deploy_task_id}"
    )
    print(deployment_status)
    if deployment_status["state"] == "COMPLETED":
        break
    time.sleep(10)  # Wait for 10 seconds before checking again

# Create ingest pipeline
ingest_pipeline_response = client.ingest.put_pipeline(
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
            },
            {
                "text_embedding": {
                    "model_id": embedding_model_id,
                    "field_map": {"stock_price_history": "stock_price_history_embedding"},
                }
            }
        ],
    },
)

print(f"Ingest pipeline ID: {ingest_pipeline_response}")

# Create index with mappings and settings
client.indices.create(
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

# Bulk insert data
# opensearch helpers bulk insert data

helpers.bulk(
    client,
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

client.indices.create(
    index="test_stock_price_data",
    body={
        "mappings": {
            "properties": {
                "stock_price_history": {"type": "text"},
                "stock_price_history_embedding": {
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

# Bulk insert data
helpers.bulk(
    client,
    actions=[
        {
            "_index": "test_stock_price_data",
            "_id": "1",
            "_source": {
                "stock_price_history": "This is the historical monthly stock price record for Amazon.com, Inc. (AMZN) with CSV format.\nDate,Open,High,Low,Close,Adj Close,Volume\n2023-03-01,93.870003,103.489998,88.120003,103.290001,103.290001,1349240300\n2023-04-01,102.300003,110.860001,97.709999,105.449997,105.449997,1224083600\n2023-05-01,104.949997,122.919998,101.150002,120.580002,120.580002,1432891600\n2023-06-01,120.690002,131.490005,119.930000,130.360001,130.360001,1242648800\n2023-07-01,130.820007,136.649994,125.919998,133.679993,133.679993,1058754800\n2023-08-01,133.550003,143.630005,126.410004,138.009995,138.009995,1210426200\n2023-09-01,139.460007,145.860001,123.040001,127.120003,127.120003,1120271900\n2023-10-01,127.279999,134.479996,118.349998,133.089996,133.089996,1224564700\n2023-11-01,133.960007,149.259995,133.710007,146.089996,146.089996,1025986900\n2023-12-01,146.000000,155.630005,142.809998,151.940002,151.940002,931128600\n2024-01-01,151.539993,161.729996,144.050003,155.199997,155.199997,953344900\n2024-02-01,155.869995,175.000000,155.619995,174.449997,174.449997,437720800\n"
            },
        },
        {
            "_index": "test_stock_price_data",
            "_id": "2",
            "_source": {
                "stock_price_history": "This is the historical monthly stock price record for Apple Inc. (AAPL) with CSV format.\nDate,Open,High,Low,Close,Adj Close,Volume\n2023-03-01,146.830002,165.000000,143.899994,164.899994,164.024475,1520266600\n2023-04-01,164.270004,169.850006,159.779999,169.679993,168.779099,969709700\n2023-05-01,169.279999,179.350006,164.309998,177.250000,176.308914,1275155500\n2023-06-01,177.699997,194.479996,176.929993,193.970001,193.207016,1297101100\n2023-07-01,193.779999,198.229996,186.600006,196.449997,195.677261,996066400\n2023-08-01,196.240005,196.729996,171.960007,187.869995,187.130997,1322439400\n2023-09-01,189.490005,189.979996,167.619995,171.210007,170.766846,1337586600\n2023-10-01,171.220001,182.339996,165.669998,170.770004,170.327972,1172719600\n2023-11-01,171.000000,192.929993,170.119995,189.949997,189.458313,1099586100\n2023-12-01,190.330002,199.619995,187.449997,192.529999,192.284637,1062774800\n2024-01-01,187.149994,196.380005,180.169998,184.399994,184.164993,1187219300\n2024-02-01,183.990005,191.050003,179.250000,188.850006,188.609329,420063900\n"
            },
        },
        {
            "_index": "test_stock_price_data",
            "_id": "3",
            "_source": {
                "stock_price_history": "This is the historical monthly stock price record for NVIDIA Corporation (NVDA) with CSV format.\nDate,Open,High,Low,Close,Adj Close,Volume\n2023-03-01,231.919998,278.339996,222.970001,277.769989,277.646820,1126373100\n2023-04-01,275.089996,281.100006,262.200012,277.489990,277.414032,743592100\n2023-05-01,278.399994,419.380005,272.399994,378.339996,378.236420,1169636000\n2023-06-01,384.890015,439.899994,373.559998,423.019989,422.904175,1052209200\n2023-07-01,425.170013,480.880005,413.459991,467.290009,467.210449,870489500\n2023-08-01,464.600006,502.660004,403.109985,493.549988,493.465942,1363143600\n2023-09-01,497.619995,498.000000,409.799988,434.989990,434.915924,857510100\n2023-10-01,440.299988,476.089996,392.299988,407.799988,407.764130,1013917700\n2023-11-01,408.839996,505.480011,408.690002,467.700012,467.658905,914386300\n2023-12-01,465.250000,504.329987,450.100006,495.220001,495.176453,740951700\n2024-01-01,492.440002,634.929993,473.200012,615.270020,615.270020,970385300\n2024-02-01,621.000000,721.849976,616.500000,721.330017,721.330017,355346500\n"
            },
        },
        {
            "_index": "test_stock_price_data",
            "_id": "4",
            "_source": {
                "stock_price_history": "This is the historical monthly stock price record for Meta Platforms, Inc. (META) with CSV format.\nDate,Open,High,Low,Close,Adj Close,Volume\n2023-03-01,174.589996,212.169998,171.429993,211.940002,211.940002,690053000\n2023-04-01,208.839996,241.690002,207.130005,240.320007,240.320007,446687900\n2023-05-01,238.619995,268.649994,229.850006,264.720001,264.720001,486968500\n2023-06-01,265.899994,289.790009,258.880005,286.980011,286.980011,480979900\n2023-07-01,286.700012,326.200012,284.850006,318.600006,318.600006,624605100\n2023-08-01,317.540009,324.140015,274.380005,295.890015,295.890015,423147800\n2023-09-01,299.369995,312.869995,286.790009,300.209991,300.209991,406686600\n2023-10-01,302.739990,330.540009,279.399994,301.269989,301.269989,511307900\n2023-11-01,301.850006,342.920013,301.850006,327.149994,327.149994,329270500\n2023-12-01,325.480011,361.899994,313.660004,353.959991,353.959991,332813800\n2024-01-01,351.320007,406.359985,340.010010,390.140015,390.140015,347020200\n2024-02-01,393.940002,485.959991,393.049988,473.279999,473.279999,294260900\n"
            },
        },
        {
            "_index": "test_stock_price_data",
            "_id": "5",
            "_source": {
                "stock_price_history": "This is the historical monthly stock price record for Microsoft Corporation (MSFT) with CSV format.\nDate,Open,High,Low,Close,Adj Close,Volume\n2023-03-01,250.759995,289.269989,245.610001,288.299988,285.953064,747635000\n2023-04-01,286.519989,308.929993,275.369995,307.260010,304.758759,551497100\n2023-05-01,306.970001,335.940002,303.399994,328.390015,325.716766,600807200\n2023-06-01,325.929993,351.470001,322.500000,340.540009,338.506226,547588700\n2023-07-01,339.190002,366.779999,327.000000,335.920013,333.913818,666764400\n2023-08-01,335.190002,338.540009,311.549988,327.760010,325.802582,479456700\n2023-09-01,331.309998,340.859985,309.450012,315.750000,314.528809,416680700\n2023-10-01,316.279999,346.200012,311.209991,338.109985,336.802307,540907000\n2023-11-01,339.790009,384.299988,339.649994,378.910004,377.444519,563880300\n2023-12-01,376.760010,378.160004,362.899994,376.040009,375.345886,522003700\n2024-01-01,373.859985,415.320007,366.500000,397.579987,396.846130,528399000\n2024-02-01,401.829987,420.820007,401.799988,409.489990,408.734131,237639700\n"
            },
        },
        {
            "_index": "test_stock_price_data",
            "_id": "6",
            "_source": {
                "stock_price_history": "This is the historical monthly stock price record for Alphabet Inc. (GOOG) with CSV format.\nDate,Open,High,Low,Close,Adj Close,Volume\n2023-03-01,90.160004,107.510002,89.769997,104.000000,104.000000,725477100\n2023-04-01,102.669998,109.629997,102.379997,108.220001,108.220001,461670700\n2023-05-01,107.720001,127.050003,104.500000,123.370003,123.370003,620317400\n2023-06-01,123.500000,129.550003,116.910004,120.970001,120.970001,521386300\n2023-07-01,120.320000,134.070007,115.830002,133.110001,133.110001,525456900\n2023-08-01,130.854996,138.399994,127.000000,137.350006,137.350006,463482000\n2023-09-01,138.429993,139.929993,128.190002,131.850006,131.850006,389593900\n2023-10-01,132.154999,142.380005,121.459999,125.300003,125.300003,514877100\n2023-11-01,125.339996,141.100006,124.925003,133.919998,133.919998,405635900\n2023-12-01,133.320007,143.945007,129.399994,140.929993,140.929993,482059400\n2024-01-01,139.600006,155.199997,136.850006,141.800003,141.800003,428771200\n2024-02-01,143.690002,150.695007,138.169998,147.139999,147.139999,231934100\n"
            },
        },
    ],
)



try:
    # Create connector
    connector_id = create_openai_connector(client, OPENAI_API_KEY)
    print(f"OpenAI connector created with ID: {connector_id}")

    # Register model
    model_id = register_openai_model(client, connector_id)
    print(f"OpenAI model registered with ID: {model_id}")

    # Deploy model
    openai_model_id = deploy_openai_model(client,model_id)
    print(f"OpenAI model{openai_model_id} deployed")

    # Create conversational agent
    agent_id = create_conversational_agent(client, model_id, embedding_model_id)
    print(f"Conversational agent created with ID: {agent_id}")

    # Execute agent
    question = "What's the population increase of Seattle from 2021 to 2023?"
    result = execute_agent(client, agent_id, question)
    print("Agent response:")
    print(json.dumps(result, indent=2))

    # Continue conversation
    memory_id = result['inference_results'][0]['output'][0]['result']
    follow_up_question = "What was Amazon's stock price in December 2023?"
    result = execute_agent(client, agent_id, follow_up_question, memory_id)
    print("Agent response to follow-up:")
    print(json.dumps(result, indent=2))

    # Execute agent
    question = "Can you query with index population_data_knowledge_base to calculate the population increase of Seattle from 2021 to 2023?"
    result = execute_agent_tools(client, agent_id, question, ["CatIndexTool"])
    print("Agent response:")
    print(json.dumps(result, indent=2))

    # Configure root agent
    root_agent_id = create_root_agent(client, agent_id, model_id)
    print(f"Root agent created with ID: {root_agent_id}")

    ## Manually do the below in open-search cluster (node1 for e.g.)
    # curl -k --cert ./kirk.pem --key ./kirk-key.pem -X PUT https://localhost:9200/.plugins-ml-config/_doc/os_chat -H 'Content-Type: application/json' -d'{ "type": "os_chat_root_agent", "configuration":{"agent_id":"WebRWpQBhhsY4kUAptfO"}}'

except Exception as e:
    print(f"An error occurred: {str(e)}")