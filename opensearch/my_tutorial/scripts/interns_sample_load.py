from opensearchpy.helpers import bulk
import pandas as pd
from helpers import opensearch_client, opensearch_bulk_sync, opensearch_bulk_async

host = '192.168.0.111'
port = 9200
auth = ('admin', 'Padmasini10') # For testing only. Don't store credentials in code.

client = opensearch_client(host, port, auth=None, ssl=False)

BASE_DIR = "../data"
df = pd.read_parquet(f"{BASE_DIR}/interns_sample.parquet")

success, _ = opensearch_bulk_async(client, 'interns', df)

print(f"Successfully indexed {success} documents.")
