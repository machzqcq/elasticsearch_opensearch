from opensearchpy import OpenSearch, helpers
from sentence_transformers import SentenceTransformer


def opensearch_client(host, port, auth=None, ssl=False):
    client = OpenSearch(
        hosts=[{'host': host, 'port': port}],
        http_auth=auth if auth else None,
        use_ssl=ssl,
        verify_certs=False,
        ssl_show_warn=False
    )
    info = client.info()
    print(f"Welcome to {info['version']['distribution']} {info['version']['number']}!")
    return client

def opensearch_bulk_sync(client, index_name, df, mapping=None):
    if client.indices.exists(index=index_name):
        client.indices.delete(index=index_name)
    
    if mapping:
        client.indices.create(index=index_name, body=mapping)
    else:
        client.indices.create(index=index_name)

    data = [
        {"_index": index_name, "_id": i, "_source": row.to_dict()}
        for i, row in df.iterrows()
    ]

        
    success, failed = helpers.bulk(client=client, actions=data)
    return success, failed

def opensearch_bulk_async(client, index_name, df, mapping=None, delete_index=False):
    if delete_index and client.indices.exists(index=index_name):
        print(f"Deleting index {index_name}")
        client.indices.delete(index=index_name)
    if mapping:
        print(f"Creating index {index_name} with mapping {mapping}")
        client.indices.create(index=index_name, body=mapping)
    else:
        client.indices.create(index=index_name)
        
    data = dataframe_to_actions(df, index_name)
    success, failed = helpers.bulk(client=client, actions=data)
    return success, failed

def opensearch_bulk_async_with_embeddings(client, index_name, df, mapping=None, delete_index=False, 
                                          embedding_model=None, embedding_source_destination_map=None):
    if delete_index and client.indices.exists(index=index_name):
        print(f"Deleting index {index_name}")
        client.indices.delete(index=index_name)
    if mapping:
        print(f"Creating index {index_name} with mapping {mapping}")
        client.indices.create(index=index_name, body=mapping)
    else:
        client.indices.create(index=index_name)
    
    if embedding_source_destination_map:
        for source, destination in embedding_source_destination_map.items():
            print(f"Adding embeddings from {source} to {destination}")
            df = add_embeddings_from_source_to_destination(df, source, destination, embedding_model)

    data = dataframe_to_actions(df, index_name)
    success, failed = helpers.bulk(client=client, actions=data)
    return success, failed

def add_embeddings_from_source_to_destination(df, source, destination, embedding_model_name):
    model = SentenceTransformer(embedding_model_name)
    df.loc[:, destination] = df[source].apply(lambda x: model.encode(x).tolist())
    return df

def return_index_mapping_with_vectors(vectorize_fields):
    # Create OpenSearch mapping for each field with corresponding embedding vector
    mappings = {
        "settings": {
            "index": {
                "knn": True
            }
        },
        "mappings": {
            "properties": {
                field: {"type": "text"} for field in vectorize_fields
            }
        }
    }

    # Add KNN vector fields to the mapping
    for field in vectorize_fields:
        mappings["mappings"]["properties"][f"{field}_EMBEDDING"] = {
            "type": "knn_vector",
            "dimension": 768,
            "method": {
                "name": "hnsw",
                "space_type": "l2",
                "engine": "lucene"
            }
        }

    mappings["mappings"]["properties"] = {k: v for k, v in mappings["mappings"]["properties"].items() if k.endswith("_EMBEDDING")}
    return mappings

def dataframe_to_actions(df, index_name):
    for i, row in df.iterrows():
        yield {
            "_index": index_name,
            "_id": i,
            "_source": row.to_dict()
        }