#!/usr/bin/env python3
"""
Targeted fix for specific notebook syntax errors
"""

import json
import re
import sys
from pathlib import Path

def fix_notebook_targeted(notebook_path):
    """Fix specific syntax errors in a notebook"""
    print(f"\n🎯 Targeting fixes for: {notebook_path}")
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
            
            # Apply targeted fixes
            fixed_code = apply_targeted_fixes(original_code)
            
            if fixed_code != original_code:
                fixes_applied += 1
                print(f"✓ Fixed cell {cell_idx + 1}")
                
                # Update the cell source
                if isinstance(source, list):
                    # Split by lines and ensure proper line endings
                    lines = fixed_code.split('\n')
                    cell['source'] = []
                    for i, line in enumerate(lines):
                        if i < len(lines) - 1:  # Not the last line
                            cell['source'].append(line + '\n')
                        else:  # Last line
                            if line:  # Only add if not empty
                                cell['source'].append(line)
                else:
                    cell['source'] = fixed_code
    
    if fixes_applied > 0:
        try:
            with open(notebook_path, 'w', encoding='utf-8') as f:
                json.dump(notebook, f, indent=1, ensure_ascii=False)
            print(f"✅ Applied {fixes_applied} targeted fixes to {notebook_path}")
            return True
        except Exception as e:
            print(f"❌ Error saving notebook: {e}")
            return False
    else:
        print("ℹ️  No fixes needed")
        return True

def apply_targeted_fixes(code):
    """Apply targeted syntax fixes"""
    
    # Skip cells that are just magic commands
    if code.strip().startswith('%%'):
        return code
    
    lines = code.split('\n')
    fixed_lines = []
    
    i = 0
    while i < len(lines):
        line = lines[i]
        
        # 1. Fix unterminated strings in print statements
        if 'print(' in line and line.count('"') % 2 == 1:
            # Odd number of quotes - likely unterminated
            if line.rstrip().endswith('"):') or line.rstrip().endswith('")'):
                # Already properly terminated
                fixed_lines.append(line)
            elif line.rstrip().endswith('"'):
                # Has closing quote
                fixed_lines.append(line)
            else:
                # Need to add closing quote and parenthesis
                line = line.rstrip() + '")'
                fixed_lines.append(line)
        
        # 2. Fix array access with quotes instead of brackets
        elif '"' in line and '[' not in line and any(pattern in line for pattern in ['result"choices"', 'metadata_df_optimized"', 'df"', 'tables_seen"']):
            # Fix the specific patterns
            line = re.sub(r'result\["choices"\]"(\d+)"\."message"\[', r'result["choices"][\1]["message"][', line)
            line = re.sub(r'metadata_df_optimized"([^"]+)"\.', r'metadata_df_optimized["\1"].', line)
            line = re.sub(r'df"([^"]+)"\.', r'df["\1"].', line)
            line = re.sub(r'tables_seen"([^"]+)"\.', r'tables_seen["\1"].', line)
            fixed_lines.append(line)
        
        # 3. Handle docstrings and function definitions
        elif line.strip().startswith('def ') and i + 1 < len(lines):
            # This is a function definition, add it
            fixed_lines.append(line)
            
            # Check if next lines are docstring
            j = i + 1
            while j < len(lines):
                next_line = lines[j]
                if next_line.strip().startswith('"""') or next_line.strip().startswith("'''"):
                    # Start of docstring - find the end
                    quote_type = '"""' if '"""' in next_line else "'''"
                    
                    # If it's a single line docstring
                    if next_line.count(quote_type) >= 2:
                        fixed_lines.append(next_line)
                        j += 1
                        break
                    else:
                        # Multi-line docstring
                        fixed_lines.append(next_line)
                        j += 1
                        # Find closing quotes
                        while j < len(lines):
                            docstring_line = lines[j]
                            fixed_lines.append(docstring_line)
                            if quote_type in docstring_line:
                                j += 1
                                break
                            j += 1
                        break
                elif next_line.strip() == '':
                    # Empty line in docstring
                    fixed_lines.append(next_line)
                    j += 1
                elif not next_line.startswith(' ') and not next_line.startswith('\t'):
                    # End of function/docstring
                    break
                else:
                    # Part of docstring content
                    fixed_lines.append(f'    """{next_line.strip()}"""')
                    j += 1
                    break
            
            i = j - 1
        
        # 4. Fix emoji and special characters in strings
        elif any(emoji in line for emoji in ['⚠️', '💡', '📋', '📝', '✓', '→', '📊', '❌', '💬', '📈', '📋']):
            # These are likely in print statements - escape them properly
            if 'print(' in line:
                # Find the emoji and wrap the string properly
                line = re.sub(r'([⚠️💡📋📝✓→📊❌💬📈])', r'"\1"', line)
                # Clean up any double quotes
                line = re.sub(r'""([^"]*?)""', r'"\1"', line)
            fixed_lines.append(line)
        
        # 5. Fix incomplete lines that end with dots
        elif line.rstrip().endswith('.') and not any(op in line for op in ['import', 'from', 'def', 'class']):
            # Likely an incomplete statement
            line = line.rstrip()[:-1]  # Remove trailing dot
            fixed_lines.append(line)
        
        # 6. Fix SQL syntax issues
        elif 'SELECT TOP' in line:
            # PostgreSQL doesn't use SELECT TOP
            line = line.replace('SELECT TOP (1000)', 'SELECT')
            line = line.replace('SELECT TOP(1000)', 'SELECT')
            fixed_lines.append(line)
        
        # 7. Fix incomplete print statements that span multiple lines
        elif line.strip().endswith('"):') and i > 0 and 'print(' in lines[i-1]:
            # This looks like the end of a multi-line print
            fixed_lines.append(line)
        
        else:
            # No specific fix needed
            fixed_lines.append(line)
        
        i += 1
    
    return '\n'.join(fixed_lines)

def main():
    """Main function"""
    notebook_dir = Path('/home/ubuntu/git-projects/personal/github.com/elasticsearch_opensearch/opensearch/my_tutorial/scripts/5. REALTIME_PROJECTS/4. text_to_sql_visualization_insights_agent/opensearch-POSTGRES-RAG')
    
    notebooks = [
        "1. build_ingest_meta_dictionary.ipynb",
        "2. text-to-sql-viz-insights.ipynb"
    ]
    
    print("🎯 TARGETED NOTEBOOK SYNTAX REPAIR")
    print("=" * 80)
    
    all_success = True
    
    for notebook in notebooks:
        notebook_path = notebook_dir / notebook
        if notebook_path.exists():
            success = fix_notebook_targeted(notebook_path)
            all_success = all_success and success
        else:
            print(f"❌ Notebook not found: {notebook_path}")
            all_success = False
    
    print("\n" + "=" * 80)
    if all_success:
        print("🎉 ALL NOTEBOOKS REPAIRED!")
    else:
        print("❌ SOME NOTEBOOKS COULD NOT BE REPAIRED")
    print("=" * 80)
    
    return 0 if all_success else 1

if __name__ == "__main__":
    sys.exit(main())