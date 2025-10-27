#!/bin/sh
set -e

# Wait for OpenSearch to start
until curl -u admin:Developer@123 -s -k https://opensearch:9200 >/dev/null; do
    echo "Waiting for OpenSearch to be ready..."
    sleep 10
done

echo "OpenSearch is ready. Creating index with mappings..."

# Debug: Check if files exist
echo "Checking for mapping file..."
ls -la /mappings/ || echo "Mappings directory not found!"
ls -la /mappings/ecommerce-field_mappings.json || echo "Mappings file not found!"

echo "Checking for data file..."
ls -la /json_data/ || echo "Data directory not found!"
ls -la /json_data/ecommerce.json || echo "Data file not found!"

# Create index with mappings (use application/json for mappings)
if [ -f /mappings/ecommerce-field_mappings.json ]; then
    curl -k -u admin:Developer@123 -X PUT "https://opensearch:9200/ecommerce" -H "Content-Type: application/json" --data-binary @/mappings/ecommerce-field_mappings.json
    echo "Index created."
else
    echo "ERROR: Mappings file not found!"
    exit 1
fi

echo "Loading bulk data..."

# Load data (use application/x-ndjson for bulk operations)
if [ -f /json_data/ecommerce.json ]; then
    curl -k -u admin:Developer@123 -X POST "https://opensearch:9200/ecommerce/_bulk?pretty" -H "Content-Type: application/x-ndjson" --data-binary @/json_data/ecommerce.json
    echo "Data loaded successfully!"
else
    echo "ERROR: Data file not found!"
    exit 1
fi