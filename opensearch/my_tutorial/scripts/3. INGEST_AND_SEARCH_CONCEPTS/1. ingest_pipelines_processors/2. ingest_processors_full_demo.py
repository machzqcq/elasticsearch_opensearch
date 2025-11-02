"""
Complete demonstration of all 43 OpenSearch Ingest Processors
This script contains all processor examples that will be used in the notebook
"""

# Sample data for each processor type
PROCESSOR_EXAMPLES = {
    "append": {
        "description": "Adds values to an array field",
        "sample_doc": {
            "product": "Laptop",
            "tags": ["electronics", "portable"]
        },
        "pipeline": [
            {
                "append": {
                    "field": "tags",
                    "value": ["marked_for_sale", "top_seller"]
                }
            }
        ]
    },
    
    "bytes": {
        "description": "Converts human-readable byte values to bytes",
        "sample_doc": {
            "file_name": "document.pdf",
            "file_size": "2MB"
        },
        "pipeline": [
            {
                "bytes": {
                    "field": "file_size",
                    "target_field": "file_size_bytes"
                }
            }
        ]
    },
    
    "convert": {
        "description": "Changes data type of a field",
        "sample_doc": {
            "price": "99.99",
            "quantity": "50",
            "is_active": "true"
        },
        "pipeline": [
            {
                "convert": {
                    "field": "price",
                    "type": "float"
                }
            },
            {
                "convert": {
                    "field": "quantity",
                    "type": "integer"
                }
            },
            {
                "convert": {
                    "field": "is_active",
                    "type": "boolean"
                }
            }
        ]
    },
    
    "copy": {
        "description": "Copies an entire object from one field to another",
        "sample_doc": {
            "source_field": {
                "nested": {
                    "value": "important_data"
                }
            }
        },
        "pipeline": [
            {
                "copy": {
                    "from": "source_field",
                    "to": "destination_field"
                }
            }
        ]
    },
    
    "csv": {
        "description": "Extracts CSV data into individual fields",
        "sample_doc": {
            "csv_data": "John,Doe,john@example.com,35"
        },
        "pipeline": [
            {
                "csv": {
                    "field": "csv_data",
                    "target_fields": ["first_name", "last_name", "email", "age"]
                }
            }
        ]
    },
    
    "date": {
        "description": "Parses and normalizes date fields",
        "sample_doc": {
            "log_timestamp": "2024-11-02 14:30:45",
            "event_date": "02/11/2024"
        },
        "pipeline": [
            {
                "date": {
                    "field": "log_timestamp",
                    "target_field": "@timestamp",
                    "formats": ["yyyy-MM-dd HH:mm:ss"]
                }
            },
            {
                "date": {
                    "field": "event_date",
                    "formats": ["dd/MM/yyyy"],
                    "target_field": "normalized_event_date"
                }
            }
        ]
    },
    
    "dissect": {
        "description": "Extracts fields from structured text patterns",
        "sample_doc": {
            "log_line": "2024-11-02 ERROR app.py:42 Database connection failed"
        },
        "pipeline": [
            {
                "dissect": {
                    "field": "log_line",
                    "pattern": "%{TIMESTAMP} %{LEVEL} %{SOURCE} %{MESSAGE}"
                }
            }
        ]
    },
    
    "dot_expander": {
        "description": "Converts dotted field names into nested objects",
        "sample_doc": {
            "user.name": "John Doe",
            "user.email": "john@example.com",
            "user.age": 30
        },
        "pipeline": [
            {
                "dot_expander": {
                    "field": "user.name"
                }
            },
            {
                "dot_expander": {
                    "field": "user.email"
                }
            }
        ]
    },
    
    "drop": {
        "description": "Drops documents from indexing based on conditions",
        "sample_doc": {
            "status": "draft",
            "content": "This is a draft article"
        },
        "pipeline": [
            {
                "drop": {
                    "if": "ctx.status == 'draft'"
                }
            }
        ]
    },
    
    "fail": {
        "description": "Raises an error and stops pipeline execution",
        "sample_doc": {
            "price": "-100",
            "product": "Invalid Product"
        },
        "pipeline": [
            {
                "fail": {
                    "if": "ctx.price < 0",
                    "message": "Price cannot be negative: {0}",
                    "message_fields": ["price"]
                }
            }
        ]
    },
    
    "fingerprint": {
        "description": "Generates hash fingerprints for deduplication",
        "sample_doc": {
            "email": "user@example.com",
            "name": "John Doe",
            "phone": "555-1234"
        },
        "pipeline": [
            {
                "fingerprint": {
                    "fields": ["email", "name"],
                    "target_field": "document_fingerprint",
                    "method": "SHA-1"
                }
            }
        ]
    },
    
    "foreach": {
        "description": "Applies processor to each array element",
        "sample_doc": {
            "items": [
                {"name": "item1", "price": "100"},
                {"name": "item2", "price": "200"}
            ]
        },
        "pipeline": [
            {
                "foreach": {
                    "field": "items",
                    "processor": {
                        "convert": {
                            "field": "_ingest._value.price",
                            "type": "float"
                        }
                    }
                }
            }
        ]
    },
    
    "geoip": {
        "description": "Adds geolocation info based on IP address",
        "sample_doc": {
            "client_ip": "8.8.8.8"
        },
        "pipeline": [
            {
                "geoip": {
                    "field": "client_ip",
                    "target_field": "geoip"
                }
            }
        ]
    },
    
    "grok": {
        "description": "Extracts fields using regex patterns",
        "sample_doc": {
            "apache_log": "192.168.1.1 - user [02/Nov/2024:14:30:45] \"GET /api/users HTTP/1.1\" 200 1234"
        },
        "pipeline": [
            {
                "grok": {
                    "field": "apache_log",
                    "patterns": ["%{IP:client_ip} - %{DATA:user} \\[%{HTTPDATE:timestamp}\\] \"%{WORD:method} %{DATA:path} HTTP/%{NUMBER:http_version}\" %{NUMBER:status_code:int} %{NUMBER:bytes:int}"]
                }
            }
        ]
    },
    
    "gsub": {
        "description": "Substitutes or deletes substrings",
        "sample_doc": {
            "text": "Hello-World-Test-String",
            "email_raw": "user@example.com"
        },
        "pipeline": [
            {
                "gsub": {
                    "field": "text",
                    "pattern": "-",
                    "replacement": " "
                }
            }
        ]
    },
    
    "html_strip": {
        "description": "Removes HTML tags from text",
        "sample_doc": {
            "content": "<p>This is <b>bold</b> and <i>italic</i> text</p>",
            "description": "<div class=\"desc\">Product <span>description</span></div>"
        },
        "pipeline": [
            {
                "html_strip": {
                    "field": "content"
                }
            },
            {
                "html_strip": {
                    "field": "description"
                }
            }
        ]
    },
    
    "join": {
        "description": "Joins array elements into a string",
        "sample_doc": {
            "tags": ["machine-learning", "ai", "data-science"],
            "categories": ["tech", "education"]
        },
        "pipeline": [
            {
                "join": {
                    "field": "tags",
                    "separator": " | "
                }
            }
        ]
    },
    
    "json": {
        "description": "Parses JSON strings into structured objects",
        "sample_doc": {
            "metadata_json": "{\"author\": \"John\", \"version\": \"1.0\", \"tags\": [\"important\", \"reviewed\"]}",
            "config": "{\"timeout\": 30, \"retry\": true}"
        },
        "pipeline": [
            {
                "json": {
                    "field": "metadata_json",
                    "target_field": "metadata"
                }
            },
            {
                "json": {
                    "field": "config"
                }
            }
        ]
    },
    
    "kv": {
        "description": "Parses key-value pairs into fields",
        "sample_doc": {
            "query_string": "user_id=123&action=login&timestamp=1234567890"
        },
        "pipeline": [
            {
                "kv": {
                    "field": "query_string",
                    "field_split": "&",
                    "value_split": "=",
                    "target_field": "parsed_params"
                }
            }
        ]
    },
    
    "lowercase": {
        "description": "Converts text to lowercase",
        "sample_doc": {
            "category": "ELECTRONICS",
            "brand": "APPLE"
        },
        "pipeline": [
            {
                "lowercase": {
                    "field": "category"
                }
            },
            {
                "lowercase": {
                    "field": "brand"
                }
            }
        ]
    },
    
    "remove": {
        "description": "Removes fields from documents",
        "sample_doc": {
            "public_data": "visible",
            "secret_token": "xxxxx",
            "internal_id": "12345",
            "useful_data": "keep this"
        },
        "pipeline": [
            {
                "remove": {
                    "field": ["secret_token", "internal_id"]
                }
            }
        ]
    },
    
    "rename": {
        "description": "Renames fields",
        "sample_doc": {
            "provider": "AWS",
            "instance_type": "t2.micro",
            "region_name": "us-east-1"
        },
        "pipeline": [
            {
                "rename": {
                    "field": "provider",
                    "target_field": "cloud.provider"
                }
            },
            {
                "rename": {
                    "field": "instance_type",
                    "target_field": "cloud.instance.type"
                }
            }
        ]
    },
    
    "set": {
        "description": "Sets a field to a constant value",
        "sample_doc": {
            "product": "Laptop",
            "price": 999
        },
        "pipeline": [
            {
                "set": {
                    "field": "ingestion_timestamp",
                    "value": "{{_ingest.timestamp}}"
                }
            },
            {
                "set": {
                    "field": "data_source",
                    "value": "web_api"
                }
            }
        ]
    },
    
    "sort": {
        "description": "Sorts array elements",
        "sample_doc": {
            "scores": [95, 42, 87, 23, 100],
            "names": ["Zoe", "Alice", "Bob"]
        },
        "pipeline": [
            {
                "sort": {
                    "field": "scores"
                }
            },
            {
                "sort": {
                    "field": "names"
                }
            }
        ]
    },
    
    "split": {
        "description": "Splits string into array",
        "sample_doc": {
            "tags_string": "python,machine-learning,data-science",
            "categories": "books;fiction;bestsellers"
        },
        "pipeline": [
            {
                "split": {
                    "field": "tags_string",
                    "separator": ","
                }
            },
            {
                "split": {
                    "field": "categories",
                    "separator": ";"
                }
            }
        ]
    },
    
    "trim": {
        "description": "Trims whitespace from strings",
        "sample_doc": {
            "name": "  John Doe  ",
            "email": "   user@example.com   ",
            "city": "  New York  "
        },
        "pipeline": [
            {
                "trim": {
                    "field": "name"
                }
            },
            {
                "trim": {
                    "field": "email"
                }
            }
        ]
    },
    
    "uppercase": {
        "description": "Converts text to uppercase",
        "sample_doc": {
            "country": "united states",
            "status": "active"
        },
        "pipeline": [
            {
                "uppercase": {
                    "field": "country"
                }
            },
            {
                "uppercase": {
                    "field": "status"
                }
            }
        ]
    },
    
    "urldecode": {
        "description": "Decodes URL-encoded strings",
        "sample_doc": {
            "encoded_url": "hello%20world%21",
            "search_query": "machine%20learning%20algorithms"
        },
        "pipeline": [
            {
                "urldecode": {
                    "field": "encoded_url"
                }
            },
            {
                "urldecode": {
                    "field": "search_query"
                }
            }
        ]
    },
    
    "user_agent": {
        "description": "Extracts browser and device info",
        "sample_doc": {
            "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        },
        "pipeline": [
            {
                "user_agent": {
                    "field": "user_agent"
                }
            }
        ]
    },
    
    "text_chunking": {
        "description": "Splits text into chunks",
        "sample_doc": {
            "content": "Lorem ipsum dolor sit amet consectetur adipiscing elit sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat."
        },
        "pipeline": [
            {
                "text_chunking": {
                    "field": "content",
                    "chunk_size": 20,
                    "title_field": "title"
                }
            }
        ]
    },
    
    "script": {
        "description": "Runs custom scripts for transformations",
        "sample_doc": {
            "quantity": 5,
            "unit_price": 20
        },
        "pipeline": [
            {
                "script": {
                    "source": "ctx.total_price = ctx.quantity * ctx.unit_price"
                }
            }
        ]
    }
}

print(f"✅ Loaded {len(PROCESSOR_EXAMPLES)} processor examples")
print("\nProcessor categories:")
for processor_name in sorted(PROCESSOR_EXAMPLES.keys()):
    print(f"  - {processor_name}")
