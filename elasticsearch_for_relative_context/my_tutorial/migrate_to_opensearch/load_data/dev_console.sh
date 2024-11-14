GET _cat/indices

GET ecommerce/_search
{
  "query": {
    "match_all": {}
  }
}