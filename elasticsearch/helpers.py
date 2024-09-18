# elasticsearch==8.15.0
import csv
import json
from elasticsearch import Elasticsearch, helpers  # Import the helpers module
import pandas as pd
from IPython.display import display
import os


def csv_to_json(csv_file: str) -> str:
    """
    Convert a CSV file to JSON format.
    Args:
        csv_file (str): The path to the CSV file.
    Returns:
        str: The JSON data representing the contents of the CSV file.
    """
    # Read CSV file into pandas DataFrame
    df = pd.read_csv(csv_file)
    
    # Split columns with "|" delimiter
    for col in df.columns:
        if "|" in str(df[col].iloc[0]):
            df[col] = df[col].str.split('|')
    
    # Convert DataFrame to JSON
    json_data = df.to_json(orient='records')
    return json_data

def bulk_load_documents(es: Elasticsearch, index_name: str, documents: list) -> None:
    """
    Bulk loads a list of documents into Elasticsearch.
    Parameters:
    - es (Elasticsearch): The Elasticsearch client instance.
    - index_name (str): The name of the index where the documents will be inserted.
    - documents (list): A list of documents to be inserted into Elasticsearch.
    Returns:
    - None
    Raises:
    - None
    """
    # Prepare the actions for bulk indexing
    actions = [
        {
            "_index": index_name,
            "_source": doc
        }
        for doc in documents
    ]

    # Perform the bulk load
    response = helpers.bulk(es, actions)
    
    # Print the response
    print(response)