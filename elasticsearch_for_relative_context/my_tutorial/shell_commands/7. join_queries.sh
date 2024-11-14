# JOINING QUERIES
# Performing full SQL-style joins in a distributed system like Elasticsearch is prohibitively expensive. Instead, Elasticsearch offers two forms of join which are designed to scale horizontally.

# nested query
# Documents may contain fields of type nested. These fields are used to index arrays of objects, where each object can be queried (with the nested query) as an independent document.
# has_child and has_parent queries
# A join field relationship can exist between documents within a single index. The has_child query returns parent documents whose child documents match the specified query, while the has_parent query returns child documents whose parent document matches the specified query.

# NESTED QUERY
# Elasticsearch flattens all nested field types
PUT /my-index-000001
{
  "mappings": {
    "properties": {
      "obj1": {
        "type": "nested"
      }
    }
  }
}

# Indexing a document with nested fields
POST /nested/_doc/1
{
    "id": "batch_req_LZeVrRaOHsCPa8EQBfe7bFpz",
    "custom_id": "f5817a9500f6a7ad4d0bd2e1a31e660f9eb7506ce7e86dc0b06bad759f4a9902",
    "response": {
        "status_code": 200,
        "request_id": "5b756981b0ade6847033ebf6773161a4",
        "body": {
            "id": "chatcmpl-9wD0XJI72pfK2jvDdcuEKZwcArQnO",
            "object": "chat.completion",
            "created": 1723660053,
            "model": "gpt-4o-mini-2024-07-18",
            "choices": [
                {
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": "{\n  \"title\": \"Consultant/Architect\",\n  \"address\": \"Morocco\",\n  \"salary\": {\n    \"min\": null,\n    \"max\": null,\n    \"currency\": \"USD\",\n    \"frequency\": \"annually\",\n    \"description\": \"Salary details not specified.\"\n  },\n  \"employmentType\": \"full-time\",\n  \"experienceLevel\": {\n    \"minYears\": null,\n    \"maxYears\": null,\n    \"level\": \"entry-level\",\n    \"description\": \"All seniority levels considered.\",\n    \"additionalRequirements\": []\n  },\n  \"qualifications\": {\n    \"required\": [\n      \"Degree or equivalent relevant experience required.\",\n      \"Proficiency in English language AND French.\"\n    ],\n    \"preferred\": [\n      \"Prior experience in industry related technologies like Omnistudio, CPQ, OM.\",\n      \"Experience as a Senior Architect and/or CTO in a mid to large sized organisation.\"\n    ]\n ,\n  \"education\": []\n  },\n  \"responsibilities\": [\n    \"Collaborate with Customers and Partners during the project lifecycle.\",\n    \"Guide the evaluation of business and technical requirements.\",\n    \"Act as lead architect for the overall engagement.\",\n    \"Review and guide project vision and direction.\",\n    \"Direct early solution evaluation and proactive management of issues.\",\n    \"Support pre-sales activities to position Salesforce Services.\",\n    \"Contribute to broader goals by becoming a citizen philanthropist.\"\n  ],\n  \"skills_required\": [\n    \"Hands-on technical consulting and solution implementation experience.\",\n    \"Ability to analyze, design, and optimize business processes.\",\n    \"Strong presentation, communication and facilitation skills.\"\n  ],\n  \"skills_preferred\": [\n    \"Experience with enterprise integration tools (ESBs and/or ETL tools).\",\n    \"Detailed understanding of Web Services and Data Modeling.\"\n  ],\n  \"technologies\": [\n    \"Salesforce.com\",\n    \"Omnistudio\",\n    \"CPQ\",\n    \"Enterprise integration tools\"\n  ],\n  \"postedDate\": \"2023-10-01\",\n  \"applicationDeadline\": \"2023-12-01\",\n  \"applicationLink\": \"https://salesforce.com/careers\",\n  \"tags\": [\n    \"Customer Success\",\n    \"Salesforce\",\n    \"Consultant\",\n    \"Architect\"\n  ],\n  \"benefits\": [\n    \"Wellbeing reimbursement\",\n    \"Generous parental leave\",\n    \"Adoption assistance\",\n    \"Fertility benefits\"\n  ],\n  \"department\": \"Salesforce Professional Services\",\n  \"roleCategory\": \"Consulting\",\n  \"remoteWorkOption\": \"Hybrid\",\n  \"visaSponsorship\": false,\n  \"languageRequirements\": [\n    {\n      \"language\": \"English\",\n      \"proficiencyLevel\": \"Fluent\"\n    },\n    {\n      \"language\": \"French\",\n      \"proficiencyLevel\": \"Fluent\"\n    }\n  ],\n  \"workSchedule\": \"Standard business hours with regional travel required.\",\n  \"numberOfOpenings\": 5,\n  \"travelRequirements\": \"Available to travel regionally and occasionally internationally.\",\n  \"physicalRequirements\": [],\n  \"securityClearance\": \"None required.\",\n  \"diversityStatement\": \"Salesforce is committed to creating a workforce that reflects society through inclusive programs and initiatives.\",\n  \"applicationInstructions\": \"Submit your application through the Salesforce careers page.\",\n  \"interviewProcess\": [\n    \"Initial phone screening\",\n    \"Technical interview\",\n    \"Final interview with management\"\n  ],\n  \"additionalNotes\": \"Salesforce welcomes all applicants.\"\n}",
                        "refusal": null
                    },
                    "logprobs": null,
                    "finish_reason": "stop"
                }
            ],
            "usage": {
                "prompt_tokens": 1685,
                "completion_tokens": 727,
                "total_tokens": 2412
            },
            "system_fingerprint": "fp_48196bc67a"
        }
    },
    "error": null
}
# Adding nested fields to the mapping
PUT /nested-index
{
    "mappings": {
        "properties": {
            "response": {
                "type": "nested",
                "properties": {
                    "status_code": {
                        "type": "integer"
                    },
                    "body": {
                        "type": "nested",
                        "properties": {
                            "choices": {
                                "type": "nested",
                                "properties": {
                                    "message": {
                                        "type": "nested",
                                        "properties": {
                                            "content": {
                                                "type": "text"
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    }
}


# Observe that whether it is a json array or object, nested should be until the level you want to query
# For e.g. if you want to query content, then response.body.choices.message.content should be nested
GET mynested/_mapping

# Query to find documents where status_code=200 and content has the word "consultant"
GET /nested-index/_search
{
    "query": {
        "bool": {
            "must": [
                {
                    "nested": {
                        "path": "response",
                        "query": {
                            "term": {
                                "response.status_code": 200
                            }
                        }
                    }
                },
                {
                    "nested": {
                        "path": "response.body.choices.message",
                        "query": {
                            "match": {
                                "response.body.choices.message.content": "consultant"
                            }
                        }
                    }
                }
            ]
        }
    }
}


# HAS_CHILD QUERY
# The has_child query returns parent documents whose child documents match the specified query.
# The has_child query requires the child type name to be specified in the query.
# The has_child query can be used in conjunction with the bool query to combine multiple queries.
# Because it performs a join, the has_child is slow compared to other queries

PUT /company
{
  "mappings": {
    "properties": {
      "join_field": { 
        "type": "join",
        "relations": {
          "department": "employee"
        }
      }
    }
  }
}

// Index department documents
PUT /company/_doc/1
{
  "name": "Development",
  "join_field": "department"
}

PUT /company/_doc/2
{
  "name": "Marketing",
  "join_field": "department"
}

# Index employee documents
# Routing is used to determine which shard a document should be indexed on or searched from. The default routing is based on the document's ID.

PUT /company/_doc/3?routing=1
{
  "name": "John Doe",
  "age": 30,
  "join_field": {
    "name": "employee",
    "parent": "1"
  }
}

PUT /company/_doc/4?routing=1
{
  "name": "Jane Smith",
  "age": 35,
  "join_field": {
    "name": "employee",
    "parent": "1"
  }
}

PUT /company/_doc/5?routing=2
{
  "name": "Bob Johnson",
  "age": 40,
  "join_field": {
    "name": "employee",
    "parent": "2"
  }
}

GET /company/_search
{
  "query": {
    "has_child": {
      "type": "employee",
      "query": {
        "range": {
          "age": {
            "gt": 35
          }
        }
      }
    }
  }
}

# HAS_PARENT QUERY
GET /company/_search
{
  "query": {
    "has_parent": {
      "parent_type": "department",
      "query": {
        "term": {
          "name": "Development"
        }
      }
    }
  }
}

# SPAN QUERIES
# span queries can be computationally expensive
# mostly used in legal and patent search

# This query would find documents where "patent" and "infringement" appear within 5 words of each other, in that order.
GET /legal_docs/_search
{
  "query": {
    "span_near": {
      "clauses": [
        { "span_term": { "text": "patent" }},
        { "span_term": { "text": "infringement" }}
      ],
      "slop": 5,
      "in_order": true
    }
  }
}

# This query finds documents containing "invention" but not where "prior art" appears nearby.

GET /patent_docs/_search
{
  "query": {
    "span_not": {
      "include": {
        "span_term": { "text": "invention" }
      },
      "exclude": {
        "span_near": {
          "clauses": [
            { "span_term": { "text": "prior" }},
            { "span_term": { "text": "art" }}
          ],
          "slop": 1,
          "in_order": true
        }
      }
    }
  }
}

#This query finds the exact phrase "defendant pleads guilty" with no words in between.

GET /legal_docs/_search
{
  "query": {
    "span_near": {
      "clauses": [
        { "span_term": { "text": "defendant" }},
        { "span_term": { "text": "pleads" }},
        { "span_term": { "text": "guilty" }}
      ],
      "slop": 0,
      "in_order": true
    }
  }
}

#This query finds documents that either have "novel" near "invention" or "inventive" near "step".
GET /patent_docs/_search
{
  "query": {
    "span_or": {
      "clauses": [
        {
          "span_near": {
            "clauses": [
              { "span_term": { "text": "novel" }},
              { "span_term": { "text": "invention" }}
            ],
            "slop": 3,
            "in_order": true
          }
        },
        {
          "span_near": {
            "clauses": [
              { "span_term": { "text": "inventive" }},
              { "span_term": { "text": "step" }}
            ],
            "slop": 1,
            "in_order": true
          }
        }
      ]
    }
  }
}

# More: span_or, span_not, span_term, span_within

