from opensearchpy.helpers import bulk
from opensearchpy import OpenSearch
import sys
sys.path.append("../")
from helpers import return_index_mapping_with_vectors, opensearch_bulk_async_with_embeddings
import pandas as pd
import json

IS_AUTH = False

if IS_AUTH:
    # Initialize the OpenSearch client
    client = OpenSearch(
        hosts=[{'host': '192.168.0.111', 'port': 9200}],
        http_auth=('admin', 'Developer123'),  # Replace with your credentials
        use_ssl=True,
        verify_certs=False,
        ssl_show_warn=False
    )
else:
    # Initialize the OpenSearch client without authentication
    client = OpenSearch(
        hosts=[{'host': '192.168.0.111', 'port': 9200}],
        use_ssl=False,
        verify_certs=False,
        ssl_assert_hostname = False,
        ssl_show_warn=False
    )

BASE_DIR = "../../data"
df = pd.read_parquet(f"{BASE_DIR}/interns_sample.parquet")

vectorize_fields = ['COMPANY', 'JOB_TITLE', 'JOB_CONTENT_TEXT']
embedding_source_destination_map = {field: f"{field}_EMBEDDING" for field in vectorize_fields}

mappings = return_index_mapping_with_vectors(vectorize_fields=vectorize_fields)

# Print the mappings to verify
# print(json.dumps(mappings, indent=2))

success, _ = opensearch_bulk_async_with_embeddings(client, index_name="interns", delete_index=True, 
                                                   df=df.iloc[0:5], mapping=mappings, embedding_model="msmarco-distilbert-base-v2", embedding_source_destination_map=embedding_source_destination_map)
