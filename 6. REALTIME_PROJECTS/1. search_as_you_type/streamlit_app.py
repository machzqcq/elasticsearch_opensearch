"""Streamlit frontend for search-as-you-type application."""
import streamlit as st
import httpx
import asyncio
from typing import List, Dict, Any
import time
import os
from pathlib import Path
from datetime import datetime

# Load environment variables
try:
    from dotenv import load_dotenv
    env_path = Path(__file__).parent / '.env'
    load_dotenv(dotenv_path=env_path)
except ImportError:
    pass  # python-dotenv not installed, use system env vars only

# Configuration
API_BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8000")
DEBOUNCE_DELAY = 0.5  # seconds

# Page configuration
st.set_page_config(
    page_title="E-commerce Search",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .search-result {
        padding: 15px;
        margin: 10px 0;
        border-radius: 8px;
        background-color: #f8f9fa;
        border-left: 4px solid #0066cc;
    }
    .product-name {
        font-size: 18px;
        font-weight: 600;
        color: #1a1a1a;
    }
    .product-detail {
        font-size: 14px;
        color: #555;
        margin: 5px 0;
    }
    .highlight {
        background-color: #fff3cd;
        padding: 2px 4px;
        border-radius: 3px;
    }
    .search-stats {
        color: #666;
        font-size: 14px;
        margin: 10px 0;
    }
    .stTextInput > div > div > input {
        font-size: 16px;
    }
</style>
""", unsafe_allow_html=True)


def search_products(query: str, fields: List[str], size: int = 10) -> Dict[str, Any]:
    """Call the search API."""
    try:
        with httpx.Client(timeout=30.0) as client:
            response = client.post(
                f"{API_BASE_URL}/api/search",
                json={
                    "query": query,
                    "fields": fields,
                    "size": size,
                    "from": 0
                }
            )
            response.raise_for_status()
            return response.json()
    except httpx.HTTPError as e:
        st.error(f"API Error: {str(e)}")
        return None
    except Exception as e:
        st.error(f"Error: {str(e)}")
        return None


def get_suggestions(query: str, field: str) -> List[str]:
    """Get autocomplete suggestions."""
    if not query or len(query) < 2:
        return []
    
    try:
        with httpx.Client(timeout=10.0) as client:
            response = client.post(
                f"{API_BASE_URL}/api/suggestions",
                json={
                    "query": query,
                    "field": field,
                    "size": 5
                }
            )
            response.raise_for_status()
            data = response.json()
            return data.get("suggestions", [])
    except Exception:
        return []


def format_highlight(text: str, highlights: List[str]) -> str:
    """Format text with highlights."""
    if highlights:
        return highlights[0]
    return text


def display_product(hit: Dict[str, Any], index: int):
    """Display a single product result."""
    source = hit.get("source", {})
    highlight = hit.get("highlight", {})
    score = hit.get("score", 0)
    
    # Extract product information
    products = source.get("products", [])
    if products and isinstance(products, list):
        product = products[0]
        
        # Get highlighted or regular fields
        product_name = format_highlight(
            product.get("product_name", "N/A"),
            highlight.get("products.product_name", [])
        )
        category = format_highlight(
            product.get("category", "N/A"),
            highlight.get("products.category", [])
        )
        manufacturer = format_highlight(
            product.get("manufacturer", "N/A"),
            highlight.get("products.manufacturer", [])
        )
        price = product.get("price", 0)
        
        st.markdown(f"""
        <div class="search-result">
            <div class="product-name">
                {index + 1}. {product_name}
            </div>
            <div class="product-detail">
                <strong>Category:</strong> {category}
            </div>
            <div class="product-detail">
                <strong>Manufacturer:</strong> {manufacturer}
            </div>
            <div class="product-detail">
                <strong>Price:</strong> €{price:.2f} | <strong>Relevance Score:</strong> {score:.2f}
            </div>
        </div>
        """, unsafe_allow_html=True)


def main():
    """Main Streamlit application."""
    
    # Initialize session state
    if 'search_results' not in st.session_state:
        st.session_state.search_results = None
    if 'last_executed_query' not in st.session_state:
        st.session_state.last_executed_query = ""
    
    # Header
    st.title("🔍 E-commerce Product Search")
    st.markdown("**Real-time search with autocomplete functionality**")
    
    # Sidebar
    with st.sidebar:
        st.header("⚙️ Search Configuration")
        
        # Field selection
        st.subheader("Search Fields")
        search_product_name = st.checkbox("Product Name", value=True)
        search_category = st.checkbox("Category", value=True)
        search_manufacturer = st.checkbox("Manufacturer", value=True)
        
        # Results configuration
        st.subheader("Results")
        num_results = st.slider("Number of results", 5, 50, 10)
        
        # API status
        st.subheader("🔗 API Status")
        st.caption(f"Backend: {API_BASE_URL}")
        try:
            with httpx.Client(timeout=5.0) as client:
                response = client.get(f"{API_BASE_URL}/api/health")
                if response.status_code == 200:
                    health_data = response.json()
                    st.success("✅ Connected")
                    st.caption(f"Cluster: {health_data.get('cluster_status', 'N/A')}")
                else:
                    st.error("❌ Disconnected")
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")
    
    # Build field list
    fields = []
    if search_product_name:
        fields.append("products.product_name")
    if search_category:
        fields.append("products.category")
    if search_manufacturer:
        fields.append("products.manufacturer")
    
    if not fields:
        st.warning("⚠️ Please select at least one search field from the sidebar.")
        return
    
    # Search input - automatic search on every input change
    search_query = st.text_input(
        "Search products",
        placeholder="Start typing to search... (e.g., 'shirt', 'boots', 'jacket')",
        key="search_input",
        label_visibility="collapsed"
    )
    
    # Perform search automatically when query changes
    if search_query and len(search_query.strip()) > 0:
        # Only search if query is different from last executed query
        if search_query != st.session_state.last_executed_query:
            with st.spinner("Searching..."):
                start_time = time.time()
                results = search_products(search_query, fields, num_results)
                elapsed_time = time.time() - start_time
            
            st.session_state.search_results = {
                'results': results,
                'elapsed_time': elapsed_time
            }
            st.session_state.last_executed_query = search_query
    else:
        # Clear results when search query is empty
        if st.session_state.last_executed_query != "":
            st.session_state.search_results = None
            st.session_state.last_executed_query = ""
    
    # Display results
    if st.session_state.search_results:
        results = st.session_state.search_results['results']
        elapsed_time = st.session_state.search_results['elapsed_time']
        
        if results:
            total = results.get("total", 0)
            took = results.get("took", 0)
            hits = results.get("hits", [])
            
            # Display search statistics
            st.markdown(
                f'<p class="search-stats">Found <strong>{total}</strong> results in '
                f'<strong>{took}ms</strong> (Request time: {elapsed_time*1000:.0f}ms)</p>',
                unsafe_allow_html=True
            )
            
            # Display results
            if hits:
                for idx, hit in enumerate(hits):
                    display_product(hit, idx)
            else:
                st.info("No results found. Try a different search query.")
        
    else:
        # Show example searches
        st.info("👆 Enter a search query above to find products")
        
        with st.expander("💡 Example Searches"):
            st.markdown("""
            Try searching for:
            - **Product types**: shirt, boots, jacket, dress
            - **Categories**: Men's Clothing, Women's Shoes
            - **Manufacturers**: Elitelligence, Oceanavigations
            - **Partial words**: swe (for sweatshirt), boo (for boots)
            """)
        
        with st.expander("ℹ️ How It Works"):
            st.markdown("""
            This search-as-you-type application uses:
            1. **Phrase Prefix Matching**: Matches your partial query at the beginning
            2. **Fuzzy Matching**: Tolerates typos and spelling mistakes
            3. **Phrase Matching**: Finds exact phrases with some flexibility
            4. **Real-time Results**: Updates as you type
            5. **Highlighting**: Shows matched terms in results
            """)


if __name__ == "__main__":
    main()
