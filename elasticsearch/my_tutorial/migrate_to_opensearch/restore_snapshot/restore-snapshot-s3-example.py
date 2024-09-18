from elasticsearch import Elasticsearch
import boto3

# Connect to Elasticsearch
es = Elasticsearch(['your-elasticsearch-endpoint:9200'])

# Configure S3 repository
repository_name = 'my_s3_repository'
bucket_name = 'your-s3-bucket-name'
snapshot_name = 'your-snapshot-name'

# Register S3 repository if not already registered
if not es.snapshot.get_repository(repository=repository_name):
    repository_settings = {
        "type": "s3",
        "settings": {
            "bucket": bucket_name,
            "region": "your-aws-region"
        }
    }
    es.snapshot.create_repository(repository=repository_name, body=repository_settings)

# Restore snapshot
restore_body = {
    "indices": "index1,index2",  # Specify indices to restore, or use "_all" for all indices
    "ignore_unavailable": True,
    "include_global_state": False
}

try:
    response = es.snapshot.restore(
        repository=repository_name,
        snapshot=snapshot_name,
        body=restore_body,
        wait_for_completion=True
    )
    print(f"Snapshot restored successfully: {response}")
except Exception as e:
    print(f"Error restoring snapshot: {e}")

# Check restore status
restore_status = es.snapshot.status(repository=repository_name, snapshot=snapshot_name)
print(f"Restore status: {restore_status}")