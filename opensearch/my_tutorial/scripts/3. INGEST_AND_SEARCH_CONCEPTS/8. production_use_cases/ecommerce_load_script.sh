#!/bin/sh
set -e

# Wait for OpenSearch to start
until curl -u admin:Developer@123 -s -k https://opensearch:9200 >/dev/null; do
    echo "Waiting for OpenSearch to be ready..."
    sleep 10
done

echo "OpenSearch is ready. Creating index with mappings..."

# Create index with mappings (use application/json for mappings)
curl -k -u admin:Developer@123 -X PUT "https://opensearch:9200/ecommerce" \
  -H "Content-Type: application/json" \
  --data-binary @/mappings/ecommerce-field_mappings.json

echo "Index created. Loading bulk data..."

# Load data (use application/x-ndjson for bulk operations)
curl -k -u admin:Developer@123 -X POST "https://opensearch:9200/ecommerce/_bulk?pretty" \
  -H "Content-Type: application/x-ndjson" \
  --data-binary @/json_data/ecommerce.json

echo "Data loaded successfully!"