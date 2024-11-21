from opensearchpy import OpenSearch

IS_AUTH = False

if IS_AUTH:
    # Initialize the OpenSearch client
    client = OpenSearch(
        hosts=[{'host': '192.168.0.111', 'port': 9200}],
        http_auth=('admin', 'Developer@123'),  # Replace with your credentials
        use_ssl=True,
        verify_certs=False,
        ssl_show_warn=False
    )
else:
    # Initialize the OpenSearch client without authentication
    client = OpenSearch(
        hosts=[{'host': '192.168.0.111', 'port': 9200}],
        use_ssl=False,
        verify_certs=False,
        ssl_assert_hostname = False,
        ssl_show_warn=False
    )

# Define the repository configuration
repository_body = {
    "type": "fs",
    "settings": {
        "location": "/usr/share/opensearch/snapshots",  # Replace with your snapshot location
        "compress": True
    }
}

# Create the snapshot repository
repository_name = "my_backup_repo"
client.snapshot.create_repository(repository_name, body=repository_body)

# Create a snapshot
snapshot_name = "interns_snapshot"
snapshot_body = {
    "indices": "_all",  # Specify indices to include, or use "_all" for all indices OR -.opensearch*,-.opendistro*,-.kibana*, interns
    "ignore_unavailable": True,
    "include_global_state": False
}

# Check if the snapshot already exists
snapshots = client.snapshot.get(repository_name, '_all')['snapshots']
snapshot_exists = any(snap['snapshot'] == snapshot_name for snap in snapshots)

# Delete the snapshot if it already exists
# if snapshot_exists:
#     client.snapshot.delete(repository_name, snapshot_name)

# Create the snapshot
client.snapshot.create(repository_name, snapshot_name, body=snapshot_body, wait_for_completion=True)

print(f"Snapshot {snapshot_name} created successfully in repository {repository_name}.")