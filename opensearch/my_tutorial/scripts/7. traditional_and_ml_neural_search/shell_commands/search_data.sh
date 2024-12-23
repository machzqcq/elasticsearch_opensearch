# Collapse
GET my-index/_search
{
    "query": {
        "match": {
            "title": "opensearch"
        }
    },
    "collapse": {
        "field": "user.id"
    },
    "sort": ["likes"]
}

GET ecommerce/_mapping
POST ecommerce/_search
GET ecommerce/_search
{
    "query": {
        "match": {
            "category.keyword": "Men's Shoes"
        }
    },
    "collapse": {
        "field": "type"
    },
    "sort": ["day_of_week"]
}

#Paginate
GET ecommerce/_search
{
  "from": 0,
  "size": 10,
  "query": {
    "match": {
      "manufacturer": "Elitelligence"
    }
  }
}

GET ecommerce/_search?from=0&size=10

GET ecommerce/_search?scroll=10m
{
  "size": 5
}

GET _search/scroll
{
  "scroll": "10m",
  "scroll_id": "DXF1ZXJ5QW5kRmV0Y2gBAAAAAAAAAAUWdmpUZDhnRFBUcWFtV21nMmFwUGJEQQ=="
}

# Search after
GET ecommerce/_search
{
  "size": 3,
  "query": {
    "match": {
      "manufacturer": "Elitelligence"
    }
  },
  "sort": [
    { "products.category.keyword": "asc" },
    { "_id": "asc" } 
  ]
}

GET ecommerce/_search
{
  "size": 10,
  "query": {
    "match": {
      "manufacturer": "Elitelligence"
    }
  },
  "search_after": [ "Men's Accessories", "1047"],
  "sort": [
    { "products.category.keyword": "asc" },
    { "_id": "asc" } 
  ]
}


# PIT (point in time)
POST /ecommerce/_search/point_in_time?keep_alive=100m


GET _search
{
  "size": 10,
  "query": {
    "match": {
      "manufacturer": "Elitelligence"
    }
  },
  "search_after": [ "Men's Accessories", "1047"],
  "sort": [
    { "products.category.keyword": "asc" },
    { "_id": "asc" } 
  ],
  "pit": {
    "id":  "87mEQQEJZWNvbW1lcmNlFmVWMTdBdE9TU1hTS29pa1lXVmxQb2cAFi1sV1huazZoVHcybzd1MkxnMHlqZWcAAAAAAAAAADUWQXFpajZzWERSRzZxRlhnekZrc1RCUQEWZVYxN0F0T1NTWFNLb2lrWVdWbFBvZwAA", 
    "keep_alive": "100m"
  }
}


# Search
GET ecommerce/_search
{
  "size": 10,
  "query": {
    "match": {
      "manufacturer": "Elitelligence"
    }
  },
  "sort": [
    { "products.category.keyword": "asc" },
    { "_id": "asc" } 
  ],
    "search_after": [ "Men's Accessories", "1047"]
}

GET ecommerce/_search
{
   "query" : {
      "match_all": {}
   },
   "sort" : [
      {"manufacturer.keyword": {"order" : "desc"}}
   ]
}

# Highlight
GET ecommerce/_search
{
  "query": {
    "match": {
      "products.product_name": "blue"
    }
  },
  "size": 3,
  "highlight": {
    "fields": {
      "products.product_name": {}
    }
  }
}

GET ecommerce/_search
{
  "query": {
    "match": {
      "products.product_name": "blue"
    }
  },
  "size": 3,
  "highlight": {
    "pre_tags": [
      "<strong>"
    ],
    "post_tags": [
      "</strong>"
    ],
    "fields": {
      "products.product_name": {}
    }
  }
}

# AUTOCOMPLETE
DELETE ecommerce

# Use python script create_ecommerce_original_edge_ngrams.py to create mapping and load data

POST ecommerce/_analyze
{
  "analyzer": "autocomplete",
  "text": "summer"
}

GET ecommerce/_search
{
  "query": {
    "match": {
      "products.product_name": {
        "query": "sum",
        "analyzer": "autocomplete"
      }
    }
  }
}

# Too many hits above : Use the standard analyzer at search time. Otherwise, the search query splits into edge n-grams and you get results for everything that matches s, u, and m etc

GET ecommerce/_search
{
  "query": {
    "match": {
      "products.product_name": {
        "query": "sum",
        "analyzer": "standard"
      }
    }
  }
}

# Fuzzy search
DELETE ecommerce
PUT ecommerce
{
  "mappings": {
    "properties": {
      "products.product_name": {
        "type": "completion"
      }
    }
  }
}

# Use python script create_ecommerce_original_edge_ngrams.py to create mapping and load data

GET ecommerce/_search
{
  "suggest": {
    "autocomplete": {
      "prefix": "summer",
      "completion": {
        "field": "products.product_name",
        "size": 3
      }
    }
  }
}

# Misspelings 

GET ecommerce/_search
{
  "suggest": {
    "autocomplete": {
      "prefix": "smmer",
      "completion": {
        "field": "products.product_name",
        "size": 3,
        "fuzzy": {
          "fuzziness": "AUTO"
        }
      }
    }
  }
}

# Regex
GET ecommerce/_search
{
  "suggest": {
    "autocomplete": {
      "prefix": "sum*",
      "completion": {
        "field": "products.product_name",
        "size": 3,
        "fuzzy": {
          "fuzziness": "AUTO"
        }
      }
    }
  }
}

# SEARCH AS YOU TYPE
DELETE ecommerce
PUT ecommerce
{
  "mappings": {
    "properties": {
      "products.product_name": {
        "type": "search_as_you_type"
      }
    }
  }
}

GET ecommerce/_search
{
  "query": {
    "multi_match": {
      "query": "shirt black",
      "type": "bool_prefix",
      "fields": [
        "products.product_name",
        "products.product_name._2gram",
        "products.product_name._3gram"
      ]
    }
  },
  "size": 3
}

# DID YOU MEAN
GET ecommerce/_analyze
{
  "text": "Casual lace-ups - dark brown , Basic T-shirt - white",
  "field": "products.produce_name"
}

#Misspelt
GET ecommerce/_search
{
  "suggest": {
    "spell-check": {
      "text": "blzr",
      "term": {
        "field": "products.product_name"
      }
    }
  }
}

GET ecommerce/_search
{
  "suggest": {
    "spell-check1": {
      "text": "blzr",
      "term": {
        "field": "products.product_name"
      }
    },
    "spell-check2": {
      "text": "blck",
      "term": {
        "field": "products.product_name"
      }
    }
  }
}

#Phrase suggestor
PUT books2
{
  "settings": {
    "index": {
      "analysis": {
        "analyzer": {
          "trigram": {
            "type": "custom",
            "tokenizer": "standard",
            "filter": [
              "lowercase",
              "shingle"
            ]
          }
        },
        "filter": {
          "shingle": {
            "type": "shingle",
            "min_shingle_size": 2,
            "max_shingle_size": 3
          }
        }
      }
    }
  },
  "mappings": {
    "properties": {
      "title": {
        "type": "text",
        "fields": {
          "trigram": {
            "type": "text",
            "analyzer": "trigram"
          }
        }
      }
    }
  }
}

PUT books2/_doc/1
{
  "title": "Design Patterns"
}

PUT books2/_doc/2
{
  "title": "Software Architecture Patterns Explained"
}

GET books2/_search
{
  "suggest": {
    "phrase-check": {
      "text": "design paterns",
      "phrase": {
        "field": "title.trigram"
      }
    }
  }
}

GET books2/_search
{
  "suggest": {
    "phrase-check": {
      "text": "design paterns",
      "phrase": {
        "field": "title.trigram",
        "gram_size": 3,
        "highlight": {
          "pre_tag": "<em>",
          "post_tag": "</em>"
        }
      }
    }
  }
}

# RETRIEVE SPECIFIC FIELDS

# Disable source
GET /ecommerce/_search
{
    "_source": false,
    "query": {
        "match_all": {}
  }
}

# source filtering
GET /products/_search
{
  "_source": {
    "includes": ["name", "price", "reviews.*", "supplier.*"],
    "excludes": ["reviews.comment", "supplier.contact_email"]
  },
  "query": {
    "match": {
      "category": "Electronics"
    }
  }
}

GET /ecommerce/_search?pretty
{
    "_source": false,
    "fields": ["customer_last_name", "product*"],
    "query": {
        "match_all": {}
  }
}
