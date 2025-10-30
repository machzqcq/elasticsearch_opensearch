#!/usr/bin/env python3
"""
Script to convert MSSQL-based notebooks and documentation to PostgreSQL equivalents.
"""

import json
import re
import shutil
from pathlib import Path

def convert_mssql_to_postgres(content):
    """Convert MSSQL-specific code and references to PostgreSQL."""
    
    # Environment variable replacements
    content = content.replace("MSSQL_SERVER", "POSTGRES_HOST")
    content = content.replace("MSSQL_DATABASE", "POSTGRES_DB")
    content = content.replace("MSSQL_USERNAME", "POSTGRES_USER")
    content = content.replace("MSSQL_PASSWORD", "POSTGRES_PASSWORD")
    content = content.replace("MSSQL_PORT", "POSTGRES_PORT")
    content = content.replace("MSSQL_USE_WINDOWS_AUTH", "# Not applicable for PostgreSQL")
    
    # Import replacements
    content = content.replace("import pymssql", "import psycopg2")
    content = content.replace("pymssql", "psycopg2")
    
    # Class name replacements
    content = content.replace("class MSSQLConnector:", "class PostgreSQLConnector:")
    content = content.replace("MSSQLConnector", "PostgreSQLConnector")
    
    # Connection string replacements
    content = content.replace("mssql+pymssql://", "postgresql+psycopg2://")
    
    # Documentation and comment replacements
    content = content.replace("MSSQL", "PostgreSQL")
    content = content.replace("MS SQL Server", "PostgreSQL")
    content = content.replace("SQL Server", "PostgreSQL")
    content = content.replace("Microsoft SQL Server", "PostgreSQL")
    
    # SQL syntax replacements for queries
    # TOP N -> LIMIT N
    content = re.sub(r'SELECT TOP (\d+)', r'SELECT', content)
    content = re.sub(r'ORDER BY NEWID\(\)', 'ORDER BY RANDOM()', content)
    
    # Bracket notation to quoted notation for table/column references
    content = re.sub(r'\[(\w+)\]\.?\[?(\w+)?\]?', r'"\1".\2' if r'\2' else r'"\1"', content)
    
    # ISNULL -> COALESCE
    content = content.replace("ISNULL(", "COALESCE(")
    
    # sys tables -> information_schema (PostgreSQL standard)
    content = content.replace("sys.tables", "information_schema.tables")
    content = content.replace("sys.columns", "information_schema.columns")
    content = content.replace("sys.extended_properties", "-- Extended properties not available in PostgreSQL")
    
    # SCHEMA_ID function not in PostgreSQL
    content = content.replace("SCHEMA_ID(", "-- SCHEMA_ID not available in PostgreSQL -- ")
    
    # Specific query modifications for metadata extraction
    content = update_metadata_queries(content)
    
    # Update error messages and troubleshooting tips
    content = content.replace("Check if SQL Server is running", "Check if PostgreSQL is running")
    content = content.replace("Ensure SQL Server is configured to allow TCP/IP", "Ensure PostgreSQL is configured to allow connections")
    content = content.replace("default: 1433", "default: 5432")
    content = content.replace("port number (default: 1433)", "port number (default: 5432)")
    
    # Success messages
    content = content.replace("Successfully connected to MSSQL database!", "Successfully connected to PostgreSQL database!")
    
    # Remove Windows Authentication related code
    content = remove_windows_auth_code(content)
    
    return content

def update_metadata_queries(content):
    """Update SQL queries to be PostgreSQL compatible."""
    
    # Original MSSQL metadata query pattern
    mssql_metadata_query = r'''query = """
        SELECT 
            t\.TABLE_SCHEMA,
            t\.TABLE_NAME,
            c\.COLUMN_NAME,
            c\.DATA_TYPE,
            c\.CHARACTER_MAXIMUM_LENGTH,
            c\.NUMERIC_PRECISION,
            c\.NUMERIC_SCALE,
            c\.IS_NULLABLE,
            c\.COLUMN_DEFAULT,
            c\.ORDINAL_POSITION,
            -- Try to get column descriptions from extended properties
            ISNULL\(ep\.value, ''\) as COLUMN_DESCRIPTION,
            -- Additional table information
            t\.TABLE_TYPE,
            -- Create a readable data type description
            CASE 
                WHEN c\.DATA_TYPE IN \('varchar', 'char', 'nvarchar', 'nchar'\) 
                    THEN c\.DATA_TYPE \+ '\(' \+ CAST\(c\.CHARACTER_MAXIMUM_LENGTH as varchar\(10\)\) \+ '\)'
                WHEN c\.DATA_TYPE IN \('decimal', 'numeric'\) 
                    THEN c\.DATA_TYPE \+ '\(' \+ CAST\(c\.NUMERIC_PRECISION as varchar\(10\)\) \+ ',' \+ CAST\(c\.NUMERIC_SCALE as varchar\(10\)\) \+ '\)'
                ELSE c\.DATA_TYPE
            END as FULL_DATA_TYPE
        FROM INFORMATION_SCHEMA\.TABLES t
        INNER JOIN INFORMATION_SCHEMA\.COLUMNS c 
            ON t\.TABLE_SCHEMA = c\.TABLE_SCHEMA 
            AND t\.TABLE_NAME = c\.TABLE_NAME
        LEFT JOIN sys\.tables st 
            ON st\.name = t\.TABLE_NAME 
            AND st\.schema_id = SCHEMA_ID\(t\.TABLE_SCHEMA\)
        LEFT JOIN sys\.columns sc 
            ON sc\.object_id = st\.object_id 
            AND sc\.name = c\.COLUMN_NAME
        LEFT JOIN sys\.extended_properties ep 
            ON ep\.major_id = sc\.object_id 
            AND ep\.minor_id = sc\.column_id 
            AND ep\.name = 'MS_Description'
        WHERE t\.TABLE_TYPE = 'BASE TABLE'
        ORDER BY t\.TABLE_SCHEMA, t\.TABLE_NAME, c\.ORDINAL_POSITION
        """'''
    
    postgres_metadata_query = '''query = """
        SELECT 
            t.TABLE_SCHEMA,
            t.TABLE_NAME,
            c.COLUMN_NAME,
            c.DATA_TYPE,
            c.CHARACTER_MAXIMUM_LENGTH,
            c.NUMERIC_PRECISION,
            c.NUMERIC_SCALE,
            c.IS_NULLABLE,
            c.COLUMN_DEFAULT,
            c.ORDINAL_POSITION,
            -- PostgreSQL doesn't have extended properties like MSSQL
            '' as COLUMN_DESCRIPTION,
            -- Additional table information
            t.TABLE_TYPE,
            -- Create a readable data type description
            CASE 
                WHEN c.DATA_TYPE IN ('character varying', 'character', 'varchar', 'char') 
                    THEN c.DATA_TYPE || '(' || c.CHARACTER_MAXIMUM_LENGTH::varchar || ')'
                WHEN c.DATA_TYPE IN ('decimal', 'numeric') 
                    THEN c.DATA_TYPE || '(' || c.NUMERIC_PRECISION::varchar || ',' || c.NUMERIC_SCALE::varchar || ')'
                ELSE c.DATA_TYPE
            END as FULL_DATA_TYPE
        FROM INFORMATION_SCHEMA.TABLES t
        INNER JOIN INFORMATION_SCHEMA.COLUMNS c 
            ON t.TABLE_SCHEMA = c.TABLE_SCHEMA 
            AND t.TABLE_NAME = c.TABLE_NAME
        WHERE t.TABLE_TYPE = 'BASE TABLE'
        ORDER BY t.TABLE_SCHEMA, t.TABLE_NAME, c.ORDINAL_POSITION
        """'''
    
    content = re.sub(mssql_metadata_query, postgres_metadata_query, content, flags=re.DOTALL)
    
    # Update sample query patterns - TOP N -> LIMIT N
    # Pattern for: SELECT TOP {sample_size} * FROM ...
    content = re.sub(
        r'SELECT TOP \{sample_size\} \*\s+FROM \[(\w+)\]\.\[(\w+)\]\s+ORDER BY NEWID\(\)',
        r'SELECT * FROM "\1"."\2" ORDER BY RANDOM() LIMIT {sample_size}',
        content
    )
    
    # Pattern for: SELECT TOP {sample_size} [{column}] FROM ...
    content = re.sub(
        r'SELECT TOP \{sample_size\} \[(\w+)\]\s+FROM \[(\w+)\]\.\[(\w+)\]\s+WHERE \[\1\] IS NOT NULL\s+ORDER BY NEWID\(\)',
        r'SELECT "\1" FROM "\2"."\3" WHERE "\1" IS NOT NULL ORDER BY RANDOM() LIMIT {sample_size}',
        content
    )
    
    return content

def remove_windows_auth_code(content):
    """Remove or comment out Windows Authentication related code."""
    
    # Pattern to match the Windows Auth block in the connection string creation
    windows_auth_pattern = r'''if self\.use_windows_auth:
            # Windows Authentication - pymssql doesn't support this directly
            # You would need to use SSPI/Kerberos which is complex
            raise ValueError\(
                "Windows Authentication is not supported with pymssql\. "
                "Please use SQL Server authentication with username and password\."
            \)
        else:'''
    
    postgres_auth = '''# PostgreSQL uses standard username/password authentication'''
    
    content = re.sub(windows_auth_pattern, postgres_auth, content, flags=re.DOTALL)
    
    return content

def convert_notebook(source_path, target_path):
    """Convert a Jupyter notebook from MSSQL to PostgreSQL."""
    print(f"Converting notebook: {source_path.name}")
    
    with open(source_path, 'r', encoding='utf-8') as f:
        notebook = json.load(f)
    
    # Convert each cell's source
    if 'cells' in notebook:
        for cell in notebook['cells']:
            if 'source' in cell:
                if isinstance(cell['source'], list):
                    cell['source'] = [convert_mssql_to_postgres(line) for line in cell['source']]
                else:
                    cell['source'] = convert_mssql_to_postgres(cell['source'])
    
    # Write converted notebook
    with open(target_path, 'w', encoding='utf-8') as f:
        json.dump(notebook, f, indent=1, ensure_ascii=False)
    
    print(f"✓ Created: {target_path.name}")

def convert_markdown(source_path, target_path):
    """Convert a markdown file from MSSQL to PostgreSQL."""
    print(f"Converting markdown: {source_path.name}")
    
    with open(source_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    content = convert_mssql_to_postgres(content)
    
    # Additional markdown-specific replacements
    content = content.replace("AdventureWorks2019", "AdventureWorks")
    
    with open(target_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✓ Created: {target_path.name}")

def main():
    """Main conversion function."""
    base_dir = Path(__file__).parent
    source_dir = base_dir / "opensearch-MSSQL-RAG"
    target_dir = base_dir / "opensearch-POSTGRES-RAG"
    
    print("="*80)
    print("Converting MSSQL-based project to PostgreSQL")
    print("="*80)
    
    # Create target directories
    target_dir.mkdir(exist_ok=True)
    (target_dir / "docs").mkdir(exist_ok=True)
    
    # Convert notebooks
    print("\n📓 Converting Notebooks...")
    print("-"*80)
    notebooks = [
        "1. build_ingest_meta_dictionary.ipynb",
        "2. text-to-sql-viz-insights.ipynb"
    ]
    
    for notebook in notebooks:
        source_file = source_dir / notebook
        target_file = target_dir / notebook
        if source_file.exists():
            convert_notebook(source_file, target_file)
    
    # Convert markdown documentation
    print("\n📄 Converting Documentation...")
    print("-"*80)
    docs = [
        "build_ingest_meta_dictionary.md",
        "text-to-sql-viz-insights.md"
    ]
    
    for doc in docs:
        source_file = source_dir / "docs" / doc
        target_file = target_dir / "docs" / doc
        if source_file.exists():
            convert_markdown(source_file, target_file)
    
    print("\n" + "="*80)
    print("✅ Conversion Complete!")
    print("="*80)
    print(f"\n📁 Output directory: {target_dir}")
    print("\n📋 Next steps:")
    print("  1. Review the converted files for any PostgreSQL-specific adjustments")
    print("  2. Start PostgreSQL using: docker-compose -f docker-compose-postgres.yml up -d")
    print("  3. Run the converted notebooks")
    print("\n⚠️  Note: Some MSSQL-specific features may need manual adjustment:")
    print("  - Extended properties are not available in PostgreSQL")
    print("  - Some system tables/views differ between databases")
    print("  - Review all SQL queries for PostgreSQL compatibility")

if __name__ == "__main__":
    main()
