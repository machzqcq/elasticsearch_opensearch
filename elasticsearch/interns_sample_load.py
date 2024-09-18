# elasticsearch==8.15.0
import os
from elasticsearch import Elasticsearch
import json
from helpers import csv_to_json, bulk_load_documents

import pandas as pd

BASE_DIR = "../../txtai/data"

df = pd.read_parquet(f"{BASE_DIR}/interns_sample.parquet")

# Initialize Elasticsearch
es = Elasticsearch(hosts=["http://192.168.0.111:9200"])

# Load JSON documents into Elasticsearch
bulk_load_documents(es, "interns_sample", json.loads(df.to_json(orient="records")))
