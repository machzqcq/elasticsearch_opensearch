from opensearch_py_ml.ml_models import SentenceTransformerModel
import warnings
warnings.filterwarnings('ignore', category=DeprecationWarning)
warnings.filterwarnings('ignore', category=FutureWarning)
warnings.filterwarnings("ignore", message="Unverified HTTPS request")
warnings.filterwarnings("ignore", message="TracerWarning: torch.tensor")
warnings.filterwarnings("ignore", message="using SSL with verify_certs=False is insecure.")

from opensearchpy import OpenSearch
# import mlcommon to later register the model to OpenSearch Cluster
from opensearch_py_ml.ml_commons import MLCommonClient


# CLUSTER_URL = 'https://192.18.0.111:9200'
CLUSTER_URL = {'host': '192.168.0.111', 'port': 9200}

def get_os_client(cluster_url = CLUSTER_URL,
                  username='admin',
                  password='Padmasini10'):
    '''
    Get OpenSearch client
    :param cluster_url: cluster URL like https://ml-te-netwo-1s12ba42br23v-ff1736fa7db98ff2.elb.us-west-2.amazonaws.com:443
    :return: OpenSearch client
    '''
    client = OpenSearch(
        hosts=[cluster_url], #[cluster_url], # {'host': '192.168.0.111', 'port': 9200}
        http_auth=(username, password),
        verify_certs=False,
        use_ssl=True
    )
    return client

client = get_os_client()

# Update cluster settings to allow local model registration
client.cluster.put_settings(body={
    "persistent": {
        "plugins": {
            "ml_commons": {
                "allow_registering_model_via_url": "true",
                "allow_registering_model_via_local_file": "true",
                "only_run_on_ml_node": "false",
                "model_access_control_enabled": "true",
                "native_memory_threshold": "99"
            }
        }
    }
})

# Connect to ml_common client with OpenSearch client
ml_client = MLCommonClient(client)


# Get the list of all sentence transformer models
from huggingface_hub import HfApi

def get_sentence_transformer_models():
    """Fetches a list of all Sentence Transformer models using the Hugging Face API."""

    api = HfApi()
    models = api.list_models(author="sentence-transformers")

    model_names = [model.modelId for model in models]
    return model_names

print(get_sentence_transformer_models())

model_id = "sentence-transformers/all-MiniLM-L6-v1"
folder_path = "sentence-transformer-onnx/all-MiniLM-L6-v1"

# Initialize the SentenceTransformerModel
pre_trained_model = SentenceTransformerModel(model_id=model_id, overwrite=True)

# Save the model to a directory
model_path_onnx = pre_trained_model.save_as_onnx(model_id=model_id)

# Zip the model
print(f'Model saved and zipped at {model_path_onnx}')

# Model config file
model_config_path_onnx = pre_trained_model.make_model_config_json(model_format='ONNX')

# Register the model to OpenSearch Cluster, deploy automatically
model_id = ml_client.register_model(model_path_onnx, model_config_path_onnx, isVerbose=True, wait_until_deployed=True)

print(f"Model {model_id} registered successfully")


# Test the model
input_sentences = ["first sentence", "second sentence"]
# Generated embedding from onnx
embedding_output_onnx = ml_client.generate_embedding(model_id, input_sentences)
# Just taking embedding for the first sentence
data_onnx = embedding_output_onnx["inference_results"][0]["output"][0]["data"]

print(f"Embedding for the first sentence from onnx: {data_onnx}")

# Undeploy the model
ml_client.undeploy_model(model_id)

print(f"Model {model_id} undeployed successfully")

# Delete the model
ml_client.delete_model(model_id)

print(f"Model {model_id} deleted successfully")


