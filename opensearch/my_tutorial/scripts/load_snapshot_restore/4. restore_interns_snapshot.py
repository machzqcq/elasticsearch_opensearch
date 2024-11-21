from opensearchpy import OpenSearch

# Initialize the OpenSearch client
IS_AUTH = True

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

# Define the repository and snapshot name
repository_name = 'my_backup_repo'
snapshot_name = 'interns_snapshot'
index_name = "interns"

# Create the repository
repository_settings = {
    "type": "fs",
    "settings": {
        "location": "/usr/share/opensearch/snapshots"
    }
}

# Restore the snapshot
restore_body = {
    "indices": index_name,  # Restore all indices, you can specify specific indices if needed
    "ignore_unavailable": True,
    "include_global_state": False
}

client.snapshot.create_repository(repository_name, body=repository_settings)

# Delete if index already exists
try:
    client.indices.delete(index='interns')
except Exception as e:
    print("Index not found:", e)

# Restore the snapshot
try:
    response = client.snapshot.restore(
        repository=repository_name,
        snapshot=snapshot_name,
        body=restore_body,
        wait_for_completion=True
    )
    print("Snapshot restored successfully:", response)
except Exception as e:
    print("Error restoring snapshot:", e)