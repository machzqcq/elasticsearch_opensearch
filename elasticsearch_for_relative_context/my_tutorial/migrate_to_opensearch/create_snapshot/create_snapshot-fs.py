from elasticsearch import Elasticsearch

# Connect to Elasticsearch
es = Elasticsearch(["http://192.168.0.111:9200"])

# Register a snapshot repository
repository_name = "my_backup"
repository_settings = {
    "type": "fs",
    "settings": {
        "location": "/var/lib/elasticsearch/snapshots"  # Location to store snapshots
    }
}

es.snapshot.create_repository(repository=repository_name, body=repository_settings)

# Take a snapshot
snapshot_name = "snapshot_1"
snapshot_body = {
    "indices": "ecommerce",  # Specify indices to include, or use "_all" for all indices
    "ignore_unavailable": True,
    "include_global_state": False
}

es.snapshot.create(repository=repository_name, snapshot=snapshot_name, body=snapshot_body)

# Check snapshot status
snapshot_status = es.snapshot.status(repository=repository_name, snapshot=snapshot_name)
print(snapshot_status)

# List all snapshots in the repository
all_snapshots = es.snapshot.get(repository=repository_name, snapshot="_all")
print(all_snapshots)