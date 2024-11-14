#!/bin/sh
set -e

# Wait for Elasticsearch to start
until curl -s http://elasticsearch:9200 >/dev/null; do
    sleep 10
done

# Create index with mappings
curl -X PUT "http://elasticsearch:9200/ecommerce" -H "Content-Type: application/json" -d @/mappings/ecommerce-field_mappings.json

# Load data
curl -X POST "http://elasticsearch:9200/ecommerce/_bulk" -H "Content-Type: application/json" --data-binary @/json_data/ecommerce.json