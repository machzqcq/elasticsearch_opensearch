# The full text queries enable you to search analyzed text fields such as the body of an email. The query string is processed using the same analyzer that was applied to the field during indexing.

# INTERVALS QUERY
# Returns documents based on the order and proximity of matching terms.

#The intervals query uses matching rules, constructed from a small set of definitions. These rules are then applied to terms from a specified field

#The following intervals search returns documents containing my
# favorite food without any gap, followed by hot water or cold porridge in the my_text field.

# This search would match a my_text value of my favorite food is cold
# porridge but not when it's cold my favorite food is porridge.

#Valid rules include:

    # match
    # prefix
    # wildcard
    # fuzzy
    # all_of
    # any_of



POST _search
{
  "query": {
    "intervals" : {
      "my_text" : {
        "all_of" : {
          "ordered" : true,
          "intervals" : [
            {
              "match" : {
                "query" : "my favorite food",
                "max_gaps" : 0,
                "ordered" : true
              }
            },
            {
              "any_of" : {
                "intervals" : [
                  { "match" : { "query" : "hot water" } },
                  { "match" : { "query" : "cold porridge" } }
                ]
              }
            }
          ]
        }
      }
    }
  }
}

POST /tasks/_search
{
  "query": {
    "intervals" : {
      "RELATED_TASKS_NAMES_LIST" : {
        "all_of" : {
          "ordered" : true,
          "intervals" : [
            {
              "match" : {
                "query" : "code",
                "max_gaps" : 0,
                "ordered" : true
              }
            },
            {
              "any_of" : {
                "intervals" : [
                  { "match" : { "query" : "search" } },
                  { "match" : { "query" : "simplification" } }
                ]
              }
            }
          ]
        }
      }
    }
  }
}

# code quality with one space
POST /tasks/_search
{
  "query": {
    "intervals" : {
      "RELATED_TASKS_NAMES_LIST" : {
        "all_of" : {
          "ordered" : true,
          "intervals" : [
            {
              "match" : {
                "query" : "code quality",
                "max_gaps" : 0,
                "ordered" : true
              }
            },
            {
              "any_of" : {
                "intervals" : [
                  { "match" : { "query" : "improvement" } },
                  { "match" : { "query" : "simplification" } }
                ]
              }
            }
          ]
        }
      }
    }
  }
}

# with fuzzy
# Avoid mixing fuzziness with wildcards

POST /tasks/_search
{
  "query": {
    "intervals" : {
      "RELATED_TASKS_NAMES_LIST" : {
        "all_of" : {
          "ordered" : true,
          "intervals" : [
            {
              "match" : {
                "query" : "code",
                "max_gaps" : 0,
                "ordered" : true
              }
            },
            {
              "any_of" : {
                "intervals" : [
                  { "fuzzy" : { "term" : "serch" } },
                  { "match" : { "query" : "simplification" } }
                ]
              }
            }
          ]
        }
      }
    }
  }
}

# with prefix
POST /tasks/_search
{
  "query": {
    "intervals" : {
      "RELATED_TASKS_NAMES_LIST" : {
        "all_of" : {
          "ordered" : true,
          "intervals" : [
            {
              "match" : {
                "query" : "code quality",
                "max_gaps" : 0,
                "ordered" : true
              }
            },
            {
              "any_of" : {
                "intervals" : [
                  { "prefix" : { "prefix" : "impr" } },
                  { "match" : { "query" : "simplification" } }
                ]
              }
            }
          ]
        }
      }
    }
  }
}

# with wildcard
# This parameter supports two wildcard operators:

#     ?, which matches any single character
#     *, which can match zero or more characters, including an empty one

POST /tasks/_search
{
  "query": {
    "intervals" : {
      "RELATED_TASKS_NAMES_LIST" : {
        "all_of" : {
          "ordered" : true,
          "intervals" : [
            {
              "wildcard" : {
                "pattern" : "code*",
                "analyzer": "standard"
              }
            },
            {
              "any_of" : {
                "intervals" : [
                  { "match" : { "query" : "improvement" } },
                  { "match" : { "query" : "analysis" } }
                ]
              }
            }
          ]
        }
      }
    }
  }
}

POST /tasks/_search
{
  "query": {
    "intervals" : {
      "RELATED_TASKS_NAMES_LIST" : {
        "all_of" : {
          "ordered" : true,
          "intervals" : [
            {
              "wildcard" : {
                "pattern" : "code*",
                "analyzer": "standard"
              }
            },
            {
              "any_of" : {
                "intervals" : [
                  { "match" : { "query" : "improvement" } },
                  { "match" : { "query" : "simplification" } }
                ]
              }
            }
          ]
        }
      }
    }
  }
}

# Filter example

# The following search includes a filter rule. It returns documents that have the words hot and porridge within 10 positions of each other, without the word salty in between:

POST _search
{
  "query": {
    "intervals" : {
      "my_text" : {
        "match" : {
          "query" : "hot porridge",
          "max_gaps" : 10,
          "filter" : {
            "not_containing" : {
              "match" : {
                "query" : "salty"
              }
            }
          }
        }
      }
    }
  }
}

# MATCH QUERY

# Returns documents that match a provided text, number, date or boolean value. The provided text is analyzed before matching.

# The match query is the standard query for performing a full-text search, including options for fuzzy matching.

# How the match query works: The match query is of type boolean. It means that the text provided is analyzed and the analysis process constructs a boolean query from the provided text. The operator parameter can be set to or or and to control the boolean clauses (defaults to or). 

# below returns 3
POST /tasks/_search
{
  "query": {
    "match": {
      "RELATED_TASKS_NAMES_LIST": {
        "query": "code optimization"
      }
    }
  }
}

# below returns 2
POST /tasks/_search
{
  "query": {
    "match": {
      "RELATED_TASKS_NAMES_LIST": {
        "query": "code optimization",
        "operator": "and"
      }
    }
  }
}

# can set fuzziness in match query
POST /tasks/_search
{
  "query": {
    "match": {
      "RELATED_TASKS_NAMES_LIST": {
        "query": "coe optimization",
        "fuzziness": "AUTO",
        "operator": "and"
      }
    }
  }
}

# MATCH BOOLEAN PREFIX QUERY
#A match_bool_prefix query analyzes its input and constructs a bool query from the terms. Each term except the last is used in a term query. The last term is used in a prefix query. A match_bool_prefix query such as

GET /_search
{
  "query": {
    "match_bool_prefix" : {
      "message" : "quick brown f"
    }
  }
}

#where analysis produces the terms quick, brown, and f is similar to the following bool query

GET /_search
{
  "query": {
    "bool" : {
      "should": [
        { "term": { "message": "quick" }},
        { "term": { "message": "brown" }},
        { "prefix": { "message": "f"}}
      ]
    }
  }
}

#An important difference between the match_bool_prefix query and match_phrase_prefix is that the match_phrase_prefix query matches its terms as a phrase, but the match_bool_prefix query can match its terms in any position. The example match_bool_prefix query above could match a field containing quick brown fox, but it could also match brown fox quick. It could also match a field containing the term quick, the term brown and a term starting with f, appearing in any position.

# MATCH PHRASE
# The match_phrase query analyzes the text and creates a phrase query out of the analyzed text. For example:

GET /_search
{
  "query": {
    "match_phrase": {
      "message": "this is a test"
    }
  }
}

# MATCH PHRASE PREFIX
#Returns documents that contain the words of a provided text, in the same order as provided. The last term of the provided text is treated as a prefix, matching any words that begin with that term
GET /_search
{
  "query": {
    "match_phrase_prefix": {
      "message": {
        "query": "quick brown f"
      }
    }
  }
}

# COMBINED FIELDS
#The combined_fields query supports searching multiple text fields as if their contents had been indexed into one combined field. The query takes a term-centric view of the input string: first it analyzes the query string into individual terms, then looks for each term in any of the fields. This query is particularly useful when a match could span multiple text fields, for example the title, abstract, and body of an article:

GET /_search
{
  "query": {
    "combined_fields" : {
      "query":      "database systems",
      "fields":     [ "title", "abstract", "body"],
      "operator":   "and"
    }
  }
}

# per-field boosting
# Field boosts are interpreted according to the combined field model. For example, if the title field has a boost of 2, the score is calculated as if each term in the title appeared twice in the synthetic combined field
GET /_search
{
  "query": {
    "combined_fields" : {
      "query" : "distributed consensus",
      "fields" : [ "title^2", "body" ] 
    }
  }
}

# MULTI-MATCH QUERY
# The multi_match query builds on the match query to allow multi-field queries:

GET /_search
{
  "query": {
    "multi_match" : {
      "query":    "this is a test", 
      "fields": [ "subject", "message" ] 
    }
  }
}

# fields and per-field boosting and wildcards
GET /_search
{
  "query": {
    "multi_match" : {
      "query":    "Will Smith",
      "fields": [ "title", "*_name" ] 
    }
  }
}

GET /_search
{
  "query": {
    "multi_match" : {
      "query" : "this is a test",
      "fields" : [ "subject^3", "message" ] 
    }
  }
}

# best_fields
# The best_fields type is most useful when you are searching for multiple words best found in the same field. For instance “brown fox” in a single field is more meaningful than “brown” in one field and “fox” in the other.

# The best_fields type generates a match query for each field and wraps them in a dis_max query, to find the single best matching field. For instance, this query

GET /_search
{
  "query": {
    "multi_match" : {
      "query":      "brown fox",
      "type":       "best_fields",
      "fields":     [ "subject", "message" ],
      "tie_breaker": 0.3
    }
  }
}

# is the same as....

GET /_search
{
  "query": {
    "dis_max": {
      "queries": [
        { "match": { "subject": "brown fox" }},
        { "match": { "message": "brown fox" }}
      ],
      "tie_breaker": 0.3
    }
  }
}


# most_fields
# Example Scenarios
# E-commerce product search: Searching product name, description, brand, and category fields simultaneously
# Document search: Querying title, abstract, body, and metadata fields together
# People search: Matching across first name, last name, and full name fields

# Key Differences from best_fields
# most_fields: Combines scores from all matching fields
# best_fields: Uses the score from the single best matching field

GET /_search
{
  "query": {
    "multi_match" : {
      "query":      "quick brown fox",
      "type":       "most_fields",
      "fields":     [ "title", "title.original", "title.shingles" ]
    }
  }
}

# phrase and phrase_prefix
# The phrase and phrase_prefix types behave just like best_fields, but they use a match_phrase or match_phrase_prefix query instead of a match query

# cross_fields
# The cross_fields type is particularly useful with structured documents where multiple fields should match. For instance, when querying the first_name and last_name fields for “Will Smith”, the best match is likely to have “Will” in one field and “Smith” in the other.

GET /_search
{
  "query": {
    "multi_match" : {
      "query":      "Will Smith",
      "type":       "cross_fields",
      "fields":     [ "first_name", "last_name" ],
      "operator":   "and"
    }
  }
}

GET tasks/_search
{
  "query": {
    "multi_match" : {
      "query":      "code optimization",
      "type":       "cross_fields",
      "fields":     [ "RELATED_TASKS_NAMES_LIST", "TASK_NAME"],
      "operator":   "and"
    }
  }
}

# QUERY STRING QUERY
# This query uses a syntax to parse and split the provided query string based on operators, such as AND or NOT
# Because it returns an error for any invalid syntax, we don’t recommend using the query_string query for search boxes

GET tasks/_search
{
  "query": {
    "query_string": {
      "query": "(Ui5) AND (blockchain)",
      "default_field": "RELATED_TASKS_NAMES_LIST"
    }
  }
}

GET tasks/_search
{
  "query": {
    "query_string": {
      "query": "(Ui5) OR (blockchain)",
      "default_field": "RELATED_TASKS_NAMES_LIST"
    }
  }
}

GET tasks/_search
{
  "query": {
    "query_string": {
      "query": "(Civil engineering) OR (theses)",
      "default_field": "RELATED_TASKS_NAMES_LIST"
    }
  }
}

GET tasks/_search
{
  "query": {
    "query_string": {
      "query": "(Civil engineering) OR (theses)",
      "fields": ["RELATED_TASKS*"]
    }
  }
}

GET tasks/_search
{
  "query": {
    "query_string": {
      "query": "(Civil\\*) OR (theses)",
      "fields": ["RELATED_TASKS*"]
    }
  }
}

# SIMPLE QUERY STRING QUERY
# Returns documents based on a provided query string, using a parser with a limited but fault-tolerant syntax.
# While its syntax is more limited than the query_string query, the simple_query_string query does not return errors for invalid syntax

GET tasks/_search
{
  "query": {
    "simple_query_string": {
      "query": "(Civil engineering*)) OR (theses)",
      "fields": ["RELATED_TASKS*"]
    }
  }
}

# LIMIT OPERATORS
# explicitly enable only specific operators, use a | separator. For example, a flags value of OR|AND|PREFIX disables all operators except OR, AND, and PREFIX
GET /_search
{
  "query": {
    "simple_query_string": {
      "query": "foo | bar + baz*",
      "flags": "OR|AND|PREFIX"
    }
  }
}

# GEO POINT
