#!/usr/bin/env python3
"""
Post-conversion fixes for PostgreSQL notebooks.
"""

import json
import re
from pathlib import Path

def fix_postgres_notebook(notebook_path):
    """Apply specific fixes to the converted PostgreSQL notebooks."""
    print(f"Fixing: {notebook_path.name}")
    
    with open(notebook_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Fix connection string - should be postgresql not mssql
    content = content.replace('mssql+psycopg2://', 'postgresql+psycopg2://')
    
    # Fix Windows Auth check (should be removed entirely for PostgreSQL)
    content = re.sub(
        r"self\.use_windows_auth = os\.getenv\('# Not applicable for PostgreSQL'.*?\)",
        "# PostgreSQL doesn't use Windows Authentication",
        content
    )
    
    # Fix the connect method result check
    content = content.replace('if result"0". == 1:', 'if result[0] == 1:')
    
    # Fix metadata extraction query for PostgreSQL
    old_metadata_query = r'''query = """
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
            COALESCE\(ep\.value, ''\) as COLUMN_DESCRIPTION,
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
            AND t\.TABLE_NAME = c\.TABLE_NAME.*?
        WHERE t\.TABLE_TYPE = 'BASE TABLE'
        ORDER BY t\.TABLE_SCHEMA, t\.TABLE_NAME, c\.ORDINAL_POSITION
        """'''
    
    new_metadata_query = r'''query = """
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
    
    content = re.sub(old_metadata_query, new_metadata_query, content, flags=re.DOTALL)
    
    # Fix sample query for columns
    content = re.sub(
        r'SELECT \\"(\w+)\\" FROM \\"(\w+)\\"\\.\\"(\w+)\\" WHERE \\"(\w+)\\" IS NOT NULL ORDER BY RANDOM\(\) LIMIT \{sample_size\}',
        r'SELECT "\1" FROM "\2"."\3" WHERE "\1" IS NOT NULL ORDER BY RANDOM() LIMIT {sample_size}',
        content
    )
    
    # Fix sample query for tables
    content = re.sub(
        r'SELECT \* FROM \\"(\w+)\\"\\.\\"(\w+)\\" ORDER BY RANDOM\(\) LIMIT \{sample_size\}',
        r'SELECT * FROM "\1"."\2" ORDER BY RANDOM() LIMIT {sample_size}',
        content
    )
    
    # Fix double backslash escaping issues in queries
    content = content.replace('\\\\"', '"')
    content = content.replace('\\\\n', '\\n')
    
    # Fix port default value (was getting POSTGRES_PORT as default)
    content = re.sub(
        r"self\.port = int\(os\.getenv\('POSTGRES_PORT', os\.getenv\('POSTGRES_PORT'\)\)\)",
        "self.port = int(os.getenv('POSTGRES_PORT', '5432'))",
        content
    )
    
    # Remove Windows auth block entirely
    if_windows_auth_pattern = r'''if self\.use_windows_auth:
            # Windows Authentication - psycopg2 doesn't support this directly
            # You would need to use SSPI/Kerberos which is complex
            raise ValueError\(
                "Windows Authentication is not supported with psycopg2\. "
                "Please use PostgreSQL authentication with username and password\."
            \)
        else:
            # PostgreSQL Authentication'''
    
    content = re.sub(if_windows_auth_pattern, '# PostgreSQL uses standard username/password authentication', content, flags=re.DOTALL)
    
    # Fix PostgreSQL connection string creation
    old_conn_string = r'''# psycopg2 connection string format
            self\.connection_string = \(
                f"mssql\+psycopg2://\{encoded_username\}:\{encoded_password\}@"
                f"\{self\.server\}:\{self\.port\}/\{self\.database\}"
            \)'''
    
    new_conn_string = '''# psycopg2 connection string format
            self.connection_string = (
                f"postgresql+psycopg2://{encoded_username}:{encoded_password}@"
                f"{self.server}:{self.port}/{self.database}"
            )'''
    
    content = re.sub(old_conn_string, new_conn_string, content)
    
    # Fix any remaining MSSQL/pymssql references
    content = content.replace('PostgreSQL using SQLAlchemy with the psycopg2', 'PostgreSQL using SQLAlchemy with the psycopg2')
    content = content.replace('PostgrePostgreSQL', 'PostgreSQL')
    
    with open(notebook_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✓ Fixed: {notebook_path.name}")

def main():
    base_dir = Path(__file__).parent / "opensearch-POSTGRES-RAG"
    
    print("="*80)
    print("Applying post-conversion fixes for PostgreSQL")
    print("="*80)
    
    notebooks = [
        "1. build_ingest_meta_dictionary.ipynb",
        "2. text-to-sql-viz-insights.ipynb"
    ]
    
    for notebook_name in notebooks:
        notebook_path = base_dir / notebook_name
        if notebook_path.exists():
            fix_postgres_notebook(notebook_path)
    
    print("\n" + "="*80)
    print("✅ Post-conversion fixes applied successfully!")
    print("="*80)

if __name__ == "__main__":
    main()
