import os
import subprocess

def generate_image_from_mermaid(mermaid_file_path, output_image_path, image_format):
    # Ensure the output directory exists
    os.makedirs(os.path.dirname(output_image_path), exist_ok=True)
    
    try:
        # Use mermaid-cli to generate the image
        subprocess.run(['mmdc', '-i', mermaid_file_path, '-o', output_image_path, '-t', image_format], check=True)
        print(f"Generated image {output_image_path}")
    except subprocess.CalledProcessError as e:
        print(f"Failed to generate image for {mermaid_file_path}: {e}")

def process_mermaid_files(source_dir, target_dir, image_format):
    for root, dirs, files in os.walk(source_dir):
        for file in files:
            if file.endswith('.mermaid'):
                source_file_path = os.path.join(root, file)
                relative_path = os.path.relpath(root, source_dir)
                target_file_dir = os.path.join(target_dir, relative_path)
                target_file_path = os.path.join(target_file_dir, file.replace('.mermaid', f'.{image_format}'))

                # Generate image from mermaid diagram code
                generate_image_from_mermaid(source_file_path, target_file_path, image_format)

# Example usage
source_directory = 'mermaid_diagrams'
target_directory = 'mermaid_images'

# Ensure the source and target directories exist
os.makedirs(source_directory, exist_ok=True)
os.makedirs(target_directory, exist_ok=True)
image_format = 'png'  # Change to 'svg' if you want to generate SVG images

process_mermaid_files(source_directory, target_directory, image_format)