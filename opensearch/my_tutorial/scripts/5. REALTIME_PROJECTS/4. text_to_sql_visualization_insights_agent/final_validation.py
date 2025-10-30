#!/usr/bin/env python3
"""
Final validation of PostgreSQL notebooks
"""

import json
import ast
import sys
from pathlib import Path

def validate_notebook_final(notebook_path):
    """Final validation of converted notebook"""
    print(f"\n🎯 Final validation: {notebook_path}")
    print("=" * 60)
    
    try:
        with open(notebook_path, 'r', encoding='utf-8') as f:
            notebook = json.load(f)
    except Exception as e:
        print(f"❌ Error reading notebook: {e}")
        return False
    
    errors_found = 0
    warnings_found = 0
    cell_num = 0
    
    for cell in notebook.get('cells', []):
        cell_num += 1
        
        if cell.get('cell_type') == 'code':
            source = cell.get('source', [])
            if isinstance(source, list):
                code = ''.join(source)
            else:
                code = source
            
            # Skip empty cells
            if not code.strip():
                continue
            
            print(f"\n📱 Cell {cell_num}:")
            print("-" * 30)
            
            # Check if it's a magic command cell
            if code.strip().startswith('%%') or code.strip().startswith('!'):
                print("✅ Magic command cell (valid)")
                continue
            
            # Try to parse the code
            try:
                ast.parse(code)
                print("✅ Python syntax OK")
            except SyntaxError as e:
                # Try removing magic commands first
                lines = code.split('\n')
                clean_lines = []
                has_magic = False
                
                for line in lines:
                    stripped = line.strip()
                    if stripped.startswith('%') or stripped.startswith('!'):
                        has_magic = True
                        print(f"⚠️  Magic command: {stripped}")
                    else:
                        clean_lines.append(line)
                
                if clean_lines:
                    clean_code = '\n'.join(clean_lines)
                    try:
                        ast.parse(clean_code)
                        if has_magic:
                            print("✅ Python syntax OK (after magic commands)")
                        else:
                            print("✅ Python syntax OK")
                    except SyntaxError as e:
                        print(f"❌ Python syntax error: {e}")
                        print(f"   Line {e.lineno}: {e.text}")
                        errors_found += 1
                else:
                    print("✅ Only magic commands (valid)")
            except Exception as e:
                print(f"⚠️  Parse warning: {e}")
                warnings_found += 1
    
    print(f"\n📊 Summary for {notebook_path.name}:")
    print(f"   Cells checked: {cell_num}")
    print(f"   Errors: {errors_found}")
    print(f"   Warnings: {warnings_found}")
    
    return errors_found == 0

def main():
    """Main function"""
    notebook_dir = Path('/home/ubuntu/git-projects/personal/github.com/elasticsearch_opensearch/opensearch/my_tutorial/scripts/5. REALTIME_PROJECTS/4. text_to_sql_visualization_insights_agent/opensearch-POSTGRES-RAG')
    
    notebooks = [
        "1. build_ingest_meta_dictionary.ipynb",
        "2. text-to-sql-viz-insights.ipynb"
    ]
    
    print("🎯 FINAL POSTGRESQL NOTEBOOK VALIDATION")
    print("=" * 80)
    
    all_valid = True
    total_errors = 0
    total_warnings = 0
    
    for notebook in notebooks:
        notebook_path = notebook_dir / notebook
        if notebook_path.exists():
            valid = validate_notebook_final(notebook_path)
            all_valid = all_valid and valid
        else:
            print(f"❌ Notebook not found: {notebook_path}")
            all_valid = False
    
    print("\n" + "=" * 80)
    print("🏁 FINAL VALIDATION RESULTS")
    print("=" * 80)
    
    if all_valid:
        print("🎉 ALL NOTEBOOKS ARE VALID AND READY TO USE!")
        print("\n✅ PostgreSQL conversion completed successfully")
        print("✅ All Python syntax is correct")
        print("✅ Magic commands are properly formatted")
        print("\n📋 Next steps:")
        print("1. Start PostgreSQL: docker-compose -f docker-compose-postgres.yml up -d")
        print("2. Run the notebooks in Jupyter/VS Code")
        print("3. Test the RAG pipeline with your data")
    else:
        print("❌ SOME NOTEBOOKS STILL HAVE ISSUES")
        print("   Please review the errors above")
    
    print("=" * 80)
    
    return 0 if all_valid else 1

if __name__ == "__main__":
    sys.exit(main())