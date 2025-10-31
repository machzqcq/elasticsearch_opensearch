"""
Business Intelligence RAG Application
=====================================

This Gradio application provides a complete workflow for:
1. Extracting database metadata from PostgreSQL
2. Enhancing metadata with LLM-generated descriptions
3. Ingesting metadata into OpenSearch with embeddings
4. Converting natural language queries to SQL using RAG
5. Executing SQL queries on the database
6. Creating visualizations from query results
7. Generating business insights using LLM

Author: Adapted from opensearch-POSTGRES-RAG notebooks
"""

import gradio as gr
import pandas as pd
import numpy as np
import json
import os
import sys
import time
import warnings
import requests
import io
from datetime import datetime
from typing import Dict, List, Tuple, Optional, Any

# Database imports
import sqlalchemy
from sqlalchemy import create_engine, text, MetaData, inspect
import psycopg2
import urllib.parse

# OpenSearch imports
from opensearchpy import OpenSearch, helpers
from opensearch_py_ml.ml_commons import MLCommonClient

# Visualization imports
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend for Gradio
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Excel handling
import openpyxl
from openpyxl import Workbook

# Environment variables
from dotenv import load_dotenv

# Suppress warnings
warnings.filterwarnings('ignore')

# Load environment variables
load_dotenv(".env")

# ============================================================================
# GLOBAL CONFIGURATION
# ============================================================================

# OpenSearch Configuration
OPENSEARCH_HOST = 'localhost'
OPENSEARCH_PORT = 9200
OPENSEARCH_USERNAME = 'admin'
OPENSEARCH_PASSWORD = 'Developer@123'
OPENSEARCH_CLUSTER_URL = {'host': OPENSEARCH_HOST, 'port': OPENSEARCH_PORT}

# DeepSeek Configuration
DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"
DEEPSEEK_API_KEY = os.getenv('DEEPSEEK_API_KEY')
DEEPSEEK_MODEL = 'deepseek-chat'

# Sampling Configuration
SAMPLING_COUNT = 10
SCHEMAS_TO_EXCLUDE = ['information_schema', 'pg_catalog']

# Global state variables
global_state = {
    'db_connector': None,
    'os_client': None,
    'ml_client': None,
    'model_id': None,
    'metadata_df': None,
    'metadata_enhanced_df': None,
    'index_name': 'adventure_works_meta_ai_ready',
    'pipeline_name': 'metadata_embedding_pipeline',
    'last_query_result': None,
    'last_sql': None,
    'last_dataframe': None,
    'last_query': None,
    'last_metadata_context': None
}

# ============================================================================
# DATABASE CONNECTION CLASS
# ============================================================================

class PostgreSQLConnector:
    """PostgreSQL Database Connector using SQLAlchemy and psycopg2"""
    
    def __init__(self):
        self.host = os.getenv('POSTGRES_HOST', 'localhost')
        self.user = os.getenv('POSTGRES_USER', 'postgres')
        self.password = os.getenv('POSTGRES_PASSWORD', 'postgres')
        self.database = os.getenv('POSTGRES_DB', 'Adventureworks')
        self.port = int(os.getenv('POSTGRES_PORT', '5432'))
        self.engine = None
        self.connection = None
    
    def create_connection_string(self):
        """Create PostgreSQL connection string"""
        password_encoded = urllib.parse.quote_plus(self.password)
        connection_string = (
            f"postgresql+psycopg2://{self.user}:{password_encoded}"
            f"@{self.host}:{self.port}/{self.database}"
        )
        return connection_string
    
    def connect(self):
        """Establish connection to PostgreSQL database"""
        try:
            connection_string = self.create_connection_string()
            self.engine = create_engine(connection_string)
            self.connection = self.engine.connect()
            return True, f"✅ Connected to {self.database} at {self.host}:{self.port}"
        except Exception as e:
            return False, f"❌ Connection failed: {str(e)}"
    
    def execute_query(self, query, params=None):
        """Execute SQL query and return results as DataFrame"""
        try:
            if params:
                result = pd.read_sql_query(text(query), self.connection, params=params)
            else:
                result = pd.read_sql_query(text(query), self.connection)
            return result
        except Exception as e:
            error_msg = str(e)
            print(f"Query execution error: {error_msg}")
            
            # If transaction is aborted, try to rollback and retry once
            if "transaction is aborted" in error_msg or "InFailedSqlTransaction" in error_msg:
                print("Attempting to rollback and retry...")
                try:
                    self.connection.rollback()
                    # Retry the query
                    if params:
                        result = pd.read_sql_query(text(query), self.connection, params=params)
                    else:
                        result = pd.read_sql_query(text(query), self.connection)
                    return result
                except Exception as retry_error:
                    print(f"Retry failed: {str(retry_error)}")
                    return None
            
            return None
    
    def get_tables(self):
        """Get list of all tables in the database"""
        query = """
        SELECT table_schema, table_name
        FROM information_schema.tables
        WHERE table_type = 'BASE TABLE'
        AND table_schema NOT IN ('information_schema', 'pg_catalog')
        ORDER BY table_schema, table_name
        """
        return self.execute_query(query)
    
    def get_columns(self, schema_name=None, table_name=None):
        """Get column information for tables"""
        query = """
        SELECT 
            TABLE_SCHEMA,
            TABLE_NAME,
            COLUMN_NAME,
            DATA_TYPE,
            COLUMN_DEFAULT,
            ORDINAL_POSITION,
            IS_NULLABLE,
            CHARACTER_MAXIMUM_LENGTH,
            NUMERIC_PRECISION,
            NUMERIC_SCALE
        FROM information_schema.columns
        WHERE table_schema NOT IN ('information_schema', 'pg_catalog')
        """
        
        if schema_name:
            query += f" AND table_schema = '{schema_name}'"
        if table_name:
            query += f" AND table_name = '{table_name}'"
        
        query += " ORDER BY table_schema, table_name, ordinal_position"
        
        return self.execute_query(query)

# ============================================================================
# OPENSEARCH CONNECTION AND SETUP
# ============================================================================

def get_opensearch_client(cluster_url=OPENSEARCH_CLUSTER_URL, 
                         username=OPENSEARCH_USERNAME, 
                         password=OPENSEARCH_PASSWORD):
    """Create and return an OpenSearch client"""
    client = OpenSearch(
        hosts=[cluster_url],
        http_auth=(username, password),
        verify_certs=False,
        ssl_assert_hostname=False,
        ssl_show_warn=False,
        use_ssl=True,
        max_retries=10,
        retry_on_timeout=True,
        timeout=300
    )
    return client

def initialize_opensearch():
    """Initialize OpenSearch client and configure cluster"""
    try:
        os_client = get_opensearch_client()
        ml_client = MLCommonClient(os_client)
        
        # Configure cluster settings
        cluster_settings = {
            "persistent": {
                "plugins.ml_commons.trusted_connector_endpoints_regex": [".*"],
                "plugins.ml_commons.only_run_on_ml_node": "false",
                "plugins.ml_commons.memory_feature_enabled": "true",
                "plugins.ml_commons.connector.private_ip_enabled": "true"
            }
        }
        os_client.cluster.put_settings(body=cluster_settings)
        
        return True, "✅ OpenSearch client initialized successfully", os_client, ml_client
    except Exception as e:
        return False, f"❌ OpenSearch initialization failed: {str(e)}", None, None

def register_embedding_model(ml_client):
    """Register and deploy sentence transformer model, or reuse existing one"""
    try:
        model_name = "huggingface/sentence-transformers/all-MiniLM-L12-v2"
        model_version = "1.0.1"
        model_format = "TORCH_SCRIPT"
        
        # Check for existing deployed models using ML plugin API
        try:
            # Get the os_client from global state to use the ML search endpoint
            os_client = global_state.get('os_client')
            if os_client:
                # Search for models using the ML plugin API
                response = os_client.transport.perform_request(
                    'GET',
                    '/_plugins/_ml/models/_search',
                    body={
                        "query": {
                            "bool": {
                                "must": [
                                    {"term": {"name.keyword": model_name}},
                                    {"term": {"model_state": "DEPLOYED"}}
                                ]
                            }
                        },
                        "size": 1
                    }
                )
                
                if response and response.get('hits', {}).get('total', {}).get('value', 0) > 0:
                    hit = response['hits']['hits'][0]
                    existing_model_id = hit['_id']
                    model_info = hit.get('_source', {})
                    print(f"DEBUG: Found existing deployed model: {existing_model_id} (state: {model_info.get('model_state')})")
                    return True, f"🔄 Reusing existing model (ID: {existing_model_id}) - No deployment needed!", existing_model_id
        except Exception as check_error:
            print(f"DEBUG: Error checking existing models: {check_error}")
            # Continue to register new model if check fails
        
        # No existing model found, register a new one
        print(f"DEBUG: No existing deployed model found. Registering new model...")
        model_id = ml_client.register_pretrained_model(
            model_name=model_name,
            model_version=model_version,
            model_format=model_format,
            deploy_model=True,
            wait_until_deployed=True
        )
        
        return True, f"🆕 New model created and deployed (ID: {model_id})", model_id
    except Exception as e:
        return False, f"❌ Model registration failed: {str(e)}", None

# ============================================================================
# METADATA EXTRACTION
# ============================================================================

def extract_database_metadata(db_connector, exclude_schemas=None):
    """Extract full metadata from database"""
    if exclude_schemas is None:
        exclude_schemas = SCHEMAS_TO_EXCLUDE
    
    try:
        # Get all columns with metadata
        metadata_df = db_connector.get_columns()
        
        if metadata_df is None or metadata_df.empty:
            return False, "❌ No metadata found", None
        
        # Filter out excluded schemas
        metadata_df = metadata_df[~metadata_df['table_schema'].isin(exclude_schemas)]
        
        # Add computed columns
        metadata_df['id'] = range(1, len(metadata_df) + 1)
        metadata_df['full_column_name'] = (
            metadata_df['table_schema'] + '.' + 
            metadata_df['table_name'] + '.' + 
            metadata_df['column_name']
        )
        
        msg = f"✅ Extracted metadata: {len(metadata_df)} columns from {metadata_df['table_name'].nunique()} tables"
        return True, msg, metadata_df
        
    except Exception as e:
        return False, f"❌ Metadata extraction failed: {str(e)}", None

def save_metadata_to_excel(metadata_df, db_name, sheet_name='Metadata'):
    """Save metadata DataFrame to Excel file"""
    try:
        filename = f"metadata_{db_name}.xlsx"
        filepath = os.path.join(os.getcwd(), filename)
        
        with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
            metadata_df.to_excel(writer, sheet_name=sheet_name, index=False)
        
        return True, f"✅ Saved to {filename}", filepath
    except Exception as e:
        return False, f"❌ Save failed: {str(e)}", None

# ============================================================================
# LLM ENHANCEMENT
# ============================================================================

def call_deepseek_api(sample_values, column_name, table_name, data_type):
    """Call DeepSeek API to generate column description"""
    if not DEEPSEEK_API_KEY:
        return f"AI description for {column_name} (API key not configured)"
    
    try:
        sample_str = ", ".join([str(val) for val in sample_values[:10] if val is not None])
        
        if not sample_str:
            return f"{data_type} column in {table_name}"
        
        prompt = f"""Based on these sample values from column '{column_name}' (type: {data_type}) in table '{table_name}':
{sample_str}

Provide a concise description (max 40 words) of what this column contains."""
        
        headers = {
            "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": "deepseek-chat",
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 300,
            "temperature": 0.1
        }
        
        response = requests.post(DEEPSEEK_API_URL, headers=headers, json=data, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            return result["choices"][0]["message"]["content"].strip()
        else:
            return f"API error for {column_name}"
            
    except Exception as e:
        return f"Error: {str(e)}"

def get_sample_values_from_db(db_connector, schema, table, column, sample_size=10):
    """Get random sample values from database column"""
    try:
        query = f"""
        SELECT "{column}"
        FROM "{schema}"."{table}"
        WHERE "{column}" IS NOT NULL
        ORDER BY RANDOM()
        LIMIT {sample_size}
        """
        
        result_df = db_connector.execute_query(query)
        
        if result_df is not None and not result_df.empty:
            column_lower = column.lower()
            if column_lower in result_df.columns:
                return result_df[column_lower].tolist()
            elif column in result_df.columns:
                return result_df[column].tolist()
        return []
            
    except Exception as e:
        return []

def enhance_metadata_with_llm(metadata_df, db_connector, progress=gr.Progress()):
    """Enhance metadata with LLM-generated descriptions"""
    try:
        df_enhanced = metadata_df.copy()
        df_enhanced['inferred_column_description'] = ""
        
        total = len(df_enhanced)
        
        for idx, row in progress.tqdm(df_enhanced.iterrows(), total=total, desc="Enhancing metadata"):
            schema = row['table_schema']
            table = row['table_name']
            column = row['column_name']
            data_type = row['data_type']
            
            # Get sample values
            sample_values = get_sample_values_from_db(db_connector, schema, table, column)
            
            if sample_values:
                description = call_deepseek_api(sample_values, column, f"{schema}.{table}", data_type)
            else:
                description = f"{data_type} column in {schema}.{table}"
            
            df_enhanced.at[idx, 'inferred_column_description'] = description
        
        msg = f"✅ Enhanced {len(df_enhanced)} columns with AI descriptions"
        return True, msg, df_enhanced
        
    except Exception as e:
        return False, f"❌ Enhancement failed: {str(e)}", None

# ============================================================================
# TABLE-LEVEL DESCRIPTIONS
# ============================================================================

def call_deepseek_api_for_table(sample_df, schema, table, column_list):
    """Generate table-level description using LLM"""
    if not DEEPSEEK_API_KEY:
        return f"Table description for {schema}.{table} (API key not configured)"
    
    try:
        sample_summary = []
        for idx, row in sample_df.iterrows():
            row_data = {col: str(val)[:50] for col, val in row.items()}
            sample_summary.append(row_data)
        
        sample_str = json.dumps(sample_summary[:3], indent=2)[:2000]
        
        prompt = f"""Based on this sample data from table '{schema}.{table}':

Columns: {', '.join(column_list[:10])}{'...' if len(column_list) > 10 else ''}
Total Columns: {len(column_list)}

Sample Rows:
{sample_str}

Provide a concise description (max 60 words) of what this table stores and its business purpose."""
        
        headers = {
            "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": "deepseek-chat",
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 400,
            "temperature": 0.1
        }
        
        response = requests.post(DEEPSEEK_API_URL, headers=headers, json=data, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            return result["choices"][0]["message"]["content"].strip()
        else:
            return f"API error for table {schema}.{table}"
            
    except Exception as e:
        return f"Error: {str(e)}"

def add_table_descriptions(metadata_df, db_connector, progress=gr.Progress()):
    """Add table-level descriptions to metadata"""
    try:
        df_with_tables = metadata_df.copy()
        
        # Get unique tables
        tables_df = df_with_tables[['table_schema', 'table_name']].drop_duplicates()
        
        table_descriptions = {}
        
        for idx, (_, row) in progress.tqdm(
            enumerate(tables_df.iterrows(), 1), 
            total=len(tables_df), 
            desc="Adding table descriptions"
        ):
            schema = row['table_schema']
            table = row['table_name']
            
            # Get sample rows
            try:
                query = f'SELECT * FROM "{schema}"."{table}" ORDER BY RANDOM() LIMIT 5'
                sample_df = db_connector.execute_query(query)
                
                if sample_df is not None and not sample_df.empty:
                    columns = list(sample_df.columns)
                    description = call_deepseek_api_for_table(sample_df, schema, table, columns)
                else:
                    description = f"Table {schema}.{table}"
                
                table_descriptions[f"{schema}.{table}"] = description
                
            except Exception as e:
                table_descriptions[f"{schema}.{table}"] = f"Table {schema}.{table}"
        
        # Add descriptions to dataframe
        df_with_tables['inferred_table_description'] = df_with_tables.apply(
            lambda row: table_descriptions.get(f"{row['table_schema']}.{row['table_name']}", ""),
            axis=1
        )
        
        msg = f"✅ Added descriptions for {len(tables_df)} tables"
        return True, msg, df_with_tables
        
    except Exception as e:
        return False, f"❌ Failed: {str(e)}", None

# ============================================================================
# OPENSEARCH INGESTION
# ============================================================================

def create_opensearch_mappings(df, model_id, pipeline_name):
    """Create OpenSearch index mappings with vector fields"""
    mappings = {
        "settings": {
            "index": {
                "knn": True,
                "default_pipeline": pipeline_name
            }
        },
        "mappings": {
            "properties": {}
        }
    }
    
    # Add mappings for each column
    for col in df.columns:
        sample_value = df[col].iloc[0] if not df[col].isna().all() else None
        
        if isinstance(sample_value, (int, np.integer)):
            mappings["mappings"]["properties"][col] = {"type": "long"}
        elif isinstance(sample_value, (float, np.floating)):
            mappings["mappings"]["properties"][col] = {"type": "double"}
        elif isinstance(sample_value, bool):
            mappings["mappings"]["properties"][col] = {"type": "boolean"}
        else:
            mappings["mappings"]["properties"][col] = {"type": "text"}
            # Add vector field for text columns
            mappings["mappings"]["properties"][f"{col}_embedding"] = {
                "type": "knn_vector",
                "dimension": 384
            }
    
    return mappings

def create_embedding_pipeline(os_client, model_id, pipeline_name, text_fields):
    """Create ingest pipeline for automatic embeddings"""
    try:
        # Create field_map
        field_map = {field: f"{field}_embedding" for field in text_fields}
        
        pipeline_body = {
            "description": f"Embedding pipeline for metadata",
            "processors": [
                {
                    "text_embedding": {
                        "model_id": model_id,
                        "field_map": field_map
                    }
                }
            ]
        }
        
        # Delete existing pipeline
        try:
            os_client.ingest.delete_pipeline(id=pipeline_name)
        except:
            pass
        
        # Create pipeline
        os_client.ingest.put_pipeline(id=pipeline_name, body=pipeline_body)
        
        return True, f"✅ Pipeline created: {pipeline_name}"
    except Exception as e:
        return False, f"❌ Pipeline creation failed: {str(e)}"

def ingest_metadata_to_opensearch(os_client, metadata_df, index_name, mappings, progress=gr.Progress()):
    """Ingest metadata into OpenSearch with embeddings"""
    try:
        print(f"DEBUG: Starting ingestion of {len(metadata_df)} rows")
        print(f"DEBUG: DataFrame columns: {list(metadata_df.columns)}")
        
        # Delete existing index
        if os_client.indices.exists(index=index_name):
            os_client.indices.delete(index=index_name)
            print(f"DEBUG: Deleted existing index {index_name}")
        
        # Create index
        os_client.indices.create(index=index_name, body=mappings)
        print(f"DEBUG: Created index {index_name}")
        
        # Prepare bulk data
        bulk_data = []
        failed_rows = []
        
        for idx, row in metadata_df.iterrows():
            try:
                doc = row.to_dict()
                
                # Convert numpy types and handle NaN values
                for key, value in doc.items():
                    if pd.isna(value):
                        doc[key] = None
                    elif isinstance(value, (np.integer, np.floating)):
                        doc[key] = value.item()
                    elif isinstance(value, np.ndarray):
                        doc[key] = value.tolist()
                
                bulk_data.append({
                    "_index": index_name,
                    "_id": doc.get('id', idx),
                    "_source": doc
                })
            except Exception as row_error:
                print(f"DEBUG: Error processing row {idx}: {row_error}")
                failed_rows.append((idx, str(row_error)))
        
        print(f"DEBUG: Prepared {len(bulk_data)} documents for bulk ingestion")
        
        if not bulk_data:
            return False, "❌ No documents to ingest - all rows failed processing"
        
        # Bulk ingest
        success_count, failed_list = helpers.bulk(
            os_client,
            bulk_data,
            chunk_size=100,
            request_timeout=120,
            raise_on_error=False
        )
        
        print(f"DEBUG: Bulk ingestion result - success: {success_count}, failed: {len(failed_list) if isinstance(failed_list, list) else failed_list}")
        
        if failed_list:
            print(f"DEBUG: Failed items: {failed_list[:5]}")  # Print first 5 failures
        
        # Refresh index
        time.sleep(2)
        os_client.indices.refresh(index=index_name)
        
        count_response = os_client.count(index=index_name)
        actual_count = count_response['count']
        
        print(f"DEBUG: Final document count in index: {actual_count}")
        
        if actual_count == 0:
            return False, f"❌ Ingestion failed: 0 documents ingested. Check pipeline and mapping issues.\n\nFailed rows during processing: {len(failed_rows)}\nBulk failures: {len(failed_list) if isinstance(failed_list, list) else failed_list}"
        
        msg = f"✅ Ingested {actual_count} documents into {index_name}"
        if failed_rows:
            msg += f"\n⚠️  {len(failed_rows)} rows failed during processing"
        
        return True, msg
        
    except Exception as e:
        print(f"DEBUG: Ingestion exception: {str(e)}")
        import traceback
        traceback.print_exc()
        return False, f"❌ Ingestion failed: {str(e)}"

# ============================================================================
# TEXT-TO-SQL RAG FUNCTIONS
# ============================================================================

def hybrid_search(os_client, query_text, index_name, model_id, fields_to_search, k=10):
    """Perform hybrid search (keyword + semantic)"""
    try:
        print(f"DEBUG hybrid_search: index={index_name}, query={query_text}, fields={fields_to_search}")
        
        # Try hybrid search first (keyword + neural)
        keyword_queries = []
        for field in fields_to_search:
            keyword_queries.append({
                "match": {field: {"query": query_text, "boost": 1.0}}
            })
        
        semantic_queries = []
        for field in fields_to_search:
            semantic_queries.append({
                "neural": {
                    f"{field}_embedding": {
                        "query_text": query_text,
                        "model_id": model_id,
                        "k": k * 2,
                        "boost": 1.5
                    }
                }
            })
        
        search_body = {
            "size": k,
            "query": {
                "bool": {
                    "should": keyword_queries + semantic_queries,
                    "minimum_should_match": 1
                }
            },
            "_source": {"excludes": ["*_embedding"]}
        }
        
        print(f"DEBUG: Trying hybrid search (keyword + neural)...")
        try:
            results = os_client.search(index=index_name, body=search_body)
            print(f"DEBUG: Hybrid search completed successfully")
            return results
        except Exception as neural_error:
            print(f"DEBUG: Neural search failed: {neural_error}, falling back to keyword-only search")
            # Fallback to keyword-only search
            search_body_keyword = {
                "size": k,
                "query": {
                    "bool": {
                        "should": keyword_queries,
                        "minimum_should_match": 1
                    }
                },
                "_source": {"excludes": ["*_embedding"]}
            }
            results = os_client.search(index=index_name, body=search_body_keyword)
            print(f"DEBUG: Keyword-only search completed successfully")
            return results
        
    except Exception as e:
        print(f"DEBUG: Search error: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

def retrieve_relevant_metadata(os_client, query_text, index_name, model_id, top_k=10):
    """Retrieve relevant metadata for query"""
    fields = ['full_column_name', 'inferred_column_description', 
              'inferred_table_description', 'table_name']
    
    print(f"DEBUG: Searching index '{index_name}' with query: '{query_text}'")
    print(f"DEBUG: Using model_id: {model_id}")
    
    results = hybrid_search(os_client, query_text, index_name, model_id, fields, top_k)
    
    if not results:
        print("DEBUG: hybrid_search returned None")
        return None
    
    print(f"DEBUG: Search results: {results.get('hits', {}).get('total', 'unknown')} total hits")
    print(f"DEBUG: Returned hits: {len(results.get('hits', {}).get('hits', []))}")
    
    if not results['hits']['hits']:
        print("DEBUG: No hits found in search results")
        return None
    
    metadata_context = []
    for hit in results['hits']['hits']:
        source = hit['_source']
        metadata_context.append(source)
    
    print(f"DEBUG: Returning {len(metadata_context)} metadata items")
    return metadata_context

def format_metadata_for_llm(metadata_list):
    """Format metadata into readable context for LLM"""
    if not metadata_list:
        return ""
    
    # Group by table
    tables = {}
    for item in metadata_list:
        table_full = f"{item.get('table_schema', '')}.{item.get('table_name', '')}"
        if table_full not in tables:
            tables[table_full] = {
                'description': item.get('inferred_table_description', ''),
                'columns': []
            }
        tables[table_full]['columns'].append({
            'name': item.get('column_name', ''),
            'type': item.get('data_type', ''),
            'description': item.get('inferred_column_description', '')
        })
    
    # Format as text
    context = ""
    for table_name, table_info in tables.items():
        context += f"\nTable: {table_name}\n"
        context += f"Description: {table_info['description']}\n"
        context += "Columns:\n"
        for col in table_info['columns']:
            context += f"  - {col['name']} ({col['type']}): {col['description']}\n"
    
    return context

def generate_sql_with_deepseek(query_text, metadata_context):
    """Generate SQL query using DeepSeek LLM"""
    if not DEEPSEEK_API_KEY:
        return None, "DeepSeek API key not configured"
    
    try:
        prompt = f"""You are a PostgreSQL expert. Generate a SQL query to answer this question:

Question: {query_text}

Available Database Schema:
{metadata_context}

Instructions:
- Generate ONLY the SQL query, no explanations
- Use proper PostgreSQL syntax with EXACT column names from the schema above
- PostgreSQL is case-sensitive: use double quotes for mixed-case identifiers (e.g., "CustomerID", "LineTotal")
- Use schema.table notation (e.g., sales.customer)
- Include appropriate JOINs if needed
- CRITICAL: Use ONLY the exact column names shown in the schema above - do not guess or modify column names
- If a column uses CamelCase (like CustomerID), preserve the exact casing with double quotes
- Return ONLY the SQL query

SQL Query:"""
        
        headers = {
            "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": "deepseek-chat",
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 1000,
            "temperature": 0.1
        }
        
        response = requests.post(DEEPSEEK_API_URL, headers=headers, json=data, timeout=60)
        
        if response.status_code == 200:
            result = response.json()
            sql_query = result["choices"][0]["message"]["content"].strip()
            
            # Clean up SQL query
            sql_query = sql_query.replace("```sql", "").replace("```", "").strip()
            
            return sql_query, None
        else:
            return None, f"API Error: {response.status_code}"
            
    except Exception as e:
        return None, f"Error: {str(e)}"

def text_to_sql_pipeline(os_client, query_text, index_name, model_id, top_k=10):
    """Complete text-to-SQL pipeline with RAG"""
    try:
        # Step 1: Retrieve relevant metadata
        metadata_list = retrieve_relevant_metadata(os_client, query_text, index_name, model_id, top_k)
        
        if not metadata_list:
            return None, "No relevant metadata found", None
        
        # Step 2: Format metadata
        metadata_context = format_metadata_for_llm(metadata_list)
        
        # Step 3: Generate SQL
        sql_query, error = generate_sql_with_deepseek(query_text, metadata_context)
        
        if error:
            return None, error, None
        
        return sql_query, None, metadata_context
        
    except Exception as e:
        return None, f"Pipeline error: {str(e)}", None

# ============================================================================
# SQL EXECUTION AND VISUALIZATION
# ============================================================================

def execute_sql_query(db_connector, sql_query):
    """Execute SQL query and return DataFrame"""
    try:
        df = db_connector.execute_query(sql_query)
        
        if df is None:
            return None, "Query execution failed"
        
        if df.empty:
            return None, "Query returned no results"
        
        return df, None
        
    except Exception as e:
        return None, f"Execution error: {str(e)}"

def analyze_dataframe(df):
    """Perform statistical analysis on DataFrame"""
    if df is None or df.empty:
        return "No data to analyze"
    
    analysis = []
    analysis.append(f"**Dataset Overview**")
    analysis.append(f"- Rows: {len(df)}")
    analysis.append(f"- Columns: {len(df.columns)}")
    analysis.append(f"- Column Names: {', '.join(df.columns)}")
    
    # Numeric columns
    numeric_cols = df.select_dtypes(include=['number']).columns
    if len(numeric_cols) > 0:
        analysis.append(f"\n**Numeric Columns ({len(numeric_cols)})**")
        for col in numeric_cols:
            stats = df[col].describe()
            analysis.append(f"- {col}: mean={stats['mean']:.2f}, std={stats['std']:.2f}, "
                          f"min={stats['min']:.2f}, max={stats['max']:.2f}")
    
    # Categorical columns
    cat_cols = df.select_dtypes(include=['object']).columns
    if len(cat_cols) > 0:
        analysis.append(f"\n**Categorical Columns ({len(cat_cols)})**")
        for col in cat_cols:
            unique_count = df[col].nunique()
            analysis.append(f"- {col}: {unique_count} unique values")
    
    return "\n".join(analysis)

def create_visualizations(df):
    """Create multiple visualizations based on DataFrame content"""
    if df is None or df.empty:
        return None, None, None, None, "No data to visualize"
    
    try:
        numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
        cat_cols = df.select_dtypes(include=['object']).columns.tolist()
        
        charts = []
        chart_descriptions = []
        
        # Chart 1: Primary visualization based on data type
        if len(numeric_cols) >= 2:
            # Scatter plot for numeric correlations
            fig1 = px.scatter(df, x=numeric_cols[0], y=numeric_cols[1], 
                           title=f"Correlation: {numeric_cols[1]} vs {numeric_cols[0]}",
                           height=400)
            charts.append(fig1)
            chart_descriptions.append(f"Scatter plot showing relationship between {numeric_cols[0]} and {numeric_cols[1]}")
            
            # Box plot if we have a categorical column
            if len(cat_cols) >= 1 and len(df) < 1000:
                fig2 = px.box(df, x=cat_cols[0], y=numeric_cols[0],
                            title=f"Distribution of {numeric_cols[0]} by {cat_cols[0]}",
                            height=400)
                charts.append(fig2)
                chart_descriptions.append(f"Box plot showing distribution across categories")
                
        elif len(numeric_cols) == 1 and len(cat_cols) >= 1:
            # Bar chart
            fig1 = px.bar(df, x=cat_cols[0], y=numeric_cols[0],
                        title=f"{numeric_cols[0]} by {cat_cols[0]}",
                        height=400)
            charts.append(fig1)
            chart_descriptions.append(f"Bar chart comparing {numeric_cols[0]} across {cat_cols[0]}")
            
            # Pie chart if reasonable number of categories
            if df[cat_cols[0]].nunique() <= 10:
                fig2 = px.pie(df, values=numeric_cols[0], names=cat_cols[0],
                            title=f"Proportion of {numeric_cols[0]} by {cat_cols[0]}",
                            height=400)
                charts.append(fig2)
                chart_descriptions.append(f"Pie chart showing proportional distribution")
                
        elif len(numeric_cols) == 1:
            # Histogram
            fig1 = px.histogram(df, x=numeric_cols[0],
                             title=f"Distribution of {numeric_cols[0]}",
                             nbins=30, height=400)
            charts.append(fig1)
            chart_descriptions.append(f"Histogram showing frequency distribution")
            
            # Box plot
            fig2 = px.box(df, y=numeric_cols[0],
                        title=f"Statistical Summary of {numeric_cols[0]}",
                        height=400)
            charts.append(fig2)
            chart_descriptions.append(f"Box plot showing quartiles and outliers")
            
        elif len(cat_cols) >= 1:
            # Value counts bar chart
            value_counts = df[cat_cols[0]].value_counts().reset_index()
            value_counts.columns = [cat_cols[0], 'count']
            fig1 = px.bar(value_counts, x=cat_cols[0], y='count',
                        title=f"Count by {cat_cols[0]}",
                        height=400)
            charts.append(fig1)
            chart_descriptions.append(f"Bar chart of counts per category")
            
            # Pie chart if reasonable number of categories
            if len(value_counts) <= 10:
                fig2 = px.pie(value_counts, values='count', names=cat_cols[0],
                            title=f"Distribution by {cat_cols[0]}",
                            height=400)
                charts.append(fig2)
                chart_descriptions.append(f"Pie chart showing percentage distribution")
        
        # Additional charts for multi-numeric data
        if len(numeric_cols) >= 3:
            # Correlation heatmap for all numeric columns (limit to first 10)
            corr_cols = numeric_cols[:10]
            corr_matrix = df[corr_cols].corr()
            fig_corr = px.imshow(corr_matrix, 
                               title="Correlation Heatmap",
                               labels=dict(color="Correlation"),
                               height=400,
                               color_continuous_scale='RdBu_r')
            charts.append(fig_corr)
            chart_descriptions.append(f"Heatmap showing correlations between numeric variables")
        
        # Line chart if data looks time-series-like (has increasing index or numeric column)
        if len(numeric_cols) >= 1 and len(df) > 2:
            fig_line = px.line(df.head(100), y=numeric_cols[0],
                             title=f"Trend: {numeric_cols[0]}",
                             height=400)
            charts.append(fig_line)
            chart_descriptions.append(f"Line chart showing trend over records")
        
        # Pad with None if we have fewer than 4 charts
        while len(charts) < 4:
            charts.append(None)
            chart_descriptions.append("")
        
        status = f"✅ Created {sum(1 for c in charts if c is not None)} visualizations"
        return charts[0], charts[1], charts[2], charts[3], status
        
    except Exception as e:
        return None, None, None, None, f"Visualization error: {str(e)}"

def generate_business_insights(df, original_query, sql_query, analysis_results):
    """Generate business insights using LLM"""
    if not DEEPSEEK_API_KEY:
        return "DeepSeek API key not configured for insights generation"
    
    try:
        # Prepare data summary
        data_summary = f"Query Results: {len(df)} rows, {len(df.columns)} columns\n"
        data_summary += f"Columns: {', '.join(df.columns)}\n\n"
        
        # Add sample data
        data_summary += "Sample Data (first 5 rows):\n"
        data_summary += df.head(5).to_string()
        
        prompt = f"""You are a business intelligence analyst. Analyze this data and provide insights.

Original Question: {original_query}

SQL Query Used:
{sql_query}

Data Analysis:
{analysis_results}

{data_summary}

Provide a comprehensive business intelligence report with:
1. **Key Findings**: Main insights from the data
2. **Trends**: Patterns and trends observed
3. **Recommendations**: Actionable business recommendations
4. **Next Steps**: Suggested follow-up analysis

Format your response in clear sections with markdown formatting."""
        
        headers = {
            "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": "deepseek-chat",
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 2000,
            "temperature": 0.7
        }
        
        response = requests.post(DEEPSEEK_API_URL, headers=headers, json=data, timeout=90)
        
        if response.status_code == 200:
            result = response.json()
            insights = result["choices"][0]["message"]["content"].strip()
            return insights
        else:
            return f"Error generating insights: {response.status_code}"
            
    except Exception as e:
        return f"Error: {str(e)}"

# ============================================================================
# GRADIO INTERFACE FUNCTIONS
# ============================================================================

def connect_to_database():
    """Connect to PostgreSQL database"""
    try:
        db_connector = PostgreSQLConnector()
        success, message = db_connector.connect()
        
        if success:
            global_state['db_connector'] = db_connector
            return message
        else:
            return message
    except Exception as e:
        return f"❌ Connection failed: {str(e)}"

def setup_opensearch(progress=gr.Progress()):
    """Initialize OpenSearch and register model"""
    try:
        progress(0, desc="🔄 Starting OpenSearch setup...")
        status_updates = []
        
        # Step 1: Initialize OpenSearch
        progress(0.3, desc="🔌 Connecting to OpenSearch cluster...")
        success, message, os_client, ml_client = initialize_opensearch()
        if not success:
            return f"❌ {message}"
        
        global_state['os_client'] = os_client
        global_state['ml_client'] = ml_client
        status_updates.append(f"✅ Step 1/2: {message}")
        
        # Step 2: Register embedding model
        progress(0.7, desc="📦 Checking/Registering embedding model...")
        success, msg, model_id = register_embedding_model(ml_client)
        if not success:
            return f"{status_updates[0]}\n❌ Step 2/2: {msg}"
        
        global_state['model_id'] = model_id
        status_updates.append(f"\n📋 Step 2/2: Embedding Model Status")
        status_updates.append(f"   {msg}")
        
        progress(1.0, desc="✅ OpenSearch setup complete!")
        status_updates.append(f"\n💡 Embedding pipeline will be created during ingestion (Tab 5)")
        
        return "\n".join(status_updates)
    except Exception as e:
        return f"❌ Setup failed: {str(e)}"

def extract_metadata_ui(progress=gr.Progress()):
    """Extract metadata from database (UI function)"""
    db_connector = global_state.get('db_connector')
    if not db_connector:
        return "❌ Please connect to database first", None
    
    success, message, metadata_df = extract_database_metadata(db_connector)
    
    if success:
        global_state['metadata_df'] = metadata_df
        return message, metadata_df.head(20)
    else:
        return message, None

def enhance_metadata_ui(progress=gr.Progress()):
    """Enhance metadata with LLM (UI function)"""
    metadata_df = global_state.get('metadata_df')
    db_connector = global_state.get('db_connector')
    
    if metadata_df is None:
        return "❌ Please extract metadata first", None
    if db_connector is None:
        return "❌ Database not connected", None
    
    success, message, enhanced_df = enhance_metadata_with_llm(metadata_df, db_connector, progress)
    
    if success:
        global_state['metadata_enhanced_df'] = enhanced_df
        return message, enhanced_df.head(20)
    else:
        return message, None

def add_table_descriptions_ui(progress=gr.Progress()):
    """Add table descriptions (UI function)"""
    metadata_df = global_state.get('metadata_enhanced_df')
    if metadata_df is None:
        metadata_df = global_state.get('metadata_df')
    
    db_connector = global_state.get('db_connector')
    
    if metadata_df is None:
        return "❌ No metadata available", None
    if db_connector is None:
        return "❌ Database not connected", None
    
    success, message, df_with_tables = add_table_descriptions(metadata_df, db_connector, progress)
    
    if success:
        global_state['metadata_enhanced_df'] = df_with_tables
        return message, df_with_tables.head(20)
    else:
        return message, None

def upload_metadata_ui(file):
    """Upload previously generated metadata Excel file (UI function)"""
    if file is None:
        return "❌ No file uploaded", None
    
    try:
        # Read the uploaded Excel file from "Metadata_Enhanced" sheet
        df = pd.read_excel(file.name, sheet_name='Metadata_Enhanced')
        
        # Create a mapping of lowercase column names to original column names
        col_mapping = {col.lower(): col for col in df.columns}
        
        # Validate that it has the expected columns (case-insensitive)
        required_columns = {'table_schema', 'table_name', 'column_name', 'data_type'}
        df_columns_lower = set(col_mapping.keys())
        
        if not required_columns.issubset(df_columns_lower):
            missing = required_columns - df_columns_lower
            return f"❌ Invalid metadata file. Missing columns: {missing}", None
        
        # Standardize column names to lowercase
        df.columns = [col.lower() for col in df.columns]
        
        # Add id column if not present
        if 'id' not in df.columns:
            df['id'] = range(1, len(df) + 1)
        
        # Add full_column_name if not present
        if 'full_column_name' not in df.columns:
            df['full_column_name'] = (
                df['table_schema'] + '.' + 
                df['table_name'] + '.' + 
                df['column_name']
            )
        
        # Store in global state
        global_state['metadata_enhanced_df'] = df
        
        # Check if it has AI-enhanced columns (case-insensitive check)
        df_columns_lower_set = set(df.columns)
        has_column_desc = 'inferred_column_description' in df_columns_lower_set
        has_table_desc = 'inferred_table_description' in df_columns_lower_set
        
        # Build detailed status message
        status_msg = f"✅ Loaded metadata from Excel: {len(df)} rows, {len(df.columns)} columns"
        status_msg += f"\n📊 Tables: {df['table_name'].nunique()}, Columns: {len(df)}"
        
        if has_column_desc:
            non_empty = df['inferred_column_description'].notna().sum()
            status_msg += f"\n✅ Contains column descriptions ({non_empty} populated)"
        
        if has_table_desc:
            non_empty = df['inferred_table_description'].notna().sum()
            status_msg += f"\n✅ Contains table descriptions ({non_empty} populated)"
        
        if not has_column_desc and not has_table_desc:
            status_msg += "\n⚠️  No AI descriptions found - basic metadata only"
            status_msg += "\n💡 Tip: You can still proceed or use Option A to enhance"
        
        # Show what columns were found
        status_msg += f"\n\n📋 Columns found: {', '.join(sorted(df.columns)[:10])}"
        if len(df.columns) > 10:
            status_msg += f"... and {len(df.columns) - 10} more"
        
        return status_msg, df.head(20)
        
    except Exception as e:
        return f"❌ Error reading file: {str(e)}\n\nDetails: {type(e).__name__}", None

def download_metadata_ui():
    """Download metadata as Excel file"""
    metadata_df = global_state.get('metadata_enhanced_df')
    if metadata_df is None:
        metadata_df = global_state.get('metadata_df')
    
    db_connector = global_state.get('db_connector')
    
    if metadata_df is None:
        return None, "❌ No metadata to download"
    
    try:
        db_name = db_connector.database if db_connector else "database"
        success, message, filepath = save_metadata_to_excel(metadata_df, db_name, 'Enhanced_Metadata')
        
        if success:
            return filepath, message
        else:
            return None, message
    except Exception as e:
        return None, f"❌ Download failed: {str(e)}"

def ingest_to_opensearch_ui(progress=gr.Progress()):
    """Ingest metadata into OpenSearch (UI function)"""
    metadata_df = global_state.get('metadata_enhanced_df')
    if metadata_df is None:
        metadata_df = global_state.get('metadata_df')
    
    os_client = global_state.get('os_client')
    model_id = global_state.get('model_id')
    
    if metadata_df is None:
        return "❌ No metadata available"
    if os_client is None:
        return "❌ OpenSearch not initialized"
    if model_id is None:
        return "❌ Model not registered"
    
    try:
        # Create pipeline
        text_fields = ['full_column_name', 'inferred_column_description', 
                      'inferred_table_description', 'table_name']
        success, msg = create_embedding_pipeline(
            os_client, model_id, global_state['pipeline_name'], text_fields
        )
        
        if not success:
            return msg
        
        # Create mappings
        mappings = create_opensearch_mappings(
            metadata_df, model_id, global_state['pipeline_name']
        )
        
        # Ingest data
        success, msg = ingest_metadata_to_opensearch(
            os_client, metadata_df, global_state['index_name'], mappings, progress
        )
        
        return msg
    except Exception as e:
        return f"❌ Ingestion failed: {str(e)}"

def generate_sql_ui(query_text):
    """Generate SQL from natural language query"""
    os_client = global_state.get('os_client')
    model_id = global_state.get('model_id')
    index_name = global_state.get('index_name')
    
    if not os_client or not model_id:
        return "❌ OpenSearch not initialized. Please complete Tab 1: Setup & Connect", ""
    
    if not index_name:
        return "❌ Metadata not ingested. Please complete Tab 5: Ingest to OpenSearch", ""
    
    # Check if index exists
    try:
        if not os_client.indices.exists(index=index_name):
            return f"❌ Index '{index_name}' does not exist. Please complete Tab 5: Ingest to OpenSearch", ""
    except Exception as e:
        return f"❌ Error checking index: {str(e)}", ""
    
    if not query_text or query_text.strip() == "":
        return "❌ Please enter a question", ""
    
    try:
        sql_query, error, metadata_context = text_to_sql_pipeline(
            os_client, query_text, index_name, model_id, top_k=10
        )
        
        if error:
            return f"❌ {error}\n\n💡 Tip: Make sure you've completed Tab 5 to ingest metadata into OpenSearch", ""
        
        global_state['last_sql'] = sql_query
        global_state['last_query'] = query_text
        global_state['last_metadata_context'] = metadata_context
        
        return "✅ SQL generated successfully", sql_query
        
    except Exception as e:
        return f"❌ Error: {str(e)}", ""

def execute_sql_ui(sql_query):
    """Execute SQL query"""
    db_connector = global_state.get('db_connector')
    metadata_context = global_state.get('last_metadata_context', '')
    
    if not db_connector:
        return "❌ Database not connected", None, "", ""
    
    if not sql_query or sql_query.strip() == "":
        return "❌ No SQL query to execute", None, "", ""
    
    try:
        df, error = execute_sql_query(db_connector, sql_query)
        
        if error:
            return f"❌ {error}", None, "", metadata_context or "No metadata context available"
        
        global_state['last_dataframe'] = df
        
        # Analyze data
        analysis = analyze_dataframe(df)
        
        # Prepare metadata context display
        context_display = metadata_context if metadata_context else "No metadata context available (SQL may have been manually entered)"
        
        return f"✅ Query executed: {len(df)} rows returned", df.head(50), analysis, context_display
        
    except Exception as e:
        return f"❌ Error: {str(e)}", None, "", metadata_context or "No metadata context available"

def visualize_data_ui():
    """Create visualizations from query results"""
    df = global_state.get('last_dataframe')
    
    if df is None:
        return None, None, None, None, "❌ No data available for visualization"
    
    try:
        fig1, fig2, fig3, fig4, status = create_visualizations(df)
        
        return fig1, fig2, fig3, fig4, status
        
    except Exception as e:
        return None, None, None, None, f"❌ Error: {str(e)}"

def generate_insights_ui():
    """Generate business insights"""
    df = global_state.get('last_dataframe')
    sql_query = global_state.get('last_sql')
    query_text = global_state.get('last_query')
    
    if df is None:
        return "❌ No data available for insights"
    
    try:
        analysis = analyze_dataframe(df)
        insights = generate_business_insights(df, query_text, sql_query, analysis)
        return insights
        
    except Exception as e:
        return f"❌ Error: {str(e)}"

# ============================================================================
# GRADIO UI DEFINITION
# ============================================================================

def create_gradio_interface():
    """Create the main Gradio interface"""
    
    with gr.Blocks(title="Business Intelligence RAG Application", theme=gr.themes.Soft()) as demo:
        gr.Markdown("# 🚀 Business Intelligence RAG Application")
        gr.Markdown("""
        **Complete workflow for Text-to-SQL-to-Visualization-to-Insights using RAG**
        
        Follow the tabs in order for the complete workflow.
        """)
        
        with gr.Tabs() as tabs:
            # ===== TAB 1: Setup =====
            with gr.Tab("1️⃣ Setup & Connect"):
                gr.Markdown("## Database & OpenSearch Setup")
                gr.Markdown("""
                **Step 1**: Connect to PostgreSQL database and initialize OpenSearch.
                
                - Connects to the PostgreSQL database specified in .env file
                - Initializes OpenSearch client and configures cluster
                - Registers and deploys the sentence transformer model for embeddings
                """)
                
                with gr.Row():
                    with gr.Column():
                        connect_db_btn = gr.Button("🔌 Connect to Database", variant="primary")
                        db_status = gr.Textbox(label="Database Status", lines=3)
                    
                    with gr.Column():
                        setup_os_btn = gr.Button("⚙️ Setup OpenSearch", variant="primary")
                        os_status = gr.Textbox(label="OpenSearch Setup Progress", lines=6)
                
                connect_db_btn.click(connect_to_database, outputs=db_status)
                setup_os_btn.click(setup_opensearch, outputs=os_status, show_progress=True)
            
            # ===== TAB 2: Extract Metadata =====
            with gr.Tab("2️⃣ Extract Metadata"):
                gr.Markdown("## Extract Database Metadata")
                gr.Markdown("""
                **Step 2**: Extract metadata (tables, columns, data types) from the database.
                
                - Retrieves all table and column information
                - Excludes system schemas (information_schema, pg_catalog)
                - Shows column names, data types, nullability, etc.
                """)
                
                extract_btn = gr.Button("📊 Extract Metadata", variant="primary")
                extract_status = gr.Textbox(label="Status", lines=2)
                metadata_preview = gr.Dataframe(label="Metadata Preview (first 20 rows)")
                
                extract_btn.click(
                    extract_metadata_ui,
                    outputs=[extract_status, metadata_preview]
                )
            
            # ===== TAB 3: Enhance with LLM =====
            with gr.Tab("3️⃣ Enhance with AI"):
                gr.Markdown("## Enhance Metadata with AI Descriptions")
                gr.Markdown("""
                **Step 3**: Use DeepSeek LLM to generate intelligent descriptions OR upload previously generated metadata.
                
                ### Option A: Generate Fresh AI Descriptions (Takes Time)
                - **Column Descriptions**: Samples data from each column and generates descriptions
                - **Table Descriptions**: Analyzes table structure and sample rows to describe purpose
                - Uses AI to understand data meaning and business context
                - **Note**: This makes API calls and may take 5-15 minutes for large databases
                
                ### Option B: Upload Previously Generated Metadata (Fast)
                - Upload an Excel file from a previous run (from Tab 4)
                - Instantly loads all metadata with descriptions
                - Skips API calls and saves time
                - **Tip**: Use this if you've already run enhancement before!
                """)
                
                gr.Markdown("---")
                gr.Markdown("### Option A: Generate AI Descriptions")
                
                with gr.Row():
                    enhance_cols_btn = gr.Button("🤖 Enhance Column Descriptions", variant="primary")
                    enhance_tables_btn = gr.Button("🏢 Add Table Descriptions", variant="secondary")
                
                gr.Markdown("---")
                gr.Markdown("### Option B: Upload Existing Metadata")
                
                with gr.Row():
                    upload_file = gr.File(
                        label="Upload Metadata Excel File",
                        file_types=[".xlsx", ".xls"],
                        type="filepath"
                    )
                    upload_btn = gr.Button("📤 Upload and Load", variant="primary")
                
                enhance_status = gr.Textbox(label="Status", lines=4)
                enhanced_preview = gr.Dataframe(label="Enhanced Metadata Preview")
                
                enhance_cols_btn.click(
                    enhance_metadata_ui,
                    outputs=[enhance_status, enhanced_preview]
                )
                
                enhance_tables_btn.click(
                    add_table_descriptions_ui,
                    outputs=[enhance_status, enhanced_preview]
                )
                
                upload_btn.click(
                    upload_metadata_ui,
                    inputs=upload_file,
                    outputs=[enhance_status, enhanced_preview]
                )
            
            # ===== TAB 4: Download Metadata =====
            with gr.Tab("4️⃣ Download"):
                gr.Markdown("## Download Enhanced Metadata")
                gr.Markdown("""
                **Step 4**: Download the enhanced metadata as an Excel file.
                
                - Saves all metadata with AI-generated descriptions
                - Format: Excel (.xlsx) file
                - Can be used for documentation or further analysis
                """)
                
                download_btn = gr.Button("💾 Download Metadata as Excel", variant="primary")
                download_status = gr.Textbox(label="Status", lines=2)
                download_file = gr.File(label="Downloaded File")
                
                download_btn.click(
                    download_metadata_ui,
                    outputs=[download_file, download_status]
                )
            
            # ===== TAB 5: Ingest to OpenSearch =====
            with gr.Tab("5️⃣ Ingest to OpenSearch"):
                gr.Markdown("## Ingest Metadata into OpenSearch")
                gr.Markdown("""
                **Step 5**: Ingest enhanced metadata into OpenSearch with embeddings.
                
                - Creates ingest pipeline for automatic embedding generation
                - Creates index with vector fields for semantic search
                - Ingests all metadata documents
                - Enables hybrid search (keyword + semantic)
                
                **Note**: This step may take several minutes for large datasets.
                """)
                
                ingest_btn = gr.Button("🔄 Ingest to OpenSearch", variant="primary")
                ingest_status = gr.Textbox(label="Status", lines=5)
                
                ingest_btn.click(
                    ingest_to_opensearch_ui,
                    outputs=ingest_status
                )
            
            # ===== TAB 6: Text-to-SQL Query =====
            with gr.Tab("6️⃣ Ask Questions"):
                gr.Markdown("## Natural Language to SQL")
                gr.Markdown("""
                **Step 6**: Ask business questions in natural language!
                
                **How it works**:
                1. Enter your question in plain English
                2. System retrieves relevant metadata using RAG (hybrid search)
                3. DeepSeek LLM generates the SQL query
                4. Review the generated SQL before execution
                """)
                
                with gr.Row():
                    query_input = gr.Textbox(
                        label="Enter your business question",
                        placeholder="Example: Segment customers based on their order values and frequency into high, medium, and low value segments.",
                        lines=3
                    )
                
                generate_sql_btn = gr.Button("🎯 Generate SQL", variant="primary")
                sql_status = gr.Textbox(label="Status", lines=2)
                sql_output = gr.Textbox(label="Generated SQL Query", lines=10)
                
                generate_sql_btn.click(
                    generate_sql_ui,
                    inputs=query_input,
                    outputs=[sql_status, sql_output]
                )
            
            # ===== TAB 7: Execute SQL =====
            with gr.Tab("7️⃣ Execute Query"):
                gr.Markdown("## Execute SQL Query")
                gr.Markdown("""
                **Step 7**: Execute the generated SQL query on the database.
                
                - Review the SQL from previous step
                - Click execute to run the query
                - View results and statistical analysis
                """)
                
                sql_to_execute = gr.Textbox(
                    label="SQL Query to Execute",
                    lines=8,
                    placeholder="SQL query will appear here from previous step"
                )
                
                execute_btn = gr.Button("▶️ Execute SQL", variant="primary")
                exec_status = gr.Textbox(label="Execution Status", lines=2)
                results_df = gr.Dataframe(label="Query Results (first 50 rows)")
                analysis_output = gr.Textbox(label="Statistical Analysis", lines=10)
                metadata_context_output = gr.Textbox(label="📚 Metadata Context Used for SQL Generation", lines=15)
                
                # Auto-populate SQL from previous step
                sql_output.change(lambda x: x, inputs=sql_output, outputs=sql_to_execute)
                
                execute_btn.click(
                    execute_sql_ui,
                    inputs=sql_to_execute,
                    outputs=[exec_status, results_df, analysis_output, metadata_context_output]
                )
            
            # ===== TAB 8: Visualize =====
            with gr.Tab("8️⃣ Visualize"):
                gr.Markdown("## Data Visualization")
                gr.Markdown("""
                **Step 8**: Automatically create multiple visualizations from query results.
                
                - System intelligently creates multiple chart types
                - Includes bar charts, scatter plots, histograms, pie charts, correlations, and trends
                - Creates interactive Plotly visualizations
                - Adapts to different data types and structures
                """)
                
                viz_btn = gr.Button("📊 Create Visualizations", variant="primary")
                viz_status = gr.Textbox(label="Status", lines=2)
                
                with gr.Row():
                    with gr.Column():
                        viz_plot1 = gr.Plot(label="Chart 1")
                    with gr.Column():
                        viz_plot2 = gr.Plot(label="Chart 2")
                
                with gr.Row():
                    with gr.Column():
                        viz_plot3 = gr.Plot(label="Chart 3")
                    with gr.Column():
                        viz_plot4 = gr.Plot(label="Chart 4")
                
                viz_btn.click(
                    visualize_data_ui,
                    outputs=[viz_plot1, viz_plot2, viz_plot3, viz_plot4, viz_status]
                )
            
            # ===== TAB 9: Business Insights =====
            with gr.Tab("9️⃣ Business Insights"):
                gr.Markdown("## AI-Generated Business Insights")
                gr.Markdown("""
                **Step 9**: Generate comprehensive business intelligence insights.
                
                - Analyzes query results and data patterns
                - Provides key findings and trends
                - Suggests actionable recommendations
                - Proposes next steps for further analysis
                
                **The AI will provide**:
                - 🔍 Key Findings
                - 📈 Trends
                - 💡 Recommendations
                - 🎯 Next Steps
                """)
                
                insights_btn = gr.Button("🧠 Generate Business Insights", variant="primary")
                insights_output = gr.Textbox(label="Business Intelligence Report", lines=20, show_copy_button=True)
                
                insights_btn.click(
                    generate_insights_ui,
                    outputs=insights_output
                )
            
            # ===== TAB 10: Help =====
            with gr.Tab("ℹ️ Help & Guide"):
                gr.Markdown("""
                ## 📖 Complete Workflow Guide
                
                ### Overview
                This application implements a complete RAG (Retrieval-Augmented Generation) pipeline for business intelligence:
                - **Extract** database metadata
                - **Enhance** with AI descriptions
                - **Ingest** into vector database
                - **Query** in natural language
                - **Visualize** and gain insights
                
                ### Step-by-Step Workflow
                
                #### Tab 1: Setup & Connect
                1. Click "Connect to Database" - establishes PostgreSQL connection
                2. Click "Setup OpenSearch" - initializes vector search engine
                3. Wait for both to show success ✅
                
                #### Tab 2: Extract Metadata
                1. Click "Extract Metadata"
                2. Review the metadata preview (tables, columns, data types)
                3. Proceed to next tab
                
                #### Tab 3: Enhance with AI
                1. Click "Enhance Column Descriptions" (this takes time - samples data and calls LLM)
                2. Click "Add Table Descriptions" (generates table-level descriptions)
                3. Review the enhanced metadata with AI-generated descriptions
                
                #### Tab 4: Download
                1. Click "Download Metadata as Excel"
                2. Save the file for documentation/backup
                
                #### Tab 5: Ingest to OpenSearch
                1. Click "Ingest to OpenSearch"
                2. Wait for ingestion to complete (creates embeddings)
                3. This enables semantic search capabilities
                
                #### Tab 6: Ask Questions
                1. Type your business question in natural language
                   - Example: "Show me top 10 customers by total order value"
                   - Example: "What products have the highest profit margins?"
                2. Click "Generate SQL"
                3. Review the generated SQL query
                
                #### Tab 7: Execute Query
                1. SQL automatically populated from previous step
                2. Review the SQL query
                3. Click "Execute SQL"
                4. View results and statistical analysis
                
                #### Tab 8: Visualize
                1. Click "Create Visualization"
                2. System automatically creates appropriate chart
                3. View interactive visualization
                
                #### Tab 9: Business Insights
                1. Click "Generate Business Insights"
                2. AI analyzes the data and provides:
                   - Key findings
                   - Trends and patterns
                   - Business recommendations
                   - Suggested next steps
                
                ### Tips for Success
                
                **For Best Results**:
                - Be specific in your questions
                - Use business terminology
                - Ask one question at a time
                - Review generated SQL before executing
                
                **Example Questions**:
                - "What are the top 10 products by revenue?"
                - "Show customer segmentation by order frequency"
                - "Which product categories have declining sales?"
                - "Compare sales performance across regions"
                
                **Troubleshooting**:
                - If SQL generation fails, try rephrasing your question
                - Make sure all setup steps (Tabs 1-5) are complete
                - Check that .env file has correct database credentials
                - For API errors, verify API keys in .env file
                
                ### Technical Details
                
                **Components**:
                - PostgreSQL: Source database
                - OpenSearch: Vector database for RAG
                - DeepSeek: LLM for SQL generation and insights
                - Gradio: User interface
                
                **RAG Pipeline**:
                1. User query → Hybrid search (keyword + semantic)
                2. Retrieved metadata → Context for LLM
                3. LLM generates SQL using metadata context
                4. SQL executed on database
                5. Results analyzed and visualized
                6. AI generates business insights
                
                ### Configuration
                
                Edit `.env` file for:
                - Database credentials
                - API keys
                - OpenSearch settings
                
                See README.md for detailed setup instructions.
                """)
        
        gr.Markdown("---")
        gr.Markdown("*Powered by PostgreSQL, OpenSearch, DeepSeek, and Gradio*")
    
    return demo

# ============================================================================
# MAIN EXECUTION
# ============================================================================

if __name__ == "__main__":
    print("="*80)
    print("🚀 Starting Business Intelligence RAG Application")
    print("="*80)
    print(f"📂 Working Directory: {os.getcwd()}")
    print(f"🔑 API Keys Configured: {'✅' if DEEPSEEK_API_KEY else '❌'}")
    print("="*80)
    
    # Create and launch interface
    demo = create_gradio_interface()
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        show_error=True
    )
