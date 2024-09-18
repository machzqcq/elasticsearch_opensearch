from elasticsearch import Elasticsearch
import boto3

# Connect to your Elasticsearch cluster
es = Elasticsearch(['your-elasticsearch-endpoint:9200'])

# Configure the S3 repository
repository_name = 'my_s3_repository'
bucket_name = 'your-s3-bucket-name'

repository_settings = {
    "type": "s3",
    "settings": {
        "bucket": bucket_name,
        "region": "your-aws-region"
    }
}

# Register the repository
es.snapshot.create_repository(repository=repository_name, body=repository_settings)

# Create a snapshot
snapshot_name = 'my_snapshot'
snapshot_body = {
    "indices": "index1,index2",  # Specify indices to include, or use "_all" for all indices
    "ignore_unavailable": True,
    "include_global_state": False
}

es.snapshot.create(repository=repository_name, snapshot=snapshot_name, body=snapshot_body, wait_for_completion=True)

print(f"Snapshot '{snapshot_name}' created successfully in repository '{repository_name}'")