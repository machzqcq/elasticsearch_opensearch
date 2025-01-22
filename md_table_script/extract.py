from playwright.sync_api import sync_playwright
from tabulate import tabulate

def generate_markdown_table(file_path):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(f'file://{file_path}')
        
        section_panels = page.query_selector_all('div[class*="section--panel--"]')
        
        # Create a dictionary to map section titles to their corresponding data
        data_dict = {}

        for panel in section_panels:
            title_element = panel.query_selector('span[class*="section--section-title--"]')
            section_title = title_element.inner_text() if title_element else "No Title"
            
            # Collect all row data under this section
            section_data = []
            section_rows = panel.query_selector_all('div[class*="section--row--"]')
            for row in section_rows:
                row_text_element = row.query_selector('span')
                if row_text_element:
                    row_text = row_text_element.inner_text()
                    # Escape '|' character
                    row_text = row_text.replace('|', '\\|')
                    section_data.append(row_text)
            
            # Map section title to its row data
            data_dict[section_title] = section_data
        
        # Transpose the data for tabulation
        max_rows = max(len(values) for values in data_dict.values())
        table_data = []

        for i in range(max_rows):
            row = [data_dict[title][i] if i < len(data_dict[title]) else "" for title in data_dict]
            table_data.append(row)
        
        # Convert dictionary keys (section titles) to headers
        headers = list(data_dict.keys())

        # Escape '|' character in headers
        headers = [header.replace('|', '\\|') for header in headers]

        # Convert to markdown table with explicit padding
        markdown_table = tabulate(
            table_data,
            headers=headers,
            tablefmt="pipe",
            stralign="left"
        )
        
        browser.close()
        return markdown_table

if __name__ == "__main__":
    markdown_content = generate_markdown_table('/home/ubuntu/git-projects/personal/github.com/elasticsearch_opensearch/md_table_script/course.html')
    with open('/home/ubuntu/git-projects/personal/github.com/elasticsearch_opensearch/md_table_script/course.md', 'w') as md_file:
        md_file.write(markdown_content)