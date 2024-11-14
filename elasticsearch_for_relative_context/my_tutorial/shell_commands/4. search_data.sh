# Search for exact values or ranges
# Full text search
# Vector search (ann or knn)

# SORTING
PUT /my-index-000001
{
  "mappings": {
    "properties": {
      "post_date": { "type": "date" },
      "user": {
        "type": "keyword"
      },
      "name": {
        "type": "keyword"
      },
      "age": { "type": "integer" }
    }
  }
}

GET /my-index-000001/_search
{
  "sort" : [
    { "post_date" : {"order" : "asc", "format": "strict_date_optional_time_nanos"}},
    "user",
    { "name" : "desc" },
    { "age" : "desc" },
    "_score"
  ],
  "query" : {
    "term" : { "user" : "kimchy" }
  }
}

# Elasticsearch supports sorting by array or multi-valued fields. The mode option controls what array value is picked for sorting the document it belongs to. 
# The mode option can have the following values: min, max, sum, avg, median. The default sort mode in the ascending sort order is min — the lowest value is picked. The default sort mode in the descending order is max — the highest value is picked

PUT /my-index-000001/_doc/1?refresh
{
   "product": "chocolate",
   "price": [20, 4]
}

POST /_search
{
   "query" : {
      "term" : { "product" : "chocolate" }
   },
   "sort" : [
      {"price" : {"order" : "asc", "mode" : "avg"}}
   ]
}

# GEO DISTANCE SORTING
GET /_search
{
  "sort" : [
    {
      "_geo_distance" : {
          "pin.location" : [-70, 40],
          "order" : "asc",
          "unit" : "km",
          "mode" : "min",
          "distance_type" : "arc",
          "ignore_unmapped": true
      }
    }
  ],
  "query" : {
    "term" : { "user" : "kimchy" }
  }
}

# PAGINATE
# Default returns 10

GET /_search
{
  "from": 5,
  "size": 20,
  "query": {
    "match": {
      "user.id": "kimchy"
    }
  }
}

#By default, you cannot use from and size to page through more than 10,000 hits. This limit is a safeguard set by the index.max_result_window index setting. If you need to page through more than 10,000 hits, use the search_after parameter instead.

# Scroll search results
# While a search request returns a single “page” of results, the scroll API can be used to retrieve large numbers of results (or even all results) from a single search request, in much the same way as you would use a cursor on a traditional database.

POST /my-index-000001/_search?scroll=1m
{
  "size": 100,
  "query": {
    "match": {
      "message": "foo"
    }
  }
}

# The result from the above request includes a _scroll_id, which should be passed to the scroll API in order to retrieve the next batch of results.

POST /_search/scroll                                                               
{
  "scroll" : "1m",                                                                 
  "scroll_id" : "DXF1ZXJ5QW5kRmV0Y2gBAAAAAAAAAD4WYm9laVYtZndUQlNsdDcwakFMNjU1QQ==" 
}

# RETRIEVE SPECIFIC FIELDS
POST my-index-000001/_search
{
  "query": {
    "match": {
      "user.id": "kimchy"
    }
  },
  "fields": [
    "user.id",
    "http.response.*",         
    {
      "field": "@timestamp",
      "format": "epoch_millis" 
    }
  ],
  "_source": false
}

# EXCLUDE SOURCE
POST my-index-000001/_search
{
  "fields": ["*"],
  "_source": false
}

# FINER CONTROL OVER SOURCE
GET /_search
{
  "_source": {
    "includes": [ "obj1.*", "obj2.*" ],
    "excludes": [ "*.description" ]
  },
  "query": {
    "term": {
      "user.id": "kimchy"
    }
  }
}

# REMEMBER DOC_VALUE FIELD (the ones used to stored in a column-based structure on disk for aggregations)
# Just another way to get _source fields
GET my-index-000001/_search
{
  "query": {
    "match": {
      "user.id": "kimchy"
    }
  },
  "docvalue_fields": [
    "user.id",
    "http.response.*", 
    {
      "field": "date",
      "format": "epoch_millis" 
    }
  ]
}

# SEARCH MULTIPLE INDICES
GET /my-index-000001,my-index-000002/_search
{
  "query": {
    "match": {
      "user.id": "kimchy"
    }
  }
}

GET /my-index-*/_search
{
  "query": {
    "match": {
      "user.id": "kimchy"
    }
  }
}

# INDEX BOOST
# When searching multiple indices, you can use the indices_boost parameter to boost results from one or more specified indices. This is useful when hits coming from some indices matter more than hits from other

GET /_search
{
  "indices_boost": [
    { "my-index-000001": 1.4 },
    { "my-index-000002": 1.3 }
  ]
}

# COLLAPSE SEARCH RESULTS
GET my-index-000001/_search
{
  "query": {
    "match": {
      "message": "GET /search"
    }
  },
  "collapse": {
    "field": "user.id"         
  },
  "sort": [
    {
      "http.response.bytes": { 
        "order": "desc"
      }
    }
  ],
  "from": 0                    
}

# EXPAND COLLAPSE RESULTS
GET /my-index-000001/_search
{
  "query": {
    "match": {
      "message": "GET /search"
    }
  },
  "collapse": {
    "field": "user.id",                       
    "inner_hits": {
      "name": "most_recent",                  
      "size": 5,                              
      "sort": [ { "@timestamp": "desc" } ]    
    },
    "max_concurrent_group_searches": 4        
  },
  "sort": [
    {
      "http.response.bytes": {
        "order": "desc"
      }
    }
  ]
}

# FILTER SEARCH RESULTS
# You can use two methods to filter search results:

#     Use a boolean query with a filter clause. Search requests apply boolean filters to both search hits and aggregations.

#     Use the search API’s post_filter parameter. Search requests apply post filters only to search hits, not aggregations. You can use a post filter to calculate aggregations based on a broader result set, and then further narrow the results.

#     You can also rescore hits after the post filter to improve relevance and reorder results.

# HIGHLIGHTING
GET /_search
{
  "query": {
    "match": { "content": "kimchy" }
  },
  "highlight": {
    "fields": {
      "content": {}
    }
  }
}

# USING OTHER DATA SOURCES

# match, match_all, multi_match, term, bool, filter
# Use Cases
# Use match for standard full-text search on a single field.
# Use match_all when you need all documents, often combined with filters or aggregations.
# Use multi_match for searching across multiple fields with the same query string.
# Use bool for complex queries combining multiple conditions.

# Performance Considerations
# match_all is the fastest query type, but returns all documents.
# For exact value matching, term queries are more efficient than match queries.
# Bool queries can be optimized by using filter context for clauses that don't need scoring.
# Multi_match queries can be less efficient than individual match queries if not optimized properly.

# In bool: must ~ AND, should ~ OR (gives higher score to matched documents), must_not ~ exclusions

# query {..} and filter {..} can be nested both ways

PUT /tasks
{
    "mappings": {
      "dynamic_date_formats": [ "MMM dd yyyy||MM/dd/yyyy||MMM d yyyy"],
      "properties": {
        "FIRST_SEEN_DATE": {
          "type": "date",
          "format": "MMM dd yyyy||MM/dd/yyyy||MMM d yyyy"
        }
      }
    }
}

POST /tasks/_doc/1
{
  "TASK_NAME": "App & code optimization(1)",
  "RELATED_AI_DATA_NAMES_LIST": [
    "App Builder Pro"
  ],
  "RELATED_TASKS_NAMES_LIST": [
    "Code optimization",
    "AppStore optimization",
    "Software performance optimization",
    "Programming language optimization",
    "App development & deployment",
    "App development",
    "Performance optimization",
    "Ui5 code optimization",
    "Java code optimization",
    "Multilingual code optimization",
    "App design",
    "Project optimization",
    "React code optimization",
    "Swift code optimization",
    "Routine optimization",
    "Content optimization",
    "Model optimization",
    "App modernization",
    "App development guidance",
    "App development automation",
    "Blockchain code optimization",
    "Code refactoring",
    "Code quality improvement"
  ],
  "FIRST_SEEN_DATE": "Jan 8 2024",
  "RELATED_AI_DATA_IDS_LIST": [
    "36571"
  ]
}

POST /tasks/_doc/2
{
  "TASK_NAME": "Blockchain code optimization(1)",
  "RELATED_AI_DATA_NAMES_LIST": [
    "Solidity Sage"
  ],
  "RELATED_TASKS_NAMES_LIST": [
    "Blockchain coding support",
    "Code optimization",
    "Programming language optimization",
    "App & code optimization",
    "Blockchain analytics",
    "Swift code optimization",
    "Blockchain data analysis",
    "React code optimization",
    "Blockchain transactions analysis",
    "Blockchain education",
    "Multilingual code optimization",
    "Blockchain development consulting",
    "Code simplification",
    "Bitcoin simplification",
    "Blockchain security",
    "Code complexity analysis",
    "Instruction optimization",
    "Java code optimization",
    "Blockchain consulting",
    "Smart contract programming"
  ],
  "FIRST_SEEN_DATE": "Dec 23 2023",
  "RELATED_AI_DATA_IDS_LIST": [
    "18879"
  ]
}



POST /tasks/_doc/3
{
  "TASK_NAME": "Building codes research(3)",
  "RELATED_AI_DATA_NAMES_LIST": [
    "CA Title 24 Wizard",
    "Utah Building Code GPT",
    "UpCodes"
  ],
  "RELATED_TASKS_NAMES_LIST": [
    "Civil engineering research",
    "Building safety guidance",
    "Building design",
    "Building analysis",
    "Research papers coding",
    "Computer science research",
    "Sanitary engineering research",
    "Code testing",
    "Mechanical engineering research",
    "Construction project analysis",
    "Building advice",
    "Sustainable construction guidance",
    "Research papers exploration",
    "Engineering inquiries",
    "Academic research",
    "Research papers analysis",
    "Architectural insights",
    "Code security analysis",
    "Research",
    "Construction documents Q&A",
    "Code search",
    "Theses research",
    "Project coding",
    "Construction guidance",
    "Sustainable architecture guidance"
  ],
  "FIRST_SEEN_DATE": "Jul 2 2023",
  "RELATED_AI_DATA_IDS_LIST": [
    "15514",
    "25068",
    "5807"
  ]
}

GET tasks/_mapping

POST tasks/_search
{
  "query": {
    "match_all": {}
  }
}

# MATCH_ALL

GET tasks/_search
{
  "query": {
    "match_all": {}
  }
}



# The key differences between using GET and POST for search queries are:
# Parameter limitations:
# GET requests have limitations on URL length (typically 2000-8000 characters), which can restrict complex search queries with many parameters.
# POST requests can send larger amounts of data in the request body, allowing for more complex search criteria.
# Caching:
# GET requests are cacheable by default, which can improve performance for repeated searches.
# POST requests are not cached by default, though this can be changed with additional headers.
# Bookmarking and sharing:
# GET requests put parameters in the URL, making searches easy to bookmark and share.
# POST request parameters are in the body, so searches are not as easily bookmarked or shared.
# Security:
# GET parameters are visible in the URL, which may expose sensitive data.
# POST parameters are in the request body, providing slightly more security for sensitive search criteria.
# Idempotency:
# GET is idempotent, meaning repeated requests should produce the same result.
# POST is not idempotent by default.
# Browser behavior:
# Browsers handle back/forward navigation and history better with GET requests.
# POST may cause issues with page reloads and navigation.
# Best practices:
# Use GET for simple searches with few parameters.
# Consider POST for complex searches, very long queries, or when sending sensitive data.
# Some APIs use POST to a /search endpoint as a compromise.

# MATCH vs. MATCH_PHRASE vs. MATCH_PHRASE_PREFIX vs. TERM

POST tasks/_search
{
  "query": {
    "match": {
      "RELATED_TASKS_NAMES_LIST": "Code optimization"
    }
  },
  "fields" : ["*"]
}

# This also matches "Code optimization" as a substring (think about tokenization done by analyzer)
POST tasks/_search
{
  "query": {
    "match": {
      "RELATED_TASKS_NAMES_LIST": "Ui5 code optimization"
    }
  },
  "fields" : ["*"]
}


# This returns only 1 document (since only document 1 has ui5 as a token)
POST tasks/_search
{
  "query": {
    "match": {
      "RELATED_TASKS_NAMES_LIST": "Ui5"
    }
  },
  "fields" : ["*"]
}

# If you want exact match, you can use .keyword field since RELATED_TASKS_NAMES_LIST is also a keyword field
POST tasks/_search
{
  "query": {
    "match": {
      "RELATED_TASKS_NAMES_LIST.keyword": "Ui5 code optimization"
    }
  },
  "fields" : ["*"]
}

# OR you could use match_phrase
POST tasks/_search
{
  "query": {
    "match_phrase": {
      "RELATED_TASKS_NAMES_LIST.keyword": "Ui5 code optimization"
    }
  },
  "fields" : ["*"]
}

# match_phrase with slop - don't care if certain words are in between, including reverse
# slop = 1 means at most 1 word can be in between 

POST tasks/_search
{
  "query": {
    "match_phrase": {
      "RELATED_TASKS_NAMES_LIST": { 
        "query": "Ui5 optimization",
        "slop": 1
      }
    }
  },
  "fields" : ["*"]
}

# To match in reverse, slop value should be 2 greater than number of words in between
POST tasks/_search
{
  "query": {
    "match_phrase": {
      "RELATED_TASKS_NAMES_LIST": { 
        "query": "optimization Ui5",
        "slop": 3
      }
    }
  },
  "fields" : ["*"]
}

# PROXIMITY SEARCH
# Find documents that have tokens "code" and "optimization" within n words
# documents that have tokens "code" and "optimization" within n words, but score the ones that are more closer

POST tasks/_search
{
  "query": {
    "match_phrase": {
      "RELATED_TASKS_NAMES_LIST": { 
        "query": "code optimization",
        "slop": 100
      }
    }
  },
  "fields" : ["*"]
}


# match_phrase_prefix is useful when you want to match a prefix of a phrase
POST tasks/_search
{
  "query": {
    "match_phrase_prefix": {
      "RELATED_TASKS_NAMES_LIST": "theses"
    }
  },
  "fields" : ["*"]
}

# TERM
# Term Query:
# Matches documents that contain an exact term in a specified field
# Searches for a single value
# Does not analyze the search term
POST tasks/_search
{
  "query": {
    "term": {
      "RELATED_TASKS_NAMES_LIST": {
        "value": "theses"
      }
    }
  },
  "fields" : ["RELATED_TASKS_NAMES_LIST"]
}

POST tasks/_search
{
  "query": {
    "term": {
      "RELATED_TASKS_NAMES_LIST": "theses"
    }
  },
  "fields" : ["RELATED_TASKS_NAMES_LIST"]
}

# at least one term match
POST tasks/_search
{
  "query": {
    "terms": {
      "RELATED_TASKS_NAMES_LIST": ["theses","Multilingual"]
    }
  },
  "fields" : ["RELATED_TASKS_NAMES_LIST"]
}

# FILTER
# Applies in the last stage of resultset (i.e. doesn't give server performance benefits, just prunes)

POST tasks/_search
{
  "query": {
    "bool": {
      "filter": {
        "term": {
          "RELATED_TASKS_NAMES_LIST": "theses"
        }
      }
    }
  },
  "fields" : ["RELATED_TASKS_NAMES_LIST"]
}

# BOOL
# Must, Must_not, Should
POST tasks/_search
{
    "query" : {
        "bool" : {
            "must" : {
                "match" : {
                    "RELATED_TASKS_NAMES_LIST" : "code" 
                }
            },
            "filter" : {
                "range" : {
                    "FIRST_SEEN_DATE": { "gt" : "Jan 7 2024" } 
                }
            }
        }
    }
}

# MIX-MATCH
# Documents must satisfy all conditions in the "must" array
# Documents matching "should" conditions get a higher score
# Documents matching "must_not" conditions are excluded
# "minimum_should_match" ensures at least one "should" condition is met

GET /tasks/_search
{
  "query": {
    "bool": {
      "must": [
        { "match": { "RELATED_TASKS_NAMES_LIST": "code" } },
        { "range": { "FIRST_SEEN_DATE": { "gte": "Jan 1 2023"} } }
      ],
      "should": [
        { "term": { "RELATED_TASKS_NAMES_LIST.keyword": "Ui5 code optimization" } }
      ],
      "must_not": [
        { "term": { "RELATED_AI_DATA_IDS_LIST.keyword": "12345" } }
      ],
      "minimum_should_match": 1
    }
  }
}

# PAGINATION
# from: 0, size: 10
# Deep pagination can be quite performance heavy, every results must be retrieved, scored and sorted

POST tasks/_search
{
  "from": 0,
  "size": 2,
  "query": {
    "match_all": {}
  }
}


# SORTING
POST tasks/_search
{
  "sort": {
    "_score": {"order": "asc"}
  },
  "query": {
    "match": {
      "RELATED_TASKS_NAMES_LIST": "code"
    }
  }
}

POST tasks/_search
{
  "sort": {
    "FIRST_SEEN_DATE": {"order": "desc"}
  },
  "query": {
    "match": {
      "RELATED_TASKS_NAMES_LIST": "code"
    }
  }
}

POST tasks/_search
{
  "sort": [
    {"FIRST_SEEN_DATE": "desc"},
    {"_score": "asc"}
  ],
  "query": {
    "match": {
      "RELATED_TASKS_NAMES_LIST": "code"
    }
  }
}

# cannot sort on text field , exception: illegal_argument_exception
# because text is already split into terms/tokens and can't be sorted
POST tasks/_search
{
  "sort": {
    "RELATED_AI_DATA_NAMES_LIST": {"order": "desc"}
  },
  "query": {
    "match": {
      "RELATED_TASKS_NAMES_LIST": "code"
    }
  }
}

# workaround: use keyword field
# assumes that RELATED_AI_DATA_NAMES_LIST is a also a keyword field
# on an existing index, for the sort field that is already analyzed only as text, it cannot be updated unless index is deleted and mappings defined again
POST tasks/_search
{
  "sort": {
    "RELATED_AI_DATA_NAMES_LIST.keyword": {"order": "desc"}
  },
  "query": {
    "match": {
      "RELATED_TASKS_NAMES_LIST": "code"
    }
  }
}


# FUZZY MATCHING - ONLY TERM LEVEL QUERY
# Fuzzy matching is a technique used in search queries to find results that are similar to the search term, even if the term is misspelled or has minor variations. Fuzzy matching can be useful for handling typos, variations in spelling, or other small differences in text data.
# Levnshtein edit distance: number of single-character edits (insertions, deletions, or substitutions) required to change one word into another

# An edit distance is the number of one-character changes needed to turn one term into another. These changes can include:

# Changing a character (box → fox)
# Removing a character (black → lack)
# Inserting a character (sic → sick)
# Transposing two adjacent characters (act → cat)


# Below will not work since RELATED_TASKS_NAMES_LIST is text
POST tasks/_search
{
  "query": {
    "fuzzy": {
      "RELATED_TASKS_NAMES_LIST": {
        "value": "code optmization",
        "fuzziness": "AUTO"
      }
    }
  }
}

# Below will work since RELATED_TASKS_NAMES_LIST.keyword is keyword
POST tasks/_search
{
  "query": {
    "fuzzy": {
      "RELATED_TASKS_NAMES_LIST.keyword": {
        "value": "code optmization",
        "fuzziness": "AUTO"
      }
    }
  }
}

#https://www.elastic.co/guide/en/elasticsearch/reference/current/common-options.html#fuzziness
# Generally leave AUTO as value for fuzziness

GET tasks/_search
{
  "query": {
    "fuzzy": {
      "RELATED_TASKS_NAMES_LIST.keyword": {
        "value": "ki",
        "fuzziness": "AUTO",
        "max_expansions": 50, #Maximum number of variations created
        "prefix_length": 3,  # first 3 characters are not considered for fuzz
        "transpositions": true,
        "rewrite": "constant_score_blended"
      }
    }
  }
}



