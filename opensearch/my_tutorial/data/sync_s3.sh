#!/bin/bash

# Define the source and destination
SOURCE_DIR="/home/ubuntu/git-projects/personal/github.com/elasticsearch_opensearch/opensearch/my_tutorial/data"
DESTINATION_BUCKET="s3://techsparksguru-training-datasets/elasticsearch_opensearch"

# Sync the files
aws s3 sync "$SOURCE_DIR" "$DESTINATION_BUCKET" --profile pradeep-seleniumframework

# Check if the sync was successful
if [ $? -eq 0 ]; then
    echo "Sync completed successfully."
else
    echo "Sync failed."
fi