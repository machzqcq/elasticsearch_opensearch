from opensearchpy import OpenSearch, helpers


def opensearch_client(host, port, auth=None, ssl=False):
    client = OpenSearch(
        hosts=[{'host': host, 'port': port}],
        http_auth=auth if auth else None,
        use_ssl=ssl,
        verify_certs=ssl
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

def opensearch_bulk_async(client, index_name, df, mapping=None):
    if client.indices.exists(index=index_name):
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

def dataframe_to_actions(df, index_name):
    for i, row in df.iterrows():
        yield {
            "_index": index_name,
            "_id": i,
            "_source": row.to_dict()
        }