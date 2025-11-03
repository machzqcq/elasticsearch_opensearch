from opensearchpy.helpers import bulk
from opensearchpy import OpenSearch

import pandas as pd
import json

IS_AUTH = True # Set to False if security is disabled
HOST = 'localhost'  # Replace with your OpenSearch host, if running everything locally use 'localhost'
DATA_FOLDER = '../0. DATA'

if IS_AUTH:
    # Initialize the OpenSearch client
    client = OpenSearch(
        hosts=[{'host': HOST, 'port': 9200}],
        http_auth=('admin', 'Developer@123'),  # Replace with your credentials
        use_ssl=True,
        verify_certs=False,
        ssl_show_warn=False
    )
else:
    # Initialize the OpenSearch client without authentication
    client = OpenSearch(
        hosts=[{'host': HOST, 'port': 9200}],
        use_ssl=False,
        verify_certs=False,
        ssl_assert_hostname = False,
        ssl_show_warn=False
    )

BASE_DIR = DATA_FOLDER
# Load the data from the JSON file
data = []
with open(f"{BASE_DIR}/ecommerce.json", 'r') as file:
    for line in file:
        data.append(line.strip() + '\n')

# Load the index mappings from the JSON file
with open(f"{BASE_DIR}/ecommerce-field_mappings.json", 'r') as file:
    index_mappings = json.load(file)

# Create the index with the specified mappings
client.indices.create(index='ecommerce', body=index_mappings, ignore=400)

# Use the bulk helper to index the data
bulk(client, actions=data, index='ecommerce', refresh=True)