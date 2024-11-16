import os
import yaml

THEMES = ["mkdocs", "readthedocs", "material"]

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
        "site_name": "OPENSEARCH TUTORIAL",
        "theme": {
            "name": THEMES[1]
        },
        "nav": generate_nav_structure(docs_path)
    }
    with open("mkdocs.yml", "w") as f:
        yaml.dump(config, f, default_flow_style=False, sort_keys=False)

if __name__ == "__main__":
    docs_path = "docs"
    generate_mkdocs_config(docs_path)
    index_content = "# Welcome to OPENSEARCH TUTORIAL\n\n (AUTHOR: PRADEEP@AUTOMATIONPRACTICE.COM)\n"
    for item in generate_nav_structure(docs_path):
        for title, path in item.items():
            if isinstance(path, list):
                index_content += f"## {title}\n"
                for sub_item in path:
                    for sub_title, sub_path in sub_item.items():
                        index_content += f"- [{sub_title}]({sub_path})\n"
            else:
                index_content += f"- [{title}]({path})\n"

    with open(os.path.join(docs_path, "index.md"), "w") as f:
        f.write(index_content)