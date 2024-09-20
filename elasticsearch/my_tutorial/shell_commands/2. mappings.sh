# Only dynamic mapping (default)
PUT /tasks

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

POST /tasks/_doc/4
{"TASK_NAME":"C code mentoring(1)","RELATED_AI_DATA_NAMES_LIST":["C Code Mentor"],"RELATED_TASKS_NAMES_LIST":["C coding assistance", "C programming assistance", "Code mentoring", "C coding interviews", "C++ mentoring", "C programming lessons", "Code tutoring", "C++ assistance", "C programming pointers", "Code assistance", "Coding help", "Javascript mentoring", "Coding tutor", "Code accessibility", "Code quality improvement", "Coding mentorship", "C++ tutoring", "Code fixing", "Code optimization", "Code formatting", "Code privacy", "Code simplification", "C## learning"],"FIRST_SEEN_DATE":"Dec 28 2023","RELATED_AI_DATA_IDS_LIST":["26361"]}

GET /tasks/_mapping

## date detection
## https://www.digitalocean.com/community/tutorials/java-simpledateformat-java-date-format

DELETE /tasks
PUT /tasks
{
    "mappings": {
      "dynamic_date_formats": [ "MMM dd yyyy||MM/dd/yyyy||MMM d yyyy"]
    }
}

PUT /tasks
{
    "mappings": {
      "dynamic_date_formats": ["MMM dd yyyy", "MM/dd/yyyy", "MMM d yyyy"]
    }
}

GET /tasks/_mapping

PUT /tasks
{
    "mappings": {
      "dynamic_date_formats": [ "MMM dd yyyy||MM/dd/yyyy"],
      "properties": {
        "FIRST_SEEN_DATE": {
          "type": "date",
          "format": "MMM dd yyyy||MM/dd/yyyy"
        }
      }
    }
  }

GET /tasks/_mapping


# NUMERIC DETECTION - only when index is being created (cannot update after index is created)
# Without numeric detection, RELATED_AI_DATA_IDS_LIST will be detected as string. With, as long
PUT tasks
{
  "mappings": {
    "numeric_detection": true
  }
}

PUT /tasks
{
    "mappings": {
      "numeric_detection": true,
      "dynamic_date_formats": [ "MMM dd yyyy||MM/dd/yyyy||MMM d yyyy"],
      "properties": {
        "FIRST_SEEN_DATE": {
          "type": "date",
          "format": "MMM dd yyyy||MM/dd/yyyy||MMM d yyyy"
        },
        "RELATED_TASKS_NAMES_LIST": {
          "type": "keyword"
        }
      }
    }
}

## DYNAMIC TEMPLATES - advanced
PUT my-index-000001/
{
  "mappings": {
    "dynamic_templates": [
      {
        "strings_as_ip": {
          "match_mapping_type": "string",
          "match": "ip*",
          "runtime": {
            "type": "ip"
          }
        }
      }
    ]
  }
}

# DOC_VALUES attribute for fields
# Most fields are indexed by default, which makes them searchable. The inverted index allows queries to look up the search term in unique sorted list of terms, and from that immediately have access to the list of documents that contain the term.

# Sorting, aggregations, and access to field values in scripts requires a different data access pattern. Instead of looking up the term and finding documents, we need to be able to look up the document and find the terms that it has in a field.

# Doc values are the on-disk data structure, built at document index time, which makes this data access pattern possible. They store the same values as the _source but in a column-oriented fashion that is way more efficient for sorting and aggregations. Doc values are supported on almost all field types, with the notable exception of text and annotated_text fields.

## aggregations again -- not following the 8.15 documentation path, this below aggregation section should be elswhere
PUT /tasks
{
    "mappings": {
      "dynamic_date_formats": [ "MMM dd yyyy||MM/dd/yyyy||MMM d yyyy"],
      "properties": {
        "FIRST_SEEN_DATE": {
          "type": "date",
          "format": "MMM dd yyyy||MM/dd/yyyy||MMM d yyyy"
        },
        "RELATED_TASKS_NAMES_LIST": {
          "type": "keyword"
        }
      }
    }
}

# POST all tasks above

GET /tasks/_search
{
  "aggs": {
    "all_tasks": {
      "terms": { "field": "RELATED_TASKS_NAMES_LIST" }
    }
  }
}

# Note dynamic mapping already creates a keyword field for RELATED_TASKS_NAMES_LIST, so no need to specify it again (a key can have multiple field types called multifield feature: which we will see later)
# You can see the mapping and get aggregations on the field
GET tasks/_search
{
  "aggs": {
    "all_ais": {
      "terms": { "field": "RELATED_AI_DATA_NAMES_LIST.keyword", "size": 20 }
    }
  }
}


## Not all buckets will be returned , because default buckets are 10. Increase using size
## Global search.max_buckets controls the upper value to 65,536

GET /tasks/_search
{
  "aggs": {
    "all_tasks": {
      "terms": {
        "field": "RELATED_TASKS_NAMES_LIST",
        "size": 100
      }
    }
  }
}

# How to know what size to use? See the sum_other_doc_count key, it will tell you how many buckets were not returned


## EXPLICIT MAPPINGS

PUT /tasks
{
    "mappings": {
      "properties": {
        "TASK_NAME":{
          "type": "text"
        },
        "FIRST_SEEN_DATE": {
          "type": "date",
          "format": "MMM dd yyyy||MM/dd/yyyy||MMM d yyyy"
        },
        "RELATED_TASKS_NAMES_LIST": {
          "type": "keyword"
        },
        "RELATED_AI_DATA_IDS_LIST":{
          "type":"integer"
        }
      }
    }
}

GET /tasks/_mapping

## See specific field mapping
GET /tasks/_mapping/field/TASK_NAME

# Update type mapping of a field after index is created is generally not recommended.Index might get invalidated etc.
# For e.g. we can update the mapping parameters - https://www.elastic.co/guide/en/elasticsearch/reference/current/mapping-params.html

# RUNTIME FIELDS
# A runtime field is a field that is evaluated at query time. Runtime fields enable you to:

#     Add fields to existing documents without reindexing your data
#     Start working with your data without understanding how it’s structured
#     Override the value returned from an indexed field at query time
#     Define fields for a specific use without modifying the underlying schema
# Runtime fields won’t display in _source

# USE CASE
# Explore your data with runtime fields
# Consider a large set of log data that you want to extract fields from. Indexing the data is time consuming and uses a lot of disk space, and you just want to explore the data structure without committing to a schema up front.
# You know that your log data contains specific fields that you want to extract. In this case, we want to focus on the @timestamp and message fields. By using runtime fields, you can define scripts to calculate values at search time for these fields.

PUT /my-index-000001/
{
  "mappings": {
    "properties": {
      "@timestamp": {
        "format": "strict_date_optional_time||epoch_second",
        "type": "date"
      },
      "message": {
        "type": "wildcard"
      }
    }
  }
}

# INGEST SOME DATA

POST /my-index-000001/_bulk?refresh
{"index":{}}
{"timestamp":"2020-04-30T14:30:17-05:00","message":"40.135.0.0 - - [30/Apr/2020:14:30:17 -0500] \"GET /images/hm_bg.jpg HTTP/1.0\" 200 24736"}
{"index":{}}
{"timestamp":"2020-04-30T14:30:53-05:00","message":"232.0.0.0 - - [30/Apr/2020:14:30:53 -0500] \"GET /images/hm_bg.jpg HTTP/1.0\" 200 24736"}
{"index":{}}
{"timestamp":"2020-04-30T14:31:12-05:00","message":"26.1.0.0 - - [30/Apr/2020:14:31:12 -0500] \"GET /images/hm_bg.jpg HTTP/1.0\" 200 24736"}
{"index":{}}
{"timestamp":"2020-04-30T14:31:19-05:00","message":"247.37.0.0 - - [30/Apr/2020:14:31:19 -0500] \"GET /french/splash_inet.html HTTP/1.0\" 200 3781"}
{"index":{}}
{"timestamp":"2020-04-30T14:31:22-05:00","message":"247.37.0.0 - - [30/Apr/2020:14:31:22 -0500] \"GET /images/hm_nbg.jpg HTTP/1.0\" 304 0"}
{"index":{}}
{"timestamp":"2020-04-30T14:31:27-05:00","message":"252.0.0.0 - - [30/Apr/2020:14:31:27 -0500] \"GET /images/hm_bg.jpg HTTP/1.0\" 200 24736"}
{"index":{}}
{"timestamp":"2020-04-30T14:31:28-05:00","message":"not a valid apache log"}


GET /my-index-000001

# DEFINE RUNTIME FIELD WITH GROK PATTERN
PUT my-index-000001/_mappings
{
  "runtime": {
    "http.client_ip": {
      "type": "ip",
      "script": """
        String clientip=grok('%{COMMONAPACHELOG}').extract(doc["message"].value)?.clientip;
        if (clientip != null) emit(clientip); 
      """
    }
  }
}

# OR directly in your search query
GET my-index-000001/_search
{
  "runtime_mappings": {
    "http.clientip": {
      "type": "ip",
      "script": """
        String clientip=grok('%{COMMONAPACHELOG}').extract(doc["message"].value)?.clientip;
        if (clientip != null) emit(clientip);
      """
    }
  },
  "query": {
    "match": {
      "http.clientip": "40.135.0.0"
    }
  },
  "fields" : ["http.clientip"]
}


# composite runtime field
PUT my-index-000001/_mappings
{
  "runtime": {
    "http": {
      "type": "composite",
      "script": "emit(grok(\"%{COMMONAPACHELOG}\").extract(doc[\"message\"].value))",
      "fields": {
        "clientip": {
          "type": "ip"
        },
        "verb": {
          "type": "keyword"
        },
        "response": {
          "type": "long"
        }
      }
    }
  }
}

GET /my-index-000001

GET my-index-000001/_search
{
  "query": {
    "match": {
      "http.clientip": "40.135.0.0"
    }
  },
  "fields" : ["*"]
}

# search for documents within a specific range
GET my-index-000001/_search
{
  "query": {
    "range": {
      "timestamp": {
        "gte": "2020-04-30T14:31:27-05:00"
      }
    }
  }
}

# Define runtime field with dissect pattern
PUT my-index-000001/_mappings
{
  "runtime": {
    "http.client.ip": {
      "type": "ip",
      "script": """
        String clientip=dissect('%{clientip} %{ident} %{auth} [%{@timestamp}] "%{verb} %{request} HTTP/%{httpversion}" %{status} %{size}').extract(doc["message"].value)?.clientip;
        if (clientip != null) emit(clientip);
      """
    }
  }
}

PUT my-index-000001/_mappings
{
  "runtime": {
    "http.responses": {
      "type": "long",
      "script": """
        String response=dissect('%{clientip} %{ident} %{auth} [%{@timestamp}] "%{verb} %{request} HTTP/%{httpversion}" %{response} %{size}').extract(doc["message"].value)?.response;
        if (response != null) emit(Integer.parseInt(response));
      """
    }
  }
}

# FIELD DATA TYPES
# For each field, there are parameters and meta (see documentation)
# See the gexcel sheet for the data types -https://docs.google.com/spreadsheets/d/1Inr5LXFg3MXXATUvstw4ZxgxXp2LDzzvNvTLHYWSKgk/edit?usp=drive_link

# Arrays : In Elasticsearch, arrays do not require a dedicated field data type. 
# Any field can contain zero or more values by default, however, all values in the array must be of the same field type
# When adding a field dynamically, the first value in the array determines the field type. 
# All subsequent values must be of the same data type or it must at least be possible to coerce subsequent values to the same data type.
# Arrays with a mixture of data types are not supported: [ 10, "some string" ]


# MULTI FIELDS
# It is often useful to index the same field in different ways for different purposes. 
# For instance, a string field could be mapped as a text field for full-text search, 
# and as a keyword field for sorting or aggregations. 
# Alternatively, you could index a text field with the standard analyzer, the english analyzer, and the french analyzer.
# This is the purpose of multi-fields. Most field types support multi-fields via the fields parameter

# ALIAS FIELD TYPE
PUT trips
{
  "mappings": {
    "properties": {
      "distance": {
        "type": "long"
      },
      "route_length_miles": {
        "type": "alias",
        "path": "distance" 
      },
      "transit_mode": {
        "type": "keyword"
      }
    }
  }
}

GET _search
{
  "query": {
    "range" : {
      "route_length_miles" : {
        "gte" : 39
      }
    }
  }
}

# There are a few restrictions on the target of an alias:

#     The target must be a concrete field, and not an object or another field alias.
#     The target field must exist at the time the alias is created.
#     If nested objects are defined, a field alias must have the same nested scope as its target.
# Writes to field aliases are not supported

# BINARY FIELD TYPE
# The binary type accepts a binary value as a Base64 encoded string. 
# The field is not stored by default and is not searchable
# newline characters are not allowed in the binary value and will cause an error

# BOOLEAN FIELD TYPE

# COMPLETION FIELD TYPE
# To use the completion suggester, map the field from which you want to generate suggestions as type completion. 
# This indexes the field values for fast completions
PUT music
{
  "mappings": {
    "properties": {
      "suggest": {
        "type": "completion"
      }
    }
  }
}

# DATE FIELD TYPE
# Default date format: "strict_date_optional_time||epoch_millis"
PUT my-index-000001
{
  "mappings": {
    "properties": {
      "date": {
        "type": "date" 
      }
    }
  }
}

PUT my-index-000001/_doc/1
{ "date": "2015-01-01" } 

PUT my-index-000001/_doc/2
{ "date": "2015-01-01T12:10:30Z" } 

PUT my-index-000001/_doc/3
{ "date": 1420070400001 } 

GET my-index-000001/_search
{
  "sort": { "date": "asc"} 
}

# Multiple date formats
PUT my-index-000001
{
  "mappings": {
    "properties": {
      "date": {
        "type":   "date",
        "format": "yyyy-MM-dd HH:mm:ss||yyyy-MM-dd||epoch_millis"
      }
    }
  }
}

# DATE NANOSECONDS
# "strict_date_optional_time_nanos||epoch_millis"
# The date_nanos data type stores dates in nanosecond resolution, which limits its range of dates from roughly 1970 to 2262, as dates are still stored as a long representing nanoseconds since the epoch
# The current unix epoch is 1 jan 1970, and we store time as milliseconds int (which has a max value), it runs out in 2038

# DENSE VECTOR FIELD TYPE
# The dense_vector field type stores dense vectors of numeric values. Dense vector fields are primarily used for k-nearest neighbor (kNN) search

PUT my-index
{
  "mappings": {
    "properties": {
      "my_vector": {
        "type": "dense_vector",
        "dims": 3
      },
      "my_text" : {
        "type" : "keyword"
      }
    }
  }
}

PUT my-index/_doc/1
{
  "my_text" : "text1",
  "my_vector" : [0.5, 10, 6]
}

PUT my-index/_doc/2
{
  "my_text" : "text2",
  "my_vector" : [-0.5, 10, 10]
}

# DEFAULT SIMILARITY IS int8_hnsw. 
# Like most kNN algorithms, HNSW is an approximate method that sacrifices result accuracy for improved speed
PUT my-index-2
{
  "mappings": {
    "properties": {
      "my_vector": {
        "type": "dense_vector",
        "dims": 3,
        "similarity": "dot_product"
      }
    }
  }
}

# Indexing vectors for kNN is expensive, so you can disable indexing
PUT my-index-2
{
  "mappings": {
    "properties": {
      "my_vector": {
        "type": "dense_vector",
        "dims": 3,
        "index": false
      }
    }
  }
}

# The dense_vector type supports quantization to reduce the memory footprint required when searching float vectors
# int8 and int4 are supported
# int4 quantization requires an even number of vector dimensions

PUT my-byte-quantized-index
{
  "mappings": {
    "properties": {
      "my_vector": {
        "type": "dense_vector",
        "dims": 3,
        "index": true,
        "index_options": {
          "type": "int8_hnsw"
        }
      }
    }
  }
}

PUT my-byte-quantized-index
{
  "mappings": {
    "properties": {
      "my_vector": {
        "type": "dense_vector",
        "dims": 4,
        "index": true,
        "index_options": {
          "type": "int4_hnsw"
        }
      }
    }
  }
}

# Further element_type can be specified: float (4 byte), byte(1-byte), bit
# dims cannot exceed 4096
# with bit, only l2_norm (euclidean distance) is supported

# FLATTENED FIELD TYPE
# By default, each subfield in an object is mapped and indexed separately. 
# If the names or types of the subfields are not known in advance, then they are mapped dynamically.
# The flattened type provides an alternative approach, where the entire object is mapped as a single field. Given an object, the flattened mapping will parse out its leaf values and index them into one field as keywords. 
# mappings explosion means too many fields for index to handle, given the infrastructure
# The object’s contents can then be searched through simple queries and aggregations.
# This data type can be useful for indexing objects with a large or unknown number of unique keys. Only one field mapping is created for the whole JSON object, which can help prevent a mappings explosion from having too many distinct field mappings.

# The flattened mapping type should not be used for indexing all document content, as it treats all values as keywords and does not provide full search functionality

PUT bug_reports
{
  "mappings": {
    "properties": {
      "title": {
        "type": "text"
      },
      "labels": {
        "type": "flattened"
      }
    }
  }
}

POST bug_reports/_doc/1
{
  "title": "Results are not sorted correctly.",
  "labels": {
    "priority": "urgent",
    "release": ["v1.2.5", "v1.3.0"],
    "timestamp": {
      "created": 1541458026,
      "closed": 1541457010
    }
  }
}

POST bug_reports/_search
{
  "query": {
    "term": {"labels.release": "v1.3.0"}
  }
}

# However if you do the below (remove v), it won't return anything, as values are keywords only
POST bug_reports/_search
{
  "query": {
    "term": {"labels.release": "1.3.0"}
  }
}

# GEO POINT FIELD TYPE
PUT my-index-000001
{
  "mappings": {
    "properties": {
      "location": {
        "type": "geo_point"
      }
    }
  }
}

PUT my-index-000001/_doc/1
{
  "text": "Geopoint as an object using GeoJSON format",
  "location": { 
    "type": "Point",
    "coordinates": [-71.34, 41.12]
  }
}

# WKT = well-known point
PUT my-index-000001/_doc/2
{
  "text": "Geopoint as a WKT POINT primitive",
  "location" : "POINT (-71.34 41.12)" 
}

PUT my-index-000001/_doc/3
{
  "text": "Geopoint as an object with 'lat' and 'lon' keys",
  "location": { 
    "lat": 41.12,
    "lon": -71.34
  }
}

PUT my-index-000001/_doc/4
{
  "text": "Geopoint as an array",
  "location": [ -71.34, 41.12 ] 
}

PUT my-index-000001/_doc/5
{
  "text": "Geopoint as a string",
  "location": "41.12,-71.34" 
}

PUT my-index-000001/_doc/6
{
  "text": "Geopoint as a geohash",
  "location": "drm3btev3e86" 
}

GET my-index-000001/_search
{
  "query": {
    "geo_bounding_box": { 
      "location": {
        "top_left": {
          "lat": 42,
          "lon": -72
        },
        "bottom_right": {
          "lat": 40,
          "lon": -74
        }
      }
    }
  }
}

# GEO SHAPE FIELD TYPE
# POINT, LINESTRING, POLYGON, MULTIPOINT, MULTILINESTRING, MULTIPOLYGON, and GEOMETRYCOLLECTION, ENVELOPE, CIRCLE
# https://www.elastic.co/guide/en/elasticsearch/reference/current/geo-shape.html

# HISTOGRAM FIELD TYPE
PUT my-index-000001
{
  "mappings" : {
    "properties" : {
      "my_histogram" : {
        "type" : "histogram"
      },
      "my_text" : {
        "type" : "keyword"
      }
    }
  }
}
PUT my-index-000001/_doc/1
{
  "my_text" : "histogram_1",
  "my_histogram" : {
      "values" : [0.1, 0.2, 0.3, 0.4, 0.5], 
      "counts" : [3, 7, 23, 12, 6] 
   }
}

PUT my-index-000001/_doc/2
{
  "my_text" : "histogram_2",
  "my_histogram" : {
      "values" : [0.1, 0.25, 0.35, 0.4, 0.45, 0.5], 
      "counts" : [8, 17, 8, 7, 6, 2] 
   }
}

# IP FIELD TYPE
# An ip field can index/store either IPv4 or IPv6 addresses

PUT my-index-000001
{
  "mappings": {
    "properties": {
      "ip_addr": {
        "type": "ip"
      }
    }
  }
}

PUT my-index-000001/_doc/1
{
  "ip_addr": "192.168.1.1"
}

GET my-index-000001/_search
{
  "query": {
    "term": {
      "ip_addr": "192.168.0.0/16"
    }
  }
}

GET my-index-000001/_search
{
  "query": {
    "term": {
      "ip_addr": "2001:db8::/48"
    }
  }
}

# JOIN FIELD TYPE
# The join data type is a special field that creates parent/child relation within documents of the same index. 
# The relations section defines a set of possible relations within the documents, each relation being a parent name and a child name.
# don’t recommend using multiple levels of relations to replicate a relational model
# Below question is parent of answer

PUT my-index-000001
{
  "mappings": {
    "properties": {
      "my_id": {
        "type": "keyword"
      },
      "my_join_field": { 
        "type": "join",
        "relations": {
          "question": "answer" 
        }
      }
    }
  }
}

# Defnie parents  aka. these are questions
PUT my-index-000001/_doc/1?refresh
{
  "my_id": "1",
  "text": "This is a question",
  "my_join_field": {
    "name": "question" 
  }
}

PUT my-index-000001/_doc/2?refresh
{
  "my_id": "2",
  "text": "This is another question",
  "my_join_field": {
    "name": "question"
  }
}

#When indexing a child, the name of the relation as well as the parent id of the document must be added in the _source
PUT my-index-000001/_doc/3?routing=1&refresh 
{
  "my_id": "3",
  "text": "This is an answer",
  "my_join_field": {
    "name": "answer", 
    "parent": "1" 
  }
}

PUT my-index-000001/_doc/4?routing=1&refresh
{
  "my_id": "4",
  "text": "This is another answer",
  "my_join_field": {
    "name": "answer",
    "parent": "1"
  }
}

# Parent-join and performance

# The only case where the join field makes sense is if your data contains a one-to-many relationship where one entity significantly outnumbers the other entity. An example of such case is a use case with products and offers for these products. In the case that offers significantly outnumbers the number of products then it makes sense to model the product as parent document and the offer as child document


# Parent-join restrictions

#     Only one join field mapping is allowed per index.
#     Parent and child documents must be indexed on the same shard. This means that the same routing value needs to be provided when getting, deleting, or updating a child document.
#     An element can have multiple children but only one parent.
#     It is possible to add a new relation to an existing join field.
#     It is also possible to add a child to an existing element but only if the element is already a parent


# Querying parent-child documents
# Returns all documents that are children of the specified parent document (in this case id:1)
# Further count the number of parents using aggregations
# The parent-join creates one field to index the name of the relation within the document (my_parent, my_child, …​).
#It also creates one field per parent/child relation. The name of this field is the name of the join field followed by # and the name of the parent in the relation. So for instance for the my_parent → [my_child, another_child] relation, the join field creates an additional field named my_join_field#my_parent.

This field contains the parent _id that the document links to if the document is a child (my_child or another_child) and the _id of document if it’s a parent (my_parent)
GET my-index-000001/_search
{
  "query": {
    "parent_id": { 
      "type": "answer",
      "id": "1"
    }
  },
  "aggs": {
    "parents": {
      "terms": {
        "field": "my_join_field#question", 
        "size": 10
      }
    }
  },
  "runtime_mappings": {
    "parent": {
      "type": "long",
      "script": """
        emit(Integer.parseInt(doc['my_join_field#question'].value)) 
      """
    }
  },
  "fields": [
    { "field": "parent" }
  ]
}

# Global ordinals, by default, are built eagerly: if the index has changed, global ordinals for the join field will be rebuilt as part of the refresh. This can add significant time to the refresh
# When the join field is used infrequently and writes occur frequently it may make sense to disable eager loading
PUT my-index-000001
{
  "mappings": {
    "properties": {
      "my_join_field": {
        "type": "join",
        "relations": {
           "question": "answer"
        },
        "eager_global_ordinals": false
      }
    }
  }
}

# Multiple children for single parent
PUT my-index-000001
{
  "mappings": {
    "properties": {
      "my_join_field": {
        "type": "join",
        "relations": {
          "question": ["answer", "comment"]  
        }
      }
    }
  }
}

# Multiple levels of parent-child relationships
# Not recommended
PUT my-index-000001
{
  "mappings": {
    "properties": {
      "my_join_field": {
        "type": "join",
        "relations": {
          "question": ["answer", "comment"],  
          "answer": "vote" 
        }
      }
    }
  }
}

# KEYWORD FIELD TYPE
# The keyword family includes the following field types:

#     keyword, which is used for structured content such as IDs, email addresses, hostnames, status codes, zip codes, or tags.
#     constant_keyword for keyword fields that always contain the same value.
#     wildcard for unstructured machine-generated content. The wildcard type is optimized for fields with large values or high cardinality.
# Avoid using keyword fields for full-text search. Use the text field type instead

# Not all numeric data should be mapped as a numeric field data type. Elasticsearch optimizes numeric fields, such as integer or long, for range queries. However, keyword fields are better for term and other term-level queries.
# Identifiers, such as an ISBN or a product ID, are rarely used in range queries. However, they are often retrieved using term-level queries.

# If you’re unsure which to use, you can use a multi-field to map the data as both a keyword and a numeric data type

PUT my-index-000001
{
  "mappings": {
    "properties": {
      "tags": {
        "type":  "keyword"
      }
    }
  }
}

# Values longer than ignore_above are preserved but sorted to the end. For example:

# Constant keyword field type
PUT logs-debug
{
  "mappings": {
    "properties": {
      "@timestamp": {
        "type": "date"
      },
      "message": {
        "type": "text"
      },
      "level": {
        "type": "constant_keyword",
        "value": "debug"
      }
    }
  }
}

# WILDCARD FIELD TYPE
# The wildcard field type is a specialized keyword field for unstructured machine-generated content you plan to search using grep-like wildcard and regexp queries. The wildcard type is optimized for fields with large values or high cardinality

PUT my-index-000001
{
  "mappings": {
    "properties": {
      "my_wildcard": {
        "type": "wildcard"
      }
    }
  }
}

PUT my-index-000001/_doc/1
{
  "my_wildcard" : "This string can be quite lengthy"
}

GET my-index-000001/_search
{
  "query": {
    "wildcard": {
      "my_wildcard": {
        "value": "*quite*lengthy"
      }
    }
  }
}

# NESTED FIELD TYPE
# PUT my-index-000001/_doc/1
{
  "group" : "fans",
  "user" : [ 
    {
      "first" : "John",
      "last" :  "Smith"
    },
    {
      "first" : "Alice",
      "last" :  "White"
    }
  ]
}

# The previous document is internally converted to the below
{
  "group" :        "fans",
  "user.first" : [ "alice", "john" ],
  "user.last" :  [ "smith", "white" ]
}

#The user.first and user.last fields are flattened into multi-value fields, and the association between alice and white is lost. This document would incorrectly match a query for alice AND smith:

GET my-index-000001/_search
{
  "query": {
    "bool": {
      "must": [
        { "match": { "user.first": "Alice" }},
        { "match": { "user.last":  "Smith" }}
      ]
    }
  }
}

# To preserve the relationship between first and last names, you can use the nested data type.
PUT my-index-000001
{
  "mappings": {
    "properties": {
      "user": {
        "type": "nested" 
      }
    }
  }
}

PUT my-index-000001/_doc/1
{
  "group" : "fans",
  "user" : [
    {
      "first" : "John",
      "last" :  "Smith"
    },
    {
      "first" : "Alice",
      "last" :  "White"
    }
  ]
}

GET my-index-000001/_search
{
  "query": {
    "nested": {
      "path": "user",
      "query": {
        "bool": {
          "must": [
            { "match": { "user.first": "Alice" }},
            { "match": { "user.last":  "Smith" }} 
          ]
        }
      }
    }
  }
}

GET my-index-000001/_search
{
  "query": {
    "nested": {
      "path": "user",
      "query": {
        "bool": {
          "must": [
            { "match": { "user.first": "Alice" }},
            { "match": { "user.last":  "White" }} 
          ]
        }
      },
      "inner_hits": { 
        "highlight": {
          "fields": {
            "user.first": {}
          }
        }
      }
    }
  }
}

# NUMBER FIELD TYPE
# https://www.elastic.co/guide/en/elasticsearch/reference/current/number.html

# OBJECT FIELD TYPE
PUT my-index-000001/_doc/1
{ 
  "region": "US",
  "manager": { 
    "age":     30,
    "name": { 
      "first": "John",
      "last":  "Smith"
    }
  }
}
#Internally flattens it
{
  "region":             "US",
  "manager.age":        30,
  "manager.name.first": "John",
  "manager.name.last":  "Smith"
}

# RANGE FIELD TYPE
# Range field types represent a continuous range of values between an upper and lower bound. For example, a range can represent any date in October or any integer from 0 to 9. They are defined using the operators gt or gte for the lower bound, and lt or lte for the upper bound. They can be used for querying, and have limited support for aggregations

PUT range_index
{
  "settings": {
    "number_of_shards": 2
  },
  "mappings": {
    "properties": {
      "expected_attendees": {
        "type": "integer_range"
      },
      "time_frame": {
        "type": "date_range", 
        "format": "yyyy-MM-dd HH:mm:ss||yyyy-MM-dd||epoch_millis"
      }
    }
  }
}

PUT range_index/_doc/1?refresh
{
  "expected_attendees" : { 
    "gte" : 10,
    "lt" : 20
  },
  "time_frame" : {
    "gte" : "2015-10-31 12:00:00", 
    "lte" : "2015-11-01"
  }
}

## 12 is a value inside the range, so below will match
GET range_index/_search
{
  "query" : {
    "term" : {
      "expected_attendees" : {
        "value": 12
      }
    }
  }
}

# IP RANGE FIELD TYPE
PUT range_index/_mapping
{
  "properties": {
    "ip_allowlist": {
      "type": "ip_range"
    }
  }
}

PUT range_index/_doc/2
{
  "ip_allowlist" : "192.168.0.0/16"
}

# SEARCH-AS-YOU-TYPE FIELD TYPE
# The search_as_you_type field type is a text-like field that is optimized to provide out-of-the-box support for queries that serve an as-you-type completion use case. It creates a series of subfields that are analyzed to index terms that can be efficiently matched by a query that partially matches the entire indexed text value. Both prefix completion (i.e matching terms starting at the beginning of the input) and infix completion (i.e. matching terms at any position within the input) are supported
PUT my-index-000001
{
  "mappings": {
    "properties": {
      "my_field": {
        "type": "search_as_you_type"
      }
    }
  }
}

PUT my-index-000001/_doc/1?refresh
{
  "my_field": "quick brown fox jump lazy dog"
}

# The most efficient way of querying to serve a search-as-you-type use case is usually a multi_match query of type bool_prefix that targets the root search_as_you_type field and its shingle subfields
GET my-index-000001/_search
{
  "query": {
    "multi_match": {
      "query": "brown f",
      "type": "bool_prefix",
      "fields": [
        "my_field",
        "my_field._2gram",
        "my_field._3gram"
      ]
    }
  }
}

# SEMANTIC TEXT FIELD TYPE
# The semantic_text field type automatically generates embeddings for text content using an inference endpoint. Long passages are automatically chunked to smaller sections to enable the processing of larger corpuses of text

PUT my-index-000001
{
  "mappings": {
    "properties": {
      "inference_field": {
        "type": "semantic_text",
        "inference_id": "my-elser-endpoint"
      }
    }
  }
}

# semantic_text and semantic query are used together generally to search for similar documents
# In case you want to customize data indexing, use the sparse_vector or dense_vector field types and create an ingest pipeline with an inference processor to generate the embeddings. This tutorial walks you through the process. In these cases - when you use sparse_vector or dense_vector field types instead of the semantic_text field type to customize indexing - using the semantic_query is not supported for querying the field data

# TEXT FIELD TYPE
# The text family includes the following field types:

#     text, the traditional field type for full-text content such as the body of an email or the description of a product.
#     match_only_text, a space-optimized variant of text that disables scoring and performs slower on queries that need positions. It is best suited for indexing log messages.

# Use a field as both text and keyword

#fielddata mapping parameter

# text fields are searchable by default, but by default are not available for aggregations, sorting, or scripting. If you try to sort, aggregate, or access values from a text field using a script, you’ll see an exception indicating that field data is disabled by default on text fields. To load field data in memory, set fielddata=true on your field
# Field data is the only way to access the analyzed tokens from a full text field in aggregations, sorting, or scripting. For example, a full text field like New York would get analyzed as new and york. To aggregate on these tokens requires field data.

# INSTEAD Most users who want to do more with text fields use multi-field mappings by having both a text field for full text searches, and an unanalyzed keyword field for aggregations, as follows

PUT my-index-000001
{
  "mappings": {
    "properties": {
      "my_field": { 
        "type": "text",
        "fields": {
          "keyword": { 
            "type": "keyword"
          }
        }
      }
    }
  }
}

# Otherwise syntax for enabling field data
PUT my-index-000001/_mapping
{
  "properties": {
    "my_field": { 
      "type":     "text",
      "fielddata": true
    }
  }
}

# MATCH-ONLY TEXT FIELD TYPE
# As mentioned above use for logs

PUT logs
{
  "mappings": {
    "properties": {
      "@timestamp": {
        "type": "date"
      },
      "message": {
        "type": "match_only_text"
      }
    }
  }
}

# TOKEN COUNT FIELD TYPE
# A field of type token_count is really an integer field which accepts string values, analyzes them, then indexes the number of tokens in the string

PUT my-index-000001
{
  "mappings": {
    "properties": {
      "name": { 
        "type": "text",
        "fields": {
          "length": { 
            "type":     "token_count",
            "analyzer": "standard"
          }
        }
      }
    }
  }
}

PUT my-index-000001/_doc/1
{ "name": "John Smith" }

PUT my-index-000001/_doc/2
{ "name": "Rachel Alice Williams" }

GET my-index-000001/_search
{
  "query": {
    "term": {
      "name.length": 3 
    }
  }
}

# VERSION FIELD TYPE
# for software semantic versioning
# The version field type is a specialization of the keyword field for handling software version values and to support specialized precedence rules for them. Precedence is defined following the rules outlined by Semantic Versioning, which for example means that major, minor and patch version parts are sorted numerically (i.e. "2.1.0" < "2.4.1" < "2.11.2") and pre-release versions are sorted before release versions (i.e. "1.0.0-alpha" < "1.0.0")

# META DATA
# https://www.elastic.co/guide/en/elasticsearch/reference/current/mapping-fields.html
# Some are pre-defined like _doc_count, _id, _index, _field_names and  you can define app specific ones

# MAPPING PARAMETERS
# https://www.elastic.co/guide/en/elasticsearch/reference/current/mapping-params.html
# Noteworthy: analyzer, coerce, copy_to, meta, 

# normalizer
PUT index
{
  "settings": {
    "analysis": {
      "normalizer": {
        "my_normalizer": {
          "type": "custom",
          "char_filter": [],
          "filter": ["lowercase", "asciifolding"]
        }
      }
    }
  },
  "mappings": {
    "properties": {
      "foo": {
        "type": "keyword",
        "normalizer": "my_normalizer"
      }
    }
  }
}

PUT index/_doc/1
{
  "foo": "BÀR"
}

PUT index/_doc/2
{
  "foo": "bar"
}

PUT index/_doc/3
{
  "foo": "baz"
}

POST index/_refresh

GET index/_search
{
  "query": {
    "term": {
      "foo": "BAR"
    }
  }
}

GET index/_search
{
  "query": {
    "match": {
      "foo": "BAR"
    }
  }
}

#meta 
PUT my-index-000001
{
  "mappings": {
    "properties": {
      "latency": {
        "type": "long",
        "meta": {
          "unit": "ms"
        }
      }
    }
  }
}

