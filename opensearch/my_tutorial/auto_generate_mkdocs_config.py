import os
import yaml

def generate_nav_structure(base_path, current_path=""):
    nav = []
    for item in sorted(os.listdir(os.path.join(base_path, current_path))):
        item_path = os.path.join(current_path, item)
        if os.path.isdir(os.path.join(base_path, item_path)):
            nav.append({item.capitalize(): generate_nav_structure(base_path, item_path)})
        elif item.endswith(".md"):
            nav.append({item.replace(".md", "").capitalize(): item_path.replace("\\", "/")})
    return nav

def generate_mkdocs_config(docs_path):
    config = {
        "site_name": "My Documentation Site",
        "theme": {
            "name": "mkdocs"
        },
        "nav": generate_nav_structure(docs_path)
    }
    with open("mkdocs.yml", "w") as f:
        yaml.dump(config, f, default_flow_style=False, sort_keys=False)

if __name__ == "__main__":
    docs_path = "docs"
    generate_mkdocs_config(docs_path)