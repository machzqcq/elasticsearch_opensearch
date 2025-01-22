from playwright.sync_api import sync_playwright
from tabulate import tabulate

def generate_markdown_table(file_path):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(f'file://{file_path}')
        
        section_panels = page.query_selector_all('div[class*="section--panel--"]')
        table_data = []
        headers = []

        for panel in section_panels:
            title_element = panel.query_selector('span[class*="section--section-title--"]')
            section_title = title_element.inner_text() if title_element else "No Title"
            headers.append(section_title)
            
            section_rows = panel.query_selector_all('div[class*="section--row--"]')
            row_data = []
            for row in section_rows:
                row_text_element = row.query_selector('span')
                if row_text_element:
                    row_data.append(row_text_element.inner_text())
            
            table_data.append(row_data)
        
        # Transpose the table data to match the new header structure
        transposed_data = list(map(list, zip(*table_data)))

        # Convert to markdown table
        markdown_table = tabulate(transposed_data, headers=headers, tablefmt="pipe")
        
        browser.close()
        return markdown_table

if __name__ == "__main__":
    markdown_content = generate_markdown_table('/home/ubuntu/git-projects/personal/github.com/elasticsearch_opensearch/test/course.html')
    with open('/home/ubuntu/git-projects/personal/github.com/elasticsearch_opensearch/test/course.md', 'w') as md_file:
        md_file.write(markdown_content)