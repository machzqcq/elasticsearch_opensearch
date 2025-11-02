"""
Ingest Pipelines Python Implementation
This script demonstrates various ingest pipeline operations in OpenSearch using Python.
Based on the shell script ingest_pipelines.sh, this provides Python equivalents
for all the pipeline operations.
"""

from opensearchpy import OpenSearch
import json
import sys
sys.path.append('../../')

IS_AUTH = True  # Set to False if security is disabled
HOST = 'localhost'  # Replace with your OpenSearch host, if running everything locally use 'localhost'

# Initialize the OpenSearch client (reusing pattern from create-ingest-interns.py)
if IS_AUTH:
    client = OpenSearch(
        hosts=[{'host': HOST, 'port': 9200}],
        http_auth=('admin', 'Developer@123'),  # Replace with your credentials
        use_ssl=True,
        verify_certs=False,
        ssl_show_warn=False
    )
else:
    client = OpenSearch(
        hosts=[{'host': HOST, 'port': 9200}],
        use_ssl=False,
        verify_certs=False,
        ssl_assert_hostname=False,
        ssl_show_warn=False
    )

def print_response(title, response):
    """Helper function to print responses in a formatted way"""
    print(f"\n{'=' * 50}")
    print(f"✓ {title}")
    print('=' * 50)
    print(json.dumps(response, indent=2, default=str))

def create_basic_pipeline():
    """Create a basic ingest pipeline"""
    pipeline_body = {
        "description": "This pipeline processes student data",
        "processors": [
            {
                "set": {
                    "description": "Sets the graduation year to 2023",
                    "field": "grad_year",
                    "value": 2023
                }
            },
            {
                "set": {
                    "description": "Sets graduated to true",
                    "field": "graduated",
                    "value": True
                }
            },
            {
                "uppercase": {
                    "field": "name"
                }
            }
        ]
    }
    
    # Create the pipeline
    response = client.ingest.put_pipeline(id='my-pipeline', body=pipeline_body)
    print_response("Created pipeline 'my-pipeline'", response)
    return response

def get_all_pipelines():
    """Get all ingest pipelines"""
    response = client.ingest.get_pipeline()
    print_response("All ingest pipelines", response)
    return response

def get_specific_pipeline(pipeline_id):
    """Get a specific pipeline"""
    response = client.ingest.get_pipeline(id=pipeline_id)
    print_response(f"Pipeline '{pipeline_id}'", response)
    return response

def delete_pipeline(pipeline_id):
    """Delete a specific pipeline"""
    response = client.ingest.delete_pipeline(id=pipeline_id)
    print_response(f"Deleted pipeline '{pipeline_id}'", response)
    return response

def simulate_existing_pipeline():
    """Simulate an existing pipeline with test documents"""
    simulation_body = {
        "docs": [
            {
                "_index": "my-index",
                "_id": "1",
                "_source": {
                    "grad_year": 2024,
                    "graduated": "",
                    "name": "John Doe"
                }
            },
            {
                "_index": "my-index",
                "_id": "2",
                "_source": {
                    "grad_year": 2025,
                    "graduated": False,
                    "name": "Jane Doe"
                }
            }
        ]
    }
    
    response = client.ingest.simulate(id='my-pipeline', body=simulation_body)
    print_response("Simulated pipeline 'my-pipeline'", response)
    return response

def simulate_inline_pipeline():
    """Simulate a pipeline defined inline without creating it first"""
    simulation_body = {
        "pipeline": {
            "description": "Splits text on white space characters",
            "processors": [
                {
                    "csv": {
                        "field": "name",
                        "separator": ",",
                        "target_fields": ["last_name", "first_name"],
                        "trim": True
                    }
                },
                {
                    "uppercase": {
                        "field": "last_name"
                    }
                }
            ]
        },
        "docs": [
            {
                "_index": "second-index",
                "_id": "1",
                "_source": {
                    "name": "Doe,John"
                }
            },
            {
                "_index": "second-index",
                "_id": "2",
                "_source": {
                    "name": "Doe, Jane"
                }
            }
        ]
    }
    
    response = client.ingest.simulate(body=simulation_body)
    print_response("Simulated inline pipeline", response)
    return response

def create_example_pipeline():
    """Create a pipeline that accesses input data using ctx object"""
    pipeline_body = {
        "description": "Sets tags, log label, and defaults error message",
        "processors": [
            {
                "set": {
                    "field": "tagline",
                    "value": "{{{user.first}}} from {{{department}}}"
                }
            },
            {
                "script": {
                    "lang": "painless",
                    "source": "ctx.year = ctx.date.substring(0, 4);"
                }
            },
            {
                "set": {
                    "field": "received_at",
                    "value": "{{_ingest.timestamp}}"
                }
            }
        ]
    }
    
    response = client.ingest.put_pipeline(id='example-pipeline', body=pipeline_body)
    print_response("Created pipeline 'example-pipeline'", response)
    return response

def simulate_example_pipeline():
    """Simulate the example pipeline"""
    simulation_body = {
        "docs": [
            {
                "_source": {
                    "user": {
                        "first": "Liam"
                    },
                    "department": "Engineering",
                    "date": "2024-12-03T14:05:00Z"
                }
            }
        ]
    }
    
    response = client.ingest.simulate(id='example-pipeline', body=simulation_body)
    print_response("Simulated example pipeline", response)
    return response

def create_conditional_drop_pipeline():
    """Create a pipeline that conditionally drops documents"""
    pipeline_body = {
        "processors": [
            {
                "drop": {
                    "if": "ctx.log_level == 'debug'"
                }
            }
        ]
    }
    
    response = client.ingest.put_pipeline(id='drop_debug_logs', body=pipeline_body)
    print_response("Created conditional drop pipeline", response)
    return response

def test_conditional_drop_pipeline():
    """Test the conditional drop pipeline by indexing documents"""
    # This document should be dropped
    try:
        response1 = client.index(
            index='logs',
            id='1',
            body={
                "message": "User logged in",
                "log_level": "debug"
            },
            pipeline='drop_debug_logs'
        )
        print_response("Document with debug level (should be dropped)", response1)
    except Exception as e:
        print(f"Expected behavior - debug document dropped: {e}")
    
    # This document should be indexed
    response2 = client.index(
        index='logs',
        id='2',
        body={
            "message": "User logged in",
            "log_level": "info"
        },
        pipeline='drop_debug_logs'
    )
    print_response("Document with info level (should be indexed)", response2)

def create_multi_step_conditional_pipeline():
    """Create a multi-step conditional pipeline"""
    pipeline_body = {
        "processors": [
            {
                "set": {
                    "field": "user",
                    "value": "guest",
                    "if": "ctx.user == null"
                }
            },
            {
                "set": {
                    "field": "error",
                    "value": True,
                    "if": "ctx.status_code != null && ctx.status_code >= 400"
                }
            },
            {
                "drop": {
                    "if": "ctx.app?.env == 'debug'"
                }
            }
        ]
    }
    
    response = client.ingest.put_pipeline(id='logs_processing', body=pipeline_body)
    print_response("Created multi-step conditional pipeline", response)
    return response

def simulate_multi_step_conditional_pipeline():
    """Simulate the multi-step conditional pipeline"""
    simulation_body = {
        "docs": [
            {
                "_source": {
                    "message": "Successful login",
                    "status_code": 200
                }
            },
            {
                "_source": {
                    "message": "Database error",
                    "status_code": 500,
                    "user": "alice"
                }
            },
            {
                "_source": {
                    "message": "Debug mode trace",
                    "app": {"env": "debug"}
                }
            }
        ]
    }
    
    response = client.ingest.simulate(id='logs_processing', body=simulation_body)
    print_response("Simulated multi-step conditional pipeline", response)
    return response

def create_sub_pipelines():
    """Create sub-pipelines for routing example"""
    # Create webapp logs pipeline
    webapp_pipeline = {
        "processors": [
            {"set": {"field": "log_type", "value": "webapp"}}
        ]
    }
    client.ingest.put_pipeline(id='webapp_logs', body=webapp_pipeline)
    
    # Create api logs pipeline
    api_pipeline = {
        "processors": [
            {"set": {"field": "log_type", "value": "api"}}
        ]
    }
    client.ingest.put_pipeline(id='api_logs', body=api_pipeline)
    
    # Create service router pipeline
    router_pipeline = {
        "processors": [
            {
                "pipeline": {
                    "name": "webapp_logs",
                    "if": "ctx.service?.name == 'webapp'"
                }
            },
            {
                "pipeline": {
                    "name": "api_logs",
                    "if": "ctx.service?.name == 'api'"
                }
            }
        ]
    }
    client.ingest.put_pipeline(id='service_router', body=router_pipeline)
    
    print_response("Created sub-pipelines and service router", {"status": "success"})

def simulate_service_router_pipeline():
    """Simulate the service router pipeline"""
    simulation_body = {
        "docs": [
            {"_source": {"service": {"name": "webapp"}, "message": "Homepage loaded"}},
            {"_source": {"service": {"name": "api"}, "message": "GET /v1/users"}},
            {"_source": {"service": {"name": "worker"}, "message": "Task started"}}
        ]
    }
    
    response = client.ingest.simulate(id='service_router', body=simulation_body)
    print_response("Simulated service router pipeline", response)
    return response

def create_regex_conditional_pipelines():
    """Create pipelines with regex conditionals"""
    
    # Email domain filtering
    email_pipeline = {
        "processors": [
            {
                "set": {
                    "field": "user_domain",
                    "value": "example.com",
                    "if": "ctx.email != null && ctx.email =~ /@example.com$/"
                }
            }
        ]
    }
    client.ingest.put_pipeline(id='tag_example_com_users', body=email_pipeline)
    
    # IPv6 detection
    ipv6_pipeline = {
        "processors": [
            {
                "set": {
                    "field": "ip_type",
                    "value": "IPv6",
                    "if": "ctx.ip != null && ctx.ip =~ /^[a-fA-F0-9:]+$/ && ctx.ip.contains(':')"
                }
            }
        ]
    }
    client.ingest.put_pipeline(id='ipv6_flagger', body=ipv6_pipeline)
    
    # UUID validation
    uuid_pipeline = {
        "processors": [
            {
                "set": {
                    "field": "valid_uuid",
                    "value": True,
                    "if": "ctx.session_id != null && ctx.session_id =~ /^[a-f0-9]{8}-[a-f0-9]{4}-4[a-f0-9]{3}-[89ab][a-f0-9]{3}-[a-f0-9]{12}$/"
                }
            }
        ]
    }
    client.ingest.put_pipeline(id='uuid_checker', body=uuid_pipeline)
    
    print_response("Created regex conditional pipelines", {"status": "success"})

def simulate_regex_pipelines():
    """Simulate the regex conditional pipelines"""
    
    # Test email pipeline
    email_simulation = {
        "docs": [
            {"_source": {"email": "alice@example.com"}},
            {"_source": {"email": "bob@another.com"}}
        ]
    }
    response1 = client.ingest.simulate(id='tag_example_com_users', body=email_simulation)
    print_response("Email domain filtering simulation", response1)
    
    # Test IPv6 pipeline
    ipv6_simulation = {
        "docs": [
            {"_source": {"ip": "2001:0db8:85a3:0000:0000:8a2e:0370:7334"}},
            {"_source": {"ip": "192.168.0.1"}}
        ]
    }
    response2 = client.ingest.simulate(id='ipv6_flagger', body=ipv6_simulation)
    print_response("IPv6 detection simulation", response2)
    
    # Test UUID pipeline
    uuid_simulation = {
        "docs": [
            {"_source": {"session_id": "550e8400-e29b-41d4-a716-446655440000"}},
            {"_source": {"session_id": "invalid-uuid-1234"}}
        ]
    }
    response3 = client.ingest.simulate(id='uuid_checker', body=uuid_simulation)
    print_response("UUID validation simulation", response3)

def cleanup_pipelines():
    """Clean up all created pipelines"""
    pipeline_ids = [
        'my-pipeline', 'example-pipeline', 'drop_debug_logs', 'logs_processing',
        'webapp_logs', 'api_logs', 'service_router', 'tag_example_com_users',
        'ipv6_flagger', 'uuid_checker'
    ]
    
    for pipeline_id in pipeline_ids:
        try:
            client.ingest.delete_pipeline(id=pipeline_id)
            print(f"✓ Deleted pipeline: {pipeline_id}")
        except Exception as e:
            print(f"✗ Failed to delete pipeline {pipeline_id}: {e}")

def main():
    """Main function to run all ingest pipeline operations"""
    try:
        print("🚀 Starting Ingest Pipeline Operations...")
        
        # Basic pipeline operations
        print("\n📝 BASIC PIPELINE OPERATIONS")
        create_basic_pipeline()
        get_all_pipelines()
        get_specific_pipeline('my-pipeline')
        simulate_existing_pipeline()
        
        # Inline pipeline simulation
        print("\n🔄 INLINE PIPELINE SIMULATION")
        simulate_inline_pipeline()
        
        # Context access pipeline
        print("\n📊 CONTEXT ACCESS PIPELINE")
        create_example_pipeline()
        simulate_example_pipeline()
        
        # Conditional pipelines
        print("\n🎯 CONDITIONAL PIPELINES")
        create_conditional_drop_pipeline()
        create_multi_step_conditional_pipeline()
        simulate_multi_step_conditional_pipeline()
        
        # Sub-pipelines and routing
        print("\n🔀 SUB-PIPELINES AND ROUTING")
        create_sub_pipelines()
        simulate_service_router_pipeline()
        
        # Regex conditional pipelines
        print("\n🔍 REGEX CONDITIONAL PIPELINES")
        create_regex_conditional_pipelines()
        simulate_regex_pipelines()
        
        print("\n✅ All ingest pipeline operations completed successfully!")
        
        # Uncomment the line below if you want to clean up all pipelines
        # cleanup_pipelines()
        
    except Exception as e:
        print(f"❌ Error occurred: {e}")

if __name__ == "__main__":
    main()