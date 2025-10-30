#!/usr/bin/env python3
"""
Validate syntax of Python code cells in Jupyter notebooks
"""

import json
import ast
import sys
import os
from pathlib import Path

def extract_and_validate_python_cells(notebook_path):
    """Extract Python code cells and validate syntax"""
    print(f"\n🔍 Validating: {notebook_path}")
    print("=" * 60)
    
    try:
        with open(notebook_path, 'r', encoding='utf-8') as f:
            notebook = json.load(f)
    except Exception as e:
        print(f"❌ Error reading notebook: {e}")
        return False
    
    errors_found = False
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
            
            try:
                # Try to parse the code
                ast.parse(code)
                print("✅ Syntax OK")
            except SyntaxError as e:
                print(f"❌ Syntax Error: {e}")
                print(f"   Line {e.lineno}: {e.text}")
                print(f"   Error: {e.msg}")
                errors_found = True
            except Exception as e:
                print(f"⚠️  Parse Error: {e}")
                # This might be due to notebook-specific magic commands
                # Try to check if it's just magic commands
                lines = code.split('\n')
                clean_lines = []
                for line in lines:
                    stripped = line.strip()
                    if not (stripped.startswith('%') or stripped.startswith('!')):
                        clean_lines.append(line)
                
                if clean_lines:
                    clean_code = '\n'.join(clean_lines)
                    try:
                        ast.parse(clean_code)
                        print("✅ Syntax OK (after removing magic commands)")
                    except SyntaxError as e:
                        print(f"❌ Syntax Error: {e}")
                        errors_found = True
                else:
                    print("✅ Only magic commands")
    
    if errors_found:
        print(f"\n❌ Syntax errors found in {notebook_path}")
        return False
    else:
        print(f"\n✅ All syntax checks passed for {notebook_path}")
        return True

def main():
    notebook_dir = Path('/home/ubuntu/git-projects/personal/github.com/elasticsearch_opensearch/opensearch/my_tutorial/scripts/5. REALTIME_PROJECTS/4. text_to_sql_visualization_insights_agent/opensearch-POSTGRES-RAG')
    
    notebooks = [
        "1. build_ingest_meta_dictionary.ipynb",
        "2. text-to-sql-viz-insights.ipynb"
    ]
    
    all_valid = True
    
    for notebook in notebooks:
        notebook_path = notebook_dir / notebook
        if notebook_path.exists():
            valid = extract_and_validate_python_cells(notebook_path)
            all_valid = all_valid and valid
        else:
            print(f"❌ Notebook not found: {notebook_path}")
            all_valid = False
    
    print("\n" + "=" * 80)
    if all_valid:
        print("🎉 ALL NOTEBOOKS HAVE VALID SYNTAX!")
    else:
        print("❌ SOME NOTEBOOKS HAVE SYNTAX ERRORS")
    print("=" * 80)
    
    return 0 if all_valid else 1

if __name__ == "__main__":
    sys.exit(main())