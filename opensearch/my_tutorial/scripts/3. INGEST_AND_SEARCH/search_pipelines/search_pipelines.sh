PUT /_search/pipeline/my_pipeline 
{
  "request_processors": [
    {
      "filter_query" : {
        "tag" : "tag1",
        "description" : "This processor is going to restrict to publicly visible documents",
        "query" : {
          "term": {
            "visibility": "public"
          }
        }
      }
    }
  ],
  "response_processors": [
    {
      "rename_field": {
        "field": "message",
        "target_field": "notification"
      }
    }
  ]
}

# Retrieve search pipelines
GET /_search/pipeline


PUT /my_index

POST /my_index/_doc
{
    "id": 1,
    "visibility" : "public",
    "message" :  "This is message 1"
}

POST /my_index/_doc
{
    "id": 1,
    "visibility" : "private",
    "message" :  "This is message 2"
}

POST /my_index/_doc
{
    "id": 1,
    "visibility" : "public",
    "message" :  "This is message 3"
}


POST /my_index/_search
{
  "query": {
    "match_all": {}
  }
}

# Option1: Specifying the pipeline in a query parameter
GET /my_index/_search?search_pipeline=my_pipeline

# Option2: Specifying the pipeline in the request body
GET /my_index/_search
{
    "query": {
        "match_all": {}
    },
    "from": 0,
    "size": 10,
    "search_pipeline": "my_pipeline"
}

# Set default search pipeline
DELETE /my_index

PUT /my_index
PUT /my_index/_settings 
{
  "index.search.default_pipeline" : "my_pipeline"
}

POST /my_index/_doc
{
    "id": 1,
    "visibility" : "public",
    "message" :  "This is message 1"
}

POST /my_index/_doc
{
    "id": 1,
    "visibility" : "private",
    "message" :  "This is message 2"
}

POST /my_index/_doc
{
    "id": 1,
    "visibility" : "public",
    "message" :  "This is message 3"
}

GET /my_index/_search

# Remove default pipeline
PUT /my_index/_settings 
{
  "index.search.default_pipeline" : "_none"
}


POST /my_index/_search
{
  "query":{
    "match_all": {}
  }
}


# SEARCH PROCESSORS
DELETE /my_index

POST /_bulk
{ "create":{"_index":"my_index","_id":1}}
{ "title" : "document 1", "color":"blue" }
{ "create":{"_index":"my_index","_id":2}}
{ "title" : "document 2", "color":"blue" }
{ "create":{"_index":"my_index","_id":3}}
{ "title" : "document 3", "color":"red" }
{ "create":{"_index":"my_index","_id":4}}
{ "title" : "document 4", "color":"red" }
{ "create":{"_index":"my_index","_id":5}}
{ "title" : "document 5", "color":"yellow" }
{ "create":{"_index":"my_index","_id":6}}
{ "title" : "document 6", "color":"yellow" }
{ "create":{"_index":"my_index","_id":7}}
{ "title" : "document 7", "color":"orange" }
{ "create":{"_index":"my_index","_id":8}}
{ "title" : "document 8", "color":"orange" }
{ "create":{"_index":"my_index","_id":9}}
{ "title" : "document 9", "color":"green" }
{ "create":{"_index":"my_index","_id":10}}
{ "title" : "document 10", "color":"green" }

# collapse
# In this example, you request the top three documents before collapsing on the color field. Because the first two documents have the same color, the second one is discarded, and the request returns the first and third documents

PUT /_search/pipeline/collapse_pipeline
{
  "response_processors": [
    {
      "collapse" : {
        "field": "color"
      }
    }
  ]
}

POST /my_index/_search?search_pipeline=collapse_pipeline
{
  "size": 3
}

# sort
DELETE /my_index

POST /my_index/_doc
{
    "id": 1,
    "message" : [4,2,3,1],
    "visibility" :  "public"
}

PUT /_search/pipeline/my_pipeline
{
  "response_processors": [
    {
      "sort": {
        "field": "message",
        "target_field": "sorted_message"
      }
    }
  ]
}

# without a search pipeline
GET /my_index/_search

# with sorting search pipeline
GET /my_index/_search?search_pipeline=my_pipeline

# split
DELETE /my_index

POST /my_index/_doc/1
{
  "message": "ingest, search, visualize, and analyze data",
  "visibility": "public"
}

PUT /_search/pipeline/my_pipeline
{
  "response_processors": [
    {
      "split": {
        "field": "message",
        "separator": ", ",
        "target_field": "split_message"
      }
    }
  ]
}

GET /my_index/_search

GET /my_index/_search?search_pipeline=my_pipeline
