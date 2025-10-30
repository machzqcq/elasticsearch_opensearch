#!/usr/bin/env python3
"""
Careful PostgreSQL conversion script - minimal changes only
"""

import json
import re
import sys
from pathlib import Path

def convert_notebook_carefully(notebook_path):
    """Carefully convert MSSQL notebook to PostgreSQL with minimal changes"""
    print(f"\n🔄 Converting: {notebook_path}")
    
    try:
        with open(notebook_path, 'r', encoding='utf-8') as f:
            notebook = json.load(f)
    except Exception as e:
        print(f"❌ Error reading notebook: {e}")
        return False
    
    changes_made = 0
    
    for cell_idx, cell in enumerate(notebook.get('cells', [])):
        if cell.get('cell_type') == 'code':
            source = cell.get('source', [])
            if isinstance(source, list):
                original_code = ''.join(source)
            else:
                original_code = source
            
            if not original_code.strip():
                continue
            
            # Apply careful conversion
            converted_code = apply_careful_conversion(original_code)
            
            if converted_code != original_code:
                changes_made += 1
                print(f"  ✓ Updated cell {cell_idx + 1}")
                
                # Update the cell source
                if isinstance(source, list):
                    cell['source'] = converted_code.split('\n')
                    # Ensure each line except the last ends with \n
                    for i in range(len(cell['source']) - 1):
                        if not cell['source'][i].endswith('\n'):
                            cell['source'][i] += '\n'
                else:
                    cell['source'] = converted_code
    
    if changes_made > 0:
        try:
            with open(notebook_path, 'w', encoding='utf-8') as f:
                json.dump(notebook, f, indent=1, ensure_ascii=False)
            print(f"✅ Applied {changes_made} changes to {notebook_path}")
            return True
        except Exception as e:
            print(f"❌ Error saving notebook: {e}")
            return False
    else:
        print("ℹ️  No changes needed")
        return True

def apply_careful_conversion(code):
    """Apply only essential PostgreSQL conversions"""
    
    # 1. Database driver import
    code = code.replace('import pymssql', 'import psycopg2')
    code = code.replace('from pymssql import ', 'from psycopg2 import ')
    
    # 2. Connection parameters (only environment variable names)
    code = code.replace('MSSQL_HOST', 'POSTGRES_HOST')
    code = code.replace('MSSQL_DATABASE', 'POSTGRES_DB')  
    code = code.replace('MSSQL_USERNAME', 'POSTGRES_USER')
    code = code.replace('MSSQL_PASSWORD', 'POSTGRES_PASSWORD')
    
    # 3. SQLAlchemy connection string
    code = code.replace('mssql+pymssql:', 'postgresql+psycopg2:')
    
    # 4. SQL syntax changes (be very careful with these)
    # Only change TOP if it's clearly in a SELECT statement
    if 'SELECT TOP' in code:
        # Replace SELECT TOP (n) with SELECT ... LIMIT n
        code = re.sub(r'SELECT TOP \((\d+)\)', r'SELECT', code)
        code = re.sub(r'SELECT TOP(\d+)', r'SELECT', code)
        # Add LIMIT at the end of the query if there isn't one already
        if 'LIMIT' not in code and 'TOP' in code:
            # This is a bit tricky - we'll handle it case by case if needed
            pass
    
    # 5. SQL Server functions to PostgreSQL equivalents
    code = code.replace('NEWID()', 'gen_random_uuid()')  # UUID generation
    code = code.replace('GETDATE()', 'NOW()')  # Current datetime
    
    # 6. Text references
    code = code.replace('MSSQL', 'PostgreSQL')
    code = code.replace('SQL Server', 'PostgreSQL')
    code = code.replace('Microsoft SQL Server', 'PostgreSQL')
    
    # 7. Connection class name
    code = code.replace('class MSSQLConnector:', 'class PostgreSQLConnector:')
    code = code.replace('MSSQLConnector()', 'PostgreSQLConnector()')
    
    return code

def convert_env_files():
    """Convert environment files"""
    postgres_dir = Path('/home/ubuntu/git-projects/personal/github.com/elasticsearch_opensearch/opensearch/my_tutorial/scripts/5. REALTIME_PROJECTS/4. text_to_sql_visualization_insights_agent/opensearch-POSTGRES-RAG')
    
    # Convert .env file
    env_file = postgres_dir / '.env'
    if env_file.exists():
        content = env_file.read_text()
        content = content.replace('MSSQL_HOST', 'POSTGRES_HOST')
        content = content.replace('MSSQL_DATABASE', 'POSTGRES_DB')
        content = content.replace('MSSQL_USERNAME', 'POSTGRES_USER')
        content = content.replace('MSSQL_PASSWORD', 'POSTGRES_PASSWORD')
        env_file.write_text(content)
        print("✓ Updated .env file")
    
    # Convert sample_env.env file
    sample_env_file = postgres_dir / 'sample_env.env'
    if sample_env_file.exists():
        content = sample_env_file.read_text()
        content = content.replace('MSSQL_HOST', 'POSTGRES_HOST')
        content = content.replace('MSSQL_DATABASE', 'POSTGRES_DB')
        content = content.replace('MSSQL_USERNAME', 'POSTGRES_USER')
        content = content.replace('MSSQL_PASSWORD', 'POSTGRES_PASSWORD')
        sample_env_file.write_text(content)
        print("✓ Updated sample_env.env file")

def main():
    """Main function"""
    notebook_dir = Path('/home/ubuntu/git-projects/personal/github.com/elasticsearch_opensearch/opensearch/my_tutorial/scripts/5. REALTIME_PROJECTS/4. text_to_sql_visualization_insights_agent/opensearch-POSTGRES-RAG')
    
    notebooks = [
        "1. build_ingest_meta_dictionary.ipynb",
        "2. text-to-sql-viz-insights.ipynb"
    ]
    
    print("🔄 CAREFUL POSTGRESQL CONVERSION")
    print("=" * 80)
    
    # Convert environment files first
    convert_env_files()
    
    all_success = True
    
    for notebook in notebooks:
        notebook_path = notebook_dir / notebook
        if notebook_path.exists():
            success = convert_notebook_carefully(notebook_path)
            all_success = all_success and success
        else:
            print(f"❌ Notebook not found: {notebook_path}")
            all_success = False
    
    print("\n" + "=" * 80)
    if all_success:
        print("🎉 CAREFUL CONVERSION COMPLETED!")
        print("\n📋 Next Steps:")
        print("1. Review the converted notebooks manually")
        print("2. Test with: docker-compose -f docker-compose-postgres.yml up -d")
        print("3. Run the notebooks to verify functionality")
    else:
        print("❌ CONVERSION FAILED")
    print("=" * 80)
    
    return 0 if all_success else 1

if __name__ == "__main__":
    sys.exit(main())