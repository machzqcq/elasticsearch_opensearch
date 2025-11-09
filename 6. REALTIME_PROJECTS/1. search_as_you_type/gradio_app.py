"""Gradio frontend for search-as-you-type application."""
import gradio as gr
import httpx
from typing import List, Dict, Any, Tuple
import pandas as pd
import os
from pathlib import Path

# Load environment variables
try:
    from dotenv import load_dotenv
    env_path = Path(__file__).parent / '.env'
    load_dotenv(dotenv_path=env_path)
except ImportError:
    pass  # python-dotenv not installed, use system env vars only

# Configuration
API_BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8000")


def search_products(
    query: str,
    search_product_name: bool,
    search_category: bool,
    search_manufacturer: bool,
    num_results: int
) -> Tuple[str, pd.DataFrame]:
    """
    Search products and return results.
    
    Returns:
        Tuple of (status_message, results_dataframe)
    """
    if not query or not query.strip():
        return "Please enter a search query", pd.DataFrame()
    
    # Build field list
    fields = []
    if search_product_name:
        fields.append("products.product_name")
    if search_category:
        fields.append("products.category")
    if search_manufacturer:
        fields.append("products.manufacturer")
    
    if not fields:
        return "Please select at least one search field", pd.DataFrame()
    
    try:
        with httpx.Client(timeout=30.0) as client:
            response = client.post(
                f"{API_BASE_URL}/api/search",
                json={
                    "query": query,
                    "fields": fields,
                    "size": num_results,
                    "from": 0
                }
            )
            response.raise_for_status()
            data = response.json()
        
        total = data.get("total", 0)
        took = data.get("took", 0)
        hits = data.get("hits", [])
        
        if not hits:
            return f"No results found for '{query}'", pd.DataFrame()
        
        # Transform hits to DataFrame
        results = []
        for hit in hits:
            source = hit.get("source", {})
            products = source.get("products", [])
            
            if products and isinstance(products, list):
                product = products[0]
                results.append({
                    "Product Name": product.get("product_name", "N/A"),
                    "Category": product.get("category", "N/A"),
                    "Manufacturer": product.get("manufacturer", "N/A"),
                    "Price (€)": f"{product.get('price', 0):.2f}",
                    "Score": f"{hit.get('score', 0):.2f}",
                })
        
        df = pd.DataFrame(results)
        status = f"✅ Found {total} results in {took}ms"
        
        return status, df
        
    except httpx.HTTPError as e:
        return f"❌ API Error: {str(e)}", pd.DataFrame()
    except Exception as e:
        return f"❌ Error: {str(e)}", pd.DataFrame()


def check_api_health() -> str:
    """Check API health status."""
    try:
        with httpx.Client(timeout=5.0) as client:
            response = client.get(f"{API_BASE_URL}/api/health")
            if response.status_code == 200:
                health_data = response.json()
                cluster_status = health_data.get("cluster_status", "N/A")
                nodes = health_data.get("number_of_nodes", "N/A")
                return f"✅ API Connected | Cluster: {cluster_status} | Nodes: {nodes}"
            else:
                return "❌ API Disconnected"
    except Exception as e:
        return f"❌ API Unavailable: {str(e)}"


def create_interface():
    """Create Gradio interface."""
    
    # Custom CSS
    css = """
    .gradio-container {
        font-family: 'Arial', sans-serif;
    }
    .search-header {
        text-align: center;
        padding: 20px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 10px;
        margin-bottom: 20px;
    }
    """
    
    with gr.Blocks(css=css, title="E-commerce Search") as demo:
        
        # Header
        gr.Markdown(
            """
            <div class="search-header">
                <h1>🔍 E-commerce Product Search</h1>
                <p>Real-time search with autocomplete functionality</p>
            </div>
            """
        )
        
        with gr.Row():
            # Left column - Search configuration
            with gr.Column(scale=1):
                gr.Markdown("### ⚙️ Search Configuration")
                
                gr.Markdown("**Search Fields**")
                search_product_name = gr.Checkbox(
                    label="Product Name",
                    value=True
                )
                search_category = gr.Checkbox(
                    label="Category",
                    value=True
                )
                search_manufacturer = gr.Checkbox(
                    label="Manufacturer",
                    value=True
                )
                
                gr.Markdown("**Results**")
                num_results = gr.Slider(
                    minimum=5,
                    maximum=50,
                    value=10,
                    step=1,
                    label="Number of results"
                )
                
                gr.Markdown("### 🔗 API Status")
                api_status = gr.Textbox(
                    label="Status",
                    interactive=False,
                    value=check_api_health()
                )
                refresh_btn = gr.Button("Refresh Status", size="sm")
                refresh_btn.click(
                    fn=check_api_health,
                    outputs=api_status
                )
            
            # Right column - Search and results
            with gr.Column(scale=3):
                gr.Markdown("### 🔎 Search Products")
                
                search_input = gr.Textbox(
                    label="Search Query",
                    placeholder="Start typing to search... (e.g., 'shirt', 'boots', 'jacket')",
                    lines=1
                )
                
                search_btn = gr.Button(
                    "Search",
                    variant="primary",
                    size="lg"
                )
                
                status_output = gr.Textbox(
                    label="Search Status",
                    interactive=False
                )
                
                results_output = gr.Dataframe(
                    label="Search Results",
                    wrap=True,
                    interactive=False
                )
                
                # Examples section
                with gr.Accordion("💡 Example Searches", open=False):
                    gr.Markdown("""
                    Try searching for:
                    - **Product types**: shirt, boots, jacket, dress
                    - **Categories**: Men's Clothing, Women's Shoes
                    - **Manufacturers**: Elitelligence, Oceanavigations
                    - **Partial words**: swe (for sweatshirt), boo (for boots)
                    """)
                
                with gr.Accordion("ℹ️ How It Works", open=False):
                    gr.Markdown("""
                    This search-as-you-type application uses:
                    1. **Phrase Prefix Matching**: Matches your partial query at the beginning
                    2. **Fuzzy Matching**: Tolerates typos and spelling mistakes
                    3. **Phrase Matching**: Finds exact phrases with some flexibility
                    4. **Real-time Results**: Updates as you type
                    5. **Highlighting**: Shows matched terms in results
                    
                    **Backend**: FastAPI with OpenSearch
                    **Frontend**: Gradio
                    """)
        
        # Event handlers - real-time search on input change with debouncing
        search_input.change(
            fn=search_products,
            inputs=[
                search_input,
                search_product_name,
                search_category,
                search_manufacturer,
                num_results
            ],
            outputs=[status_output, results_output],
            trigger_mode="always_last"  # Real-time with automatic debouncing
        )
        
        # Also handle button click for explicit search
        search_btn.click(
            fn=search_products,
            inputs=[
                search_input,
                search_product_name,
                search_category,
                search_manufacturer,
                num_results
            ],
            outputs=[status_output, results_output]
        )
        
        # Also trigger on Enter key
        search_input.submit(
            fn=search_products,
            inputs=[
                search_input,
                search_product_name,
                search_category,
                search_manufacturer,
                num_results
            ],
            outputs=[status_output, results_output]
        )
    
    return demo


if __name__ == "__main__":
    demo = create_interface()
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False
    )
