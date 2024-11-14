# BELOW FROM OFFICIAL ELASTICSEARCH DOCUMENTATION - https://www.elastic.co/guide/en/elasticsearch/reference/current/query-dsl.html
# QUERY CONTEXT: In the query context, a query clause answers the question “How well does this document match this query clause?” Besides deciding whether or not the document matches, the query clause also calculates a relevance score in the _score metadata field
# FILTER CONTEXT: In a filter context, a query clause answers the question “Does this document match this query clause?” The answer is a simple Yes or No — no scores are calculated. Filter context is mostly used for filtering structured data

GET /_search
{
  "query": { 
    "bool": { 
      "must": [
        { "match": { "RELATED_TASKS_NAMES_LIST":   "code"        }},
        { "match": { "TASK_NAME": "code" }}
      ],
      "filter": [ 
        { "range": { "FIRST_SEEN_DATE": { "gte": "01/01/2023" }}}
      ]
    }
  }
}

# COMPOUND QUERIES

## BOOL QUERY

POST _search
{
  "query": {
    "bool" : {
      "must" : {
        "match" : { "TASK_NAME" : "code" }
      },
      "filter": {
        "match" : { "RELATED_TASKS_NAMES_LIST" : "code" }
      },
      "must_not" : {
        "range" : {
          "FIRST_SEEN_DATE" : { "gte" : "02/01/2024" }
        }
      },
      "should" : [
        { "term" : { "RELATED_AI_DATA_NAMES_LIST.keyword" : "App Builder Pro" } }
      ],
      "minimum_should_match" : 1,
      "boost" : 1.0
    }
  }
}

# bool filter: Queries specified under the filter element have no effect on scoring — scores are returned as 0
# match_all gives score of 1.0

GET tasks/_search
{
  "query": {
    "bool": {
      "filter": {
        "term": {
          "RELATED_TASKS_NAMES_LIST.keyword": "Code optimization"
        }
      }
    }
  }
}

GET tasks/_search
{
  "query": {
    "bool": {
      "must": {
        "match_all": {}
      },
      "filter": {
        "term": {
          "RELATED_TASKS_NAMES_LIST.keyword": "Code optimization"
        }
      }
    }
  }
}

# constant_score does the same as above score=1
GET tasks/_search
{
  "query": {
    "constant_score": {
      "filter": {
        "term": {
          "RELATED_TASKS_NAMES_LIST.keyword": "Code optimization"
        }
      }
    }
  }
}

# you can set a boost value to the constant_score query
GET tasks/_search
{
  "query": {
    "constant_score": {
      "filter": {
        "term": {
          "RELATED_TASKS_NAMES_LIST.keyword": "Code optimization"
        }
      },
      "boost": 1.2
    }
  }
}

# NAMED QUERIES
# Each query accepts a _name in its top level definition. You can use named queries to track which queries matched returned documents. If named queries are used, the response includes a matched_queries property for each hit.

POST _search
{
  "query": {
    "bool" : {
      "must" : {
        "match" : { "TASK_NAME" : {"query":"code","_name":"match_task_name"} }
      },
      "filter": {
        "match" : { "RELATED_TASKS_NAMES_LIST" : {"query":"code","_name":"filter_task_related"} }
      },
      "must_not" : {
        "range" : {
          "FIRST_SEEN_DATE" : { "gte" : "02/01/2024","_name":"date_gt_2024" }
        }
      },
      "should" : [
        { "term" : { "RELATED_AI_DATA_NAMES_LIST.keyword" : "App Builder Pro"}}
      ],
      "minimum_should_match" : 1,
      "boost" : 1.0
    }
  }
}

# shows score contributed by matched clauses
POST _search?include_named_queries_score
{
  "query": {
    "bool" : {
      "must" : {
        "match" : { "TASK_NAME" : {"query":"code","_name":"match_task_name"} }
      },
      "filter": {
        "match" : { "RELATED_TASKS_NAMES_LIST" : {"query":"code","_name":"filter_task_related"} }
      },
      "must_not" : {
        "range" : {
          "FIRST_SEEN_DATE" : { "gte" : "02/01/2024","_name":"date_gt_2024" }
        }
      },
      "should" : [
        { "term" : { "RELATED_AI_DATA_NAMES_LIST.keyword" : "App Builder Pro"}}
      ],
      "minimum_should_match" : 1,
      "boost" : 1.0
    }
  }
}

# BOOSTING QUERY
#Returns documents matching a positive query while reducing the relevance score of documents that also match a negative query.
#You can use the boosting query to demote certain documents without excluding them from the search results
#Use case: Give higher scores to exact phrase matches while still allowing partial matches.

# Use case :1 Give higher score to task_name (raise to 3) for the same match query. Observer with and without boost
GET /tasks/_search
{
  "query": {
    "multi_match": {
      "query": "code",
      "fields": ["RELATED_TASKS_NAMES_LIST", "TASK_NAME^3"]
    }
  }
}

# Use case 2: Boosting recent documents / recency defined by another field

GET /tasks/_search
{
  "query": {
    "function_score": {
      "query": {
        "match": {
          "RELATED_TASKS_NAMES_LIST": "code"
        }
      },
      "functions": [
        {
          "exp": {
            "FIRST_SEEN_DATE": {
              "scale": "30d",
              "decay": 0.5
            }
          }
        }
      ]
    }
  }
}

# Use case 3: Boosting exact match
# Observe the _score before and after

GET /tasks/_search
{
  "query": {
    "match": {
      "RELATED_TASKS_NAMES_LIST": "code"
    }
  }
}

GET /tasks/_search
{
  "query": {
    "bool": {
      "should": [
        {
          "match": {
            "RELATED_TASKS_NAMES_LIST": "code"
          }
        },
        {
          "match_phrase": {
            "RELATED_TASKS_NAMES_LIST": {
              "query": "Model optimization",
              "boost": 2
            }
          }
        }
      ]
    }
  }
}

# DISJUNCTION MAX QUERY
#If a returned document matches multiple query clauses, the dis_max query assigns the document the highest relevance score from any matching clause, plus a tie breaking increment for any additional matching subqueries.

# use case 1: Multi-field text search : When searching across multiple text fields with the same query, dis_max can help prioritize documents where the terms appear in a single field rather than spread across multiple fields.
# e.g. maybe you have a unique skill set: [java spring docker] and you want the find the jobs that have those skills in job_description and job_title fields, you can use dis_max query to give higher score to documents where all the skills are in one field

#use case 2: Handling synonyms or related terms:
# When searching for synonyms or related terms across different fields.

{
  "query": {
    "dis_max": {
      "queries": [
        { "match": { "name": "smartphone" }},
        { "match": { "description": "mobile phone" }}
      ]
    }
  }
}

# use case 3: Combining different query types:
# When you want to search using different query types but take the best matching one.
{
  "query": {
    "dis_max": {
      "queries": [
        { "match": { "title": "elasticsearch guide" }},
        { "match_phrase": { "body": "how to use elasticsearch" }}
      ]
    }
  }
}

# use case 4: cross-field entity search: When searching for entities that might appear in different fields.
{
  "query": {
    "dis_max": {
      "queries": [
        { "match": { "author": "john smith" }},
        { "match": { "contributor": "john smith" }}
      ]
    }
  }
}

#use case 5: boosting specific fields
# When you want to search across multiple fields but give more weight to matches in certain fields.
{
  "query": {
    "dis_max": {
      "queries": [
        { "match": { "title": {"query": "elasticsearch", "boost": 3} }},
        { "match": { "body": "elasticsearch" }}
      ]
    }
  }
}

# FUNCTION SCORE QUERY
#The function_score allows you to modify the score of documents that are retrieved by a query. This can be useful if, for example, a score function is computationally expensive and it is sufficient to compute the score on a filtered set of documents.
#https://www.elastic.co/guide/en/elasticsearch/reference/current/query-dsl-function-score-query.html

# Various function scores : https://www.elastic.co/guide/en/elasticsearch/reference/current/query-dsl-function-score-query.html#score-functions

GET /_search
{
  "query": {
    "function_score": {
      "query": { "match_all": {} },
      "boost": "5",
      "random_score": {}, 
      "boost_mode": "multiply"
    }
  }
}

# optional score based on filter match
GET /_search
{
  "query": {
    "function_score": {
      "query": { "match_all": {} },
      "boost": "5", 
      "functions": [
        {
          "filter": { "match": { "test": "bar" } },
          "random_score": {}, 
          "weight": 23
        },
        {
          "filter": { "match": { "test": "cat" } },
          "weight": 42
        }
      ],
      "max_boost": 42,
      "score_mode": "max",
      "boost_mode": "multiply",
      "min_score": 42
    }
  }
}

# The function_score query provides several types of score functions.

#     script_score
#     weight
#     random_score
#     field_value_factor
#     decay functions: gauss, linear, exp



# script score
#The script_score function allows you to wrap another query and customize the scoring of it optionally with a computation derived from other numeric field values in the doc using a script expression
GET /_search
{
  "query": {
    "function_score": {
      "query": {
        "match": { "message": "elasticsearch" }
      },
      "script_score": {
        "script": {
          "source": "Math.log(2 + doc['my-int'].value)"
        }
      }
    }
  }
}

# FIELD VALUE FACTOR for function_score
# The field_value_factor function allows you to use a field from a document to influence the score. It’s similar to using the script_score function, however, it avoids the overhead of scripting

GET /_search
{
  "query": {
    "function_score": {
      "field_value_factor": {
        "field": "my-int",
        "factor": 1.2,
        "modifier": "sqrt",
        "missing": 1
      }
    }
  }
}
# Which will translate into the following formula for scoring:

# sqrt(1.2 * doc['my-int'].value)

# DECAY FUNCTIONS
# supported fields: numeric, geopoint and date
#Decay functions score a document with a function that decays depending on the distance of a numeric field value of the document from a user given origin. This is similar to a range query, but with smooth edges instead of boxes.

"DECAY_FUNCTION": { 
    "FIELD_NAME": { 
          "origin": "11, 12",
          "scale": "2km",
          "offset": "0km",
          "decay": 0.33
    }
}

# Detailed example

# Suppose you are searching for a hotel in a certain town. Your budget is limited. Also, you would like the hotel to be close to the town center, so the farther the hotel is from the desired location the less likely you are to check in.

# You would like the query results that match your criterion (for example, "hotel, Nancy, non-smoker") to be scored with respect to distance to the town center and also the price.

# Intuitively, you would like to define the town center as the origin and maybe you are willing to walk 2km to the town center from the hotel.
# In this case your origin for the location field is the town center and the scale is ~2km.

# If your budget is low, you would probably prefer something cheap above something expensive. For the price field, the origin would be 0 Euros and the scale depends on how much you are willing to pay, for example 20 Euros.

# In this example, the fields might be called "price" for the price of the hotel and "location" for the coordinates of this hotel.

# The function for price in this case would be
"gauss": {  #This decay function could also be linear or exp.
    "price": {
          "origin": "0",
          "scale": "20"
    }
}
# and for location:
"gauss": { 
    "location": {
          "origin": "11, 12",
          "scale": "2km"
    }
}

#Suppose you want to multiply these two functions on the original score, the request would look like this

GET /_search
{
  "query": {
    "function_score": {
      "functions": [
        {
          "gauss": {
            "price": {
              "origin": "0",
              "scale": "20"
            }
          }
        },
        {
          "gauss": {
            "location": {
              "origin": "11, 12",
              "scale": "2km"
            }
          }
        }
      ],
      "query": {
        "match": {
          "properties": "balcony"
        }
      },
      "score_mode": "multiply"
    }
  }
}
