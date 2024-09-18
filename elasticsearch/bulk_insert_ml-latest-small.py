# elasticsearch==8.15.0
import os
from elasticsearch import Elasticsearch
import json
from helpers import csv_to_json, bulk_load_documents

# Get the current directory
current_dir = os.getcwd()

# Get all CSV files in the current directory
csv_files = [file for file in os.listdir(current_dir) if file.endswith('.csv')]

# Initialize Elasticsearch
es = Elasticsearch(hosts=["http://192.168.0.111:9200"])

# Iterate over each CSV file
for csv_file in csv_files:
    print(f"Processing {csv_file}...")
    # Convert CSV to JSON
    json_data = csv_to_json(csv_file)

    # Load JSON documents into Elasticsearch
    bulk_load_documents(es, csv_file.split(".")[0], json.loads(json_data))
