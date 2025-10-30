#!/usr/bin/env python3
"""
Comprehensive fix for PostgreSQL notebook syntax errors
"""

import json
import re
import sys
from pathlib import Path

def fix_notebook_syntax(notebook_path):
    """Fix all syntax errors in a notebook"""
    print(f"\n🔧 Fixing: {notebook_path}")
    print("=" * 60)
    
    try:
        with open(notebook_path, 'r', encoding='utf-8') as f:
            notebook = json.load(f)
    except Exception as e:
        print(f"❌ Error reading notebook: {e}")
        return False
    
    fixes_applied = 0
    
    for cell_idx, cell in enumerate(notebook.get('cells', [])):
        if cell.get('cell_type') == 'code':
            source = cell.get('source', [])
            if isinstance(source, list):
                original_code = ''.join(source)
            else:
                original_code = source
            
            if not original_code.strip():
                continue
            
            # Apply comprehensive fixes
            fixed_code = apply_comprehensive_fixes(original_code)
            
            if fixed_code != original_code:
                fixes_applied += 1
                print(f"✓ Fixed cell {cell_idx + 1}")
                
                # Update the cell source
                if isinstance(source, list):
                    cell['source'] = fixed_code.split('\n')
                    # Ensure each line except the last ends with \n
                    for i in range(len(cell['source']) - 1):
                        if not cell['source'][i].endswith('\n'):
                            cell['source'][i] += '\n'
                else:
                    cell['source'] = fixed_code
    
    if fixes_applied > 0:
        try:
            with open(notebook_path, 'w', encoding='utf-8') as f:
                json.dump(notebook, f, indent=1, ensure_ascii=False)
            print(f"✅ Applied {fixes_applied} fixes to {notebook_path}")
            return True
        except Exception as e:
            print(f"❌ Error saving notebook: {e}")
            return False
    else:
        print("ℹ️  No fixes needed")
        return True

def apply_comprehensive_fixes(code):
    """Apply all necessary syntax fixes"""
    
    # 1. Fix unterminated string literals in print statements
    # Pattern: print(f"... or print("...
    code = re.sub(r'print\(f?"([^"]*?)$', r'print(f"\1")', code, flags=re.MULTILINE)
    
    # 2. Fix broken f-strings that lost their closing quotes
    # Look for f" without matching closing quote at end of line
    code = re.sub(r'(print\(f"[^"]*?)(\n|$)', r'\1")\2', code, flags=re.MULTILINE)
    code = re.sub(r'(print\("[^"]*?)(\n|$)', r'\1")\2', code, flags=re.MULTILINE)
    
    # 3. Fix broken array access - " instead of [
    # Pattern: something"key" should be something["key"]
    code = re.sub(r'(\w+)"(\w+)"', r'\1["\2"]', code)
    
    # 4. Fix broken method calls with " instead of .
    # Pattern: object"method" should be object.method
    code = re.sub(r'(\w+)"(\w+)"\s*\.', r'\1.\2.', code)
    
    # 5. Fix broken dictionary/list access chains
    # Pattern: dict"key"."another" should be dict["key"]["another"]
    code = re.sub(r'(\w+)"([^"]+)"\."([^"]+)"', r'\1["\2"]["\3"]', code)
    
    # 6. Fix trailing dots and commas in configuration
    # Pattern: hosts="cluster_url"., should be hosts=cluster_url,
    code = re.sub(r'hosts="([^"]+)"\.,', r'hosts="\1",', code)
    
    # 7. Fix incomplete f-strings and print statements
    # More comprehensive pattern for broken prints
    lines = code.split('\n')
    fixed_lines = []
    
    for line in lines:
        # Skip magic commands
        if line.strip().startswith(('%%', '!')):
            fixed_lines.append(line)
            continue
            
        # Fix specific problematic patterns
        
        # Pattern: print(f" at end of line (missing content and closing)
        if re.match(r'^\s*print\(f?"\s*$', line):
            line = line.rstrip() + 'Fixed print statement")'
        
        # Pattern: print(" with missing closing
        elif re.match(r'^\s*print\([f]?"[^"]*$', line) and not line.rstrip().endswith('"'):
            line = line.rstrip() + '")'
        
        # Pattern: incomplete print with f-string
        elif 'print(f"' in line and not ('"' in line[line.index('print(f"') + 8:]):
            line = line.rstrip() + '")'
        
        # Pattern: incomplete regular print
        elif 'print("' in line and not ('"' in line[line.index('print("') + 7:]):
            line = line.rstrip() + '")'
        
        # Fix array access patterns more specifically
        line = re.sub(r'result\["choices"\]"(\d+)"\."message"\[', r'result["choices"][\1]["message"][', line)
        line = re.sub(r'metadata_df_optimized"([^"]+)"\.', r'metadata_df_optimized["\1"].', line)
        line = re.sub(r'df"([^"]+)"\.', r'df["\1"].', line)
        line = re.sub(r'tables_seen"([^"]+)"\.', r'tables_seen["\1"].', line)
        
        fixed_lines.append(line)
    
    code = '\n'.join(fixed_lines)
    
    # 8. Fix specific PostgreSQL patterns
    # Replace any remaining MSSQL patterns
    code = code.replace('pymssql', 'psycopg2')
    code = code.replace('MSSQL', 'PostgreSQL')
    code = code.replace('mssql', 'postgresql')
    
    # 9. Fix multi-line string issues
    # Look for strings that span multiple lines improperly
    code = re.sub(r'"""([^"]*?)$', r'"""\1"""', code, flags=re.MULTILINE | re.DOTALL)
    
    # 10. Fix batch prompt strings
    code = re.sub(
        r'batch_prompt = "I have multiple database columns to describe\. For each column, provide a concise description \(max 40 words\) of what it contains based on the sample values\.$',
        r'batch_prompt = "I have multiple database columns to describe. For each column, provide a concise description (max 40 words) of what it contains based on the sample values."',
        code,
        flags=re.MULTILINE
    )
    
    return code

def main():
    """Main function"""
    notebook_dir = Path('/home/ubuntu/git-projects/personal/github.com/elasticsearch_opensearch/opensearch/my_tutorial/scripts/5. REALTIME_PROJECTS/4. text_to_sql_visualization_insights_agent/opensearch-POSTGRES-RAG')
    
    notebooks = [
        "1. build_ingest_meta_dictionary.ipynb",
        "2. text-to-sql-viz-insights.ipynb"
    ]
    
    print("🔧 COMPREHENSIVE NOTEBOOK SYNTAX REPAIR")
    print("=" * 80)
    
    all_success = True
    
    for notebook in notebooks:
        notebook_path = notebook_dir / notebook
        if notebook_path.exists():
            success = fix_notebook_syntax(notebook_path)
            all_success = all_success and success
        else:
            print(f"❌ Notebook not found: {notebook_path}")
            all_success = False
    
    print("\n" + "=" * 80)
    if all_success:
        print("🎉 ALL NOTEBOOKS FIXED SUCCESSFULLY!")
    else:
        print("❌ SOME NOTEBOOKS COULD NOT BE FIXED")
    print("=" * 80)
    
    return 0 if all_success else 1

if __name__ == "__main__":
    sys.exit(main())