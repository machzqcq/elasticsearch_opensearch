#!/bin/sh
set -e

# Wait for Elasticsearch to start
until curl -s -k http://opensearch:9200 >/dev/null; do
    sleep 10
done

# Create index with mappings
curl -k -X PUT "http://opensearch:9200/ecommerce" -H "Content-Type: application/x-ndjson" --data-binary @/mappings/ecommerce-field_mappings.json

# Load data
curl -k -X  PUT "http://opensearch:9200/ecommerce/_bulk" -H "Content-Type: application/x-ndjson" --data-binary @/json_data/ecommerce.json