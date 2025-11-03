"""
Search Pipelines Python Implementation
This script demonstrates various search pipeline operations in OpenSearch using Python.
Based on the shell script search_pipelines.sh, this provides Python equivalents
for all the search pipeline operations including request and response processors.
"""

from opensearchpy import OpenSearch
import json
import sys
sys.path.append('../../')

IS_AUTH = True  # Set to False if security is disabled
HOST = 'localhost'  # Replace with your OpenSearch host, if running everything locally use 'localhost'
DATA_FOLDER = '../../0. DATA'

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

def create_basic_search_pipeline():
    """Create a basic search pipeline with request and response processors"""
    pipeline_body = {
        "request_processors": [
            {
                "filter_query": {
                    "tag": "tag1",
                    "description": "This processor is going to restrict to publicly visible documents",
                    "query": {
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
    
    # Create the search pipeline
    response = client.transport.perform_request(
        'PUT',
        '/_search/pipeline/my_pipeline',
        body=pipeline_body
    )
    print_response("Created search pipeline 'my_pipeline'", response)
    return response

def get_all_search_pipelines():
    """Retrieve all search pipelines"""
    response = client.transport.perform_request('GET', '/_search/pipeline')
    print_response("All search pipelines", response)
    return response

def setup_test_index_with_data():
    """Create test index and add sample documents"""
    # Create index
    try:
        client.indices.delete(index='my_index')
        print("✓ Deleted existing index")
    except:
        pass
    
    client.indices.create(index='my_index')
    print("✓ Created index 'my_index'")
    
    # Add test documents
    documents = [
        {
            "id": 1,
            "visibility": "public",
            "message": "This is message 1"
        },
        {
            "id": 2,
            "visibility": "private",
            "message": "This is message 2"
        },
        {
            "id": 3,
            "visibility": "public",
            "message": "This is message 3"
        }
    ]
    
    for doc in documents:
        response = client.index(
            index='my_index',
            body=doc,
            refresh='wait_for'
        )
    
    print_response("Added test documents", {"documents_added": len(documents)})

def search_without_pipeline():
    """Search without any pipeline"""
    response = client.search(
        index='my_index',
        body={
            "query": {
                "match_all": {}
            }
        }
    )
    print_response("Search without pipeline", response)
    return response

def search_with_pipeline_param():
    """Search with pipeline specified as query parameter"""
    response = client.search(
        index='my_index',
        search_pipeline='my_pipeline'
    )
    print_response("Search with pipeline parameter", response)
    return response

def search_with_pipeline_body():
    """Search with pipeline specified in request body"""
    response = client.search(
        index='my_index',
        body={
            "query": {
                "match_all": {}
            },
            "from": 0,
            "size": 10,
            "search_pipeline": "my_pipeline"
        }
    )
    print_response("Search with pipeline in request body", response)
    return response

def set_default_search_pipeline():
    """Set default search pipeline for an index"""
    # Recreate index
    try:
        client.indices.delete(index='my_index')
    except:
        pass
    
    client.indices.create(index='my_index')
    
    # Set default pipeline
    response = client.indices.put_settings(
        index='my_index',
        body={
            "index.search.default_pipeline": "my_pipeline"
        }
    )
    print_response("Set default search pipeline", response)
    
    # Add test documents again
    setup_test_index_with_data()
    
    return response

def search_with_default_pipeline():
    """Search using default pipeline (no explicit pipeline specified)"""
    response = client.search(
        index='my_index',
        body={
            "query": {
                "match_all": {}
            }
        }
    )
    print_response("Search with default pipeline", response)
    return response

def remove_default_pipeline():
    """Remove default search pipeline"""
    response = client.indices.put_settings(
        index='my_index',
        body={
            "index.search.default_pipeline": "_none"
        }
    )
    print_response("Removed default search pipeline", response)
    return response

def setup_collapse_example():
    """Setup data for collapse processor example"""
    # Delete and recreate index
    try:
        client.indices.delete(index='my_index')
    except:
        pass
    
    # Bulk index documents for collapse example
    bulk_body = []
    documents = [
        {"title": "document 1", "color": "blue"},
        {"title": "document 2", "color": "blue"},
        {"title": "document 3", "color": "red"},
        {"title": "document 4", "color": "red"},
        {"title": "document 5", "color": "yellow"},
        {"title": "document 6", "color": "yellow"},
        {"title": "document 7", "color": "orange"},
        {"title": "document 8", "color": "orange"},
        {"title": "document 9", "color": "green"},
        {"title": "document 10", "color": "green"}
    ]
    
    for i, doc in enumerate(documents, 1):
        bulk_body.extend([
            {"create": {"_index": "my_index", "_id": str(i)}},
            doc
        ])
    
    response = client.bulk(body=bulk_body, refresh='wait_for')
    print_response("Setup collapse example data", {"documents_indexed": len(documents)})
    return response

def create_collapse_pipeline():
    """Create a search pipeline with collapse processor"""
    pipeline_body = {
        "response_processors": [
            {
                "collapse": {
                    "field": "color"
                }
            }
        ]
    }
    
    response = client.transport.perform_request(
        'PUT',
        '/_search/pipeline/collapse_pipeline',
        body=pipeline_body
    )
    print_response("Created collapse search pipeline", response)
    return response

def test_collapse_pipeline():
    """Test the collapse pipeline"""
    response = client.search(
        index='my_index',
        search_pipeline='collapse_pipeline',
        body={
            "size": 3
        }
    )
    print_response("Search with collapse pipeline", response)
    return response

def setup_sort_example():
    """Setup data for sort processor example"""
    # Delete and recreate index
    try:
        client.indices.delete(index='my_index')
    except:
        pass
    
    # Add document with array field for sorting
    response = client.index(
        index='my_index',
        body={
            "id": 1,
            "message": [4, 2, 3, 1],
            "visibility": "public"
        },
        refresh='wait_for'
    )
    print_response("Setup sort example data", response)
    return response

def create_sort_pipeline():
    """Create a search pipeline with sort processor"""
    pipeline_body = {
        "response_processors": [
            {
                "sort": {
                    "field": "message",
                    "target_field": "sorted_message"
                }
            }
        ]
    }
    
    response = client.transport.perform_request(
        'PUT',
        '/_search/pipeline/my_pipeline',
        body=pipeline_body
    )
    print_response("Created sort search pipeline", response)
    return response

def test_sort_pipeline():
    """Test the sort pipeline"""
    # Search without pipeline
    response_without = client.search(index='my_index')
    print_response("Search without sort pipeline", response_without)
    
    # Search with sort pipeline
    response_with = client.search(
        index='my_index',
        search_pipeline='my_pipeline'
    )
    print_response("Search with sort pipeline", response_with)
    return response_with

def setup_split_example():
    """Setup data for split processor example"""
    # Delete and recreate index
    try:
        client.indices.delete(index='my_index')
    except:
        pass
    
    # Add document with string field for splitting
    response = client.index(
        index='my_index',
        id='1',
        body={
            "message": "ingest, search, visualize, and analyze data",
            "visibility": "public"
        },
        refresh='wait_for'
    )
    print_response("Setup split example data", response)
    return response

def create_split_pipeline():
    """Create a search pipeline with split processor"""
    pipeline_body = {
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
    
    response = client.transport.perform_request(
        'PUT',
        '/_search/pipeline/my_pipeline',
        body=pipeline_body
    )
    print_response("Created split search pipeline", response)
    return response

def test_split_pipeline():
    """Test the split pipeline"""
    # Search without pipeline
    response_without = client.search(index='my_index')
    print_response("Search without split pipeline", response_without)
    
    # Search with split pipeline
    response_with = client.search(
        index='my_index',
        search_pipeline='my_pipeline'
    )
    print_response("Search with split pipeline", response_with)
    return response_with

def cleanup_pipelines():
    """Clean up all created search pipelines"""
    pipeline_ids = ['my_pipeline', 'collapse_pipeline']
    
    for pipeline_id in pipeline_ids:
        try:
            client.transport.perform_request(
                'DELETE',
                f'/_search/pipeline/{pipeline_id}'
            )
            print(f"✓ Deleted search pipeline: {pipeline_id}")
        except Exception as e:
            print(f"✗ Failed to delete search pipeline {pipeline_id}: {e}")
    
    # Clean up test index
    try:
        client.indices.delete(index='my_index')
        print("✓ Deleted test index: my_index")
    except Exception as e:
        print(f"✗ Failed to delete index: {e}")

def main():
    """Main function to run all search pipeline operations"""
    try:
        print("🚀 Starting Search Pipeline Operations...")
        
        # Basic search pipeline operations
        print("\n📝 BASIC SEARCH PIPELINE OPERATIONS")
        create_basic_search_pipeline()
        get_all_search_pipelines()
        
        # Setup test data and basic searches
        print("\n🔍 BASIC SEARCH OPERATIONS")
        setup_test_index_with_data()
        search_without_pipeline()
        search_with_pipeline_param()
        search_with_pipeline_body()
        
        # Default pipeline operations
        print("\n🎯 DEFAULT PIPELINE OPERATIONS")
        set_default_search_pipeline()
        search_with_default_pipeline()
        remove_default_pipeline()
        search_without_pipeline()
        
        # Collapse processor
        print("\n🗃️ COLLAPSE PROCESSOR")
        setup_collapse_example()
        create_collapse_pipeline()
        test_collapse_pipeline()
        
        # Sort processor
        print("\n📊 SORT PROCESSOR")
        setup_sort_example()
        create_sort_pipeline()
        test_sort_pipeline()
        
        # Split processor
        print("\n✂️ SPLIT PROCESSOR")
        setup_split_example()
        create_split_pipeline()
        test_split_pipeline()
        
        print("\n✅ All search pipeline operations completed successfully!")
        
        # Uncomment the line below if you want to clean up all pipelines
        # cleanup_pipelines()
        
    except Exception as e:
        print(f"❌ Error occurred: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()