import os
import re

def extract_headers(md_content):
    headers = re.findall(r'^(#+)\s+(.*)', md_content, re.MULTILINE)
    return headers

def generate_mermaid_diagram_code(headers):
    mermaid_code = "graph LR;\n"
    subgraph_count = (len(headers) + 3) // 4  # Calculate the total number of subgraphs
    for i, (level, header) in enumerate(headers):
        if i % 4 == 0:
            if i != 0:
                mermaid_code += "    end\n"
            mermaid_code += f"    subgraph Concepts{subgraph_count}\n \t direction LR\n"
            subgraph_count -= 1
        node_id = f"node{i}"
        mermaid_code += f"        {node_id}[{header}];\n"
        if i % 4 != 0:
            prev_node_id = f"node{i-1}"
            mermaid_code += f"        {prev_node_id} --> {node_id};\n"
    if headers:
        mermaid_code += "    end\n"
    return mermaid_code

def process_markdown_files(source_dir, target_dir):
    for root, dirs, files in os.walk(source_dir):
        for file in files:
            if file.endswith('.md'):
                source_file_path = os.path.join(root, file)
                relative_path = os.path.relpath(root, source_dir)
                target_file_dir = os.path.join(target_dir, relative_path)
                target_file_path = os.path.join(target_file_dir, file.replace('.md', '.mermaid'))

                # Ensure the target directory exists
                os.makedirs(target_file_dir, exist_ok=True)

                # Read the markdown file
                with open(source_file_path, 'r') as md_file:
                    md_content = md_file.read()

                # Extract headers and generate mermaid diagram code
                headers = extract_headers(md_content)
                mermaid_code = generate_mermaid_diagram_code(headers)

                # Save the mermaid diagram code to the target file
                with open(target_file_path, 'w') as mermaid_file:
                    mermaid_file.write(mermaid_code)

                print(f"Generated {target_file_path}")

# Example usage
source_directory = 'docs'
target_directory = 'mermaid_diagrams'

# Ensure the source and target directories exist
os.makedirs(source_directory, exist_ok=True)
os.makedirs(target_directory, exist_ok=True)
process_markdown_files(source_directory, target_directory)