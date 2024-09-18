#!/bin/sh
set -e

# Wait for Elasticsearch to be ready
until curl -s http://elasticsearch:9200 >/dev/null; do
    echo "Waiting for Elasticsearch..."
    sleep 5
done

echo "Elasticsearch is up. Proceeding with snapshot restoration."

# Register snapshot repository
echo "Registering snapshot repository..."
curl -X PUT "http://elasticsearch:9200/_snapshot/my_backup" -H "Content-Type: application/json" -d'
{
  "type": "fs",
  "settings": {
    "location": "/var/lib/elasticsearch/snapshots"
  }
}'

# List available snapshots
echo "Listing available snapshots..."
snapshots=$(curl -s "http://elasticsearch:9200/_snapshot/my_backup/_all" | grep -oP '(?<="snapshot":")[^"]*')
echo snapshots

# Restore the most recent snapshot
if [ ! -z "$snapshots" ]; then
    latest_snapshot=$(echo "$snapshots" | tail -n 1)
    echo "Restoring snapshot: ${latest_snapshot}"
    curl -X POST "http://elasticsearch:9200/_snapshot/my_backup/${latest_snapshot}/_restore?wait_for_completion=true"
    echo "Snapshot restoration completed."
else
    echo "No snapshots found to restore."
fi