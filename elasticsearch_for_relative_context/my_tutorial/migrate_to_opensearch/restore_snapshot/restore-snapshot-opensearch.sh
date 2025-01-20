#!/bin/sh
set -e

# Wait for opensearch to be ready
until curl -s http://opensearch:9200 >/dev/null; do
    echo "Waiting for opensearch..."
    sleep 5
done

echo "opensearch is up. Proceeding with snapshot restoration."

# Register snapshot repository
echo "Registering snapshot repository..."
curl -X PUT "http://opensearch:9200/_snapshot/my_backup" -H "Content-Type: application/json" -d'
{
  "type": "fs",
  "settings": {
    "location": "/var/lib/opensearch/snapshots"
  }
}'

# List available snapshots
echo "Listing available snapshots..."
snapshots=$(curl -s "http://opensearch:9200/_snapshot/my_backup/_all" | grep -oP '(?<="snapshot":")[^"]*')
echo snapshots

# Restore the most recent snapshot
if [ ! -z "$snapshots" ]; then
    latest_snapshot=$(echo "$snapshots" | tail -n 1)
    echo "Restoring snapshot: ${latest_snapshot}"
    curl -X POST "http://opensearch:9200/_snapshot/my_backup/${latest_snapshot}/_restore?wait_for_completion=true"
    echo "Snapshot restoration completed."
else
    echo "No snapshots found to restore."
fi