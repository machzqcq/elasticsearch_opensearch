# Create vector index
# l2 means distance metrics is Euclidean distance
PUT /hotels-index
{
  "settings": {
    "index.knn": true
  },
  "mappings": {
    "properties": {
      "location": {
        "type": "knn_vector",
        "dimension": 2,
        "space_type": "l2"
      }
    }
  }
}

# Add data to your index
POST /_bulk
{ "index": { "_index": "hotels-index", "_id": "1" } }
{ "location": [5.2, 4.4] }
{ "index": { "_index": "hotels-index", "_id": "2" } }
{ "location": [5.2, 3.9] }
{ "index": { "_index": "hotels-index", "_id": "3" } }
{ "location": [4.9, 3.4] }
{ "index": { "_index": "hotels-index", "_id": "4" } }
{ "location": [4.2, 4.6] }
{ "index": { "_index": "hotels-index", "_id": "5" } }
{ "location": [3.3, 4.5] }

# Search your data
POST /hotels-index/_search
{
  "size": 3,
  "query": {
    "knn": {
      "location": {
        "vector": [5, 4],
        "k": 3
      }
    }
  }
}