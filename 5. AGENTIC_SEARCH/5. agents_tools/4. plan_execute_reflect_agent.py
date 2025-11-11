# ================================================================================
# PLAN-EXECUTE-REFLECT AGENT - DEMONSTRATING ADVANCED AGENT WORKFLOW
# ================================================================================
# This script demonstrates the Plan-Execute-Reflect (PER) agent pattern,
# an advanced workflow where an AI agent:
#   1. PLAN: Breaks down a complex problem into actionable steps
#   2. EXECUTE: Performs each step and collects results
#   3. REFLECT: Analyzes results, identifies gaps, and refines the approach
#
# Workflow Diagram:
# ┌─────────────────────────────────────────────────────────────────────┐
# │                  PLAN-EXECUTE-REFLECT AGENT LOOP                    │
# ├─────────────────────────────────────────────────────────────────────┤
# │                                                                       │
# │  Question/Task                                                       │
# │      │                                                               │
# │      └─────────────────────────┐                                    │
# │                                v                                    │
# │                    ┌───────────────────┐                           │
# │                    │   PLAN PHASE      │  Agent thinks about       │
# │                    │                   │  solution approach        │
# │                    │ - Identify steps  │                           │
# │                    │ - Select tools    │                           │
# │                    │ - Create plan     │                           │
# │                    └───────────────────┘                           │
# │                            │                                       │
# │                            v                                       │
# │                    ┌───────────────────┐                           │
# │                    │ EXECUTE PHASE     │  Agent executes plan      │
# │                    │                   │  using available tools    │
# │                    │ - Tool 1: Search  │                           │
# │                    │ - Tool 2: Analyze │                           │
# │                    │ - Collect results │                           │
# │                    └───────────────────┘                           │
# │                            │                                       │
# │                            v                                       │
# │                    ┌───────────────────┐                           │
# │                    │ REFLECT PHASE     │  Agent evaluates results  │
# │                    │                   │  and decides next steps   │
# │                    │ - Check completeness                          │
# │                    │ - Identify gaps   │                           │
# │                    │ - Success or retry│                           │
# │                    └───────────────────┘                           │
# │                            │                                       │
# │         ┌──────────────────┼──────────────────┐                   │
# │         │                  │                  │                   │
# │     Success            Need More          Complete               │
# │         │              Information         Loop                  │
# │         v              │                   v                     │
# │   Final Answer         └──→ (Back to PLAN)  Done                │
# │                                                                   │
# └─────────────────────────────────────────────────────────────────────┘
#
# Reuses:
# - OpenSearch client initialization from openai_agent_tools.py
# - OpenAI connector setup from openai_agent_tools.py
# - Embedding model registration and deployment patterns
#
# ================================================================================

import json
import os
import sys
import time
import warnings
from dotenv import load_dotenv
from opensearchpy import OpenSearch

# Try to import IPython for Jupyter notebook support (optional)
try:
    from IPython.display import Markdown, display
    JUPYTER_AVAILABLE = True
except ImportError:
    JUPYTER_AVAILABLE = False

# ================================================================================
# CONFIGURATION AND SETUP
# ================================================================================

# Suppress warnings for cleaner output
warnings.filterwarnings("ignore", message="Unverified HTTPS request")
warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", message="using SSL with verify_certs=False is insecure.")

# Load environment variables from .env file
load_dotenv("../../.env")

# Environment configuration
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

# OpenSearch cluster configuration
HOST = 'localhost'
PORT = 9200
CLUSTER_URL = {'host': HOST, 'port': PORT}
DEFAULT_USERNAME = 'admin'
DEFAULT_PASSWORD = 'Developer@123'
USE_AUTHENTICATION = True

# Model configuration
OPENAI_MODEL = "gpt-4o-mini"  # You can also use "gpt-3.5-turbo" or other OpenAI models

# ================================================================================
# SIMULATED PRODUCT INVENTORY DATA (50+ Products)
# ================================================================================
# For demonstration purposes, we'll use a retail inventory scenario
# where the agent needs to search, analyze, and reflect on product queries

SAMPLE_PRODUCTS = [
    # Electronics Department
    {"id": 1, "name": "Wireless Bluetooth Headphones", "category": "Electronics", "price": 79.99, "stock": 150, "rating": 4.5, "description": "High-quality wireless headphones with noise cancellation and 30-hour battery life"},
    {"id": 2, "name": "USB-C Charging Cable", "category": "Electronics", "price": 12.99, "stock": 500, "rating": 4.2, "description": "Durable 6-foot USB-C cable compatible with phones, tablets, and laptops"},
    {"id": 3, "name": "4K Webcam", "category": "Electronics", "price": 149.99, "stock": 80, "rating": 4.7, "description": "Professional 4K webcam with auto-focus and built-in microphone"},
    {"id": 4, "name": "Mechanical Keyboard", "category": "Electronics", "price": 129.99, "stock": 120, "rating": 4.6, "description": "RGB mechanical keyboard with customizable switches and programmable keys"},
    {"id": 5, "name": "Portable SSD 1TB", "category": "Electronics", "price": 99.99, "stock": 200, "rating": 4.8, "description": "Fast portable solid-state drive with USB 3.1 for quick file transfers"},
    {"id": 6, "name": "Wireless Mouse", "category": "Electronics", "price": 29.99, "stock": 300, "rating": 4.3, "description": "Ergonomic wireless mouse with precision tracking and long battery life"},
    {"id": 7, "name": "Laptop Stand", "category": "Electronics", "price": 39.99, "stock": 250, "rating": 4.4, "description": "Adjustable aluminum laptop stand for improved ergonomics"},
    {"id": 8, "name": "Monitor Light Bar", "category": "Electronics", "price": 69.99, "stock": 100, "rating": 4.5, "description": "Auto-dimming monitor light bar that reduces eye strain"},
    {"id": 9, "name": "Wireless Charging Pad", "category": "Electronics", "price": 34.99, "stock": 180, "rating": 4.2, "description": "Fast wireless charging pad compatible with all Qi-enabled devices"},
    {"id": 10, "name": "Smart Power Strip", "category": "Electronics", "price": 44.99, "stock": 220, "rating": 4.4, "description": "WiFi-enabled smart power strip with 4 outlets and USB charging"},
    
    # Office Supplies
    {"id": 11, "name": "Notebook Set", "category": "Office Supplies", "price": 14.99, "stock": 400, "rating": 4.1, "description": "Pack of 3 premium ruled notebooks for note-taking"},
    {"id": 12, "name": "Pen Set", "category": "Office Supplies", "price": 19.99, "stock": 350, "rating": 4.0, "description": "Professional ballpoint pen set with smooth ink flow"},
    {"id": 13, "name": "Desk Organizer", "category": "Office Supplies", "price": 24.99, "stock": 280, "rating": 4.3, "description": "Wooden desk organizer with compartments for supplies"},
    {"id": 14, "name": "File Folder Set", "category": "Office Supplies", "price": 9.99, "stock": 600, "rating": 3.9, "description": "Set of 10 colorful file folders for document organization"},
    {"id": 15, "name": "Desk Lamp", "category": "Office Supplies", "price": 49.99, "stock": 160, "rating": 4.5, "description": "LED desk lamp with adjustable brightness and color temperature"},
    {"id": 16, "name": "Sticky Notes Pack", "category": "Office Supplies", "price": 7.99, "stock": 800, "rating": 3.8, "description": "Multi-color adhesive notes for reminders and notes"},
    {"id": 17, "name": "Stapler and Staples", "category": "Office Supplies", "price": 12.99, "stock": 500, "rating": 3.7, "description": "Durable stapler with box of staples included"},
    {"id": 18, "name": "Desk Pad", "category": "Office Supplies", "price": 22.99, "stock": 200, "rating": 4.2, "description": "Large anti-slip desk pad for mouse and keyboard"},
    {"id": 19, "name": "Document Scanner", "category": "Office Supplies", "price": 89.99, "stock": 75, "rating": 4.6, "description": "Compact portable document scanner for digitizing papers"},
    {"id": 20, "name": "Office Chair Cushion", "category": "Office Supplies", "price": 34.99, "stock": 190, "rating": 4.2, "description": "Ergonomic memory foam chair cushion for comfort"},
    
    # Home & Living
    {"id": 21, "name": "Coffee Maker", "category": "Home & Living", "price": 59.99, "stock": 110, "rating": 4.4, "description": "Automatic coffee maker with programmable timer and thermal carafe"},
    {"id": 22, "name": "Desk Humidifier", "category": "Home & Living", "price": 39.99, "stock": 140, "rating": 4.1, "description": "Ultrasonic humidifier perfect for office or bedroom"},
    {"id": 23, "name": "White Noise Machine", "category": "Home & Living", "price": 29.99, "stock": 170, "rating": 4.3, "description": "Compact white noise machine with 10 soothing sounds"},
    {"id": 24, "name": "Air Purifier", "category": "Home & Living", "price": 79.99, "stock": 95, "rating": 4.6, "description": "HEPA air purifier for rooms up to 300 square feet"},
    {"id": 25, "name": "Desk Plant", "category": "Home & Living", "price": 15.99, "stock": 320, "rating": 4.5, "description": "Low-maintenance indoor plant with attractive ceramic pot"},
    {"id": 26, "name": "Desk Calendar", "category": "Home & Living", "price": 8.99, "stock": 450, "rating": 3.9, "description": "Annual desk calendar with space for notes"},
    {"id": 27, "name": "Picture Frame Set", "category": "Home & Living", "price": 24.99, "stock": 210, "rating": 4.2, "description": "Set of 3 modern picture frames for desk decoration"},
    {"id": 28, "name": "Desk Lamp with USB", "category": "Home & Living", "price": 54.99, "stock": 130, "rating": 4.4, "description": "LED desk lamp with built-in USB charging port"},
    {"id": 29, "name": "Motivational Quote Board", "category": "Home & Living", "price": 16.99, "stock": 380, "rating": 4.0, "description": "Wooden quote board with inspirational messages"},
    {"id": 30, "name": "Desk Mirror", "category": "Home & Living", "price": 18.99, "stock": 260, "rating": 4.1, "description": "Compact desktop mirror with adjustable angle"},
    
    # Furniture
    {"id": 31, "name": "Standing Desk", "category": "Furniture", "price": 299.99, "stock": 45, "rating": 4.7, "description": "Electric adjustable standing desk with memory presets"},
    {"id": 32, "name": "Ergonomic Office Chair", "category": "Furniture", "price": 249.99, "stock": 60, "rating": 4.6, "description": "High-back ergonomic office chair with lumbar support"},
    {"id": 33, "name": "Bookshelf", "category": "Furniture", "price": 79.99, "stock": 85, "rating": 4.3, "description": "5-shelf wooden bookshelf for office storage"},
    {"id": 34, "name": "Filing Cabinet", "category": "Furniture", "price": 119.99, "stock": 55, "rating": 4.4, "description": "4-drawer metal filing cabinet with lock"},
    {"id": 35, "name": "Desk", "category": "Furniture", "price": 179.99, "stock": 70, "rating": 4.5, "description": "Large wooden desk with cable management"},
    {"id": 36, "name": "Storage Bench", "category": "Furniture", "price": 99.99, "stock": 90, "rating": 4.2, "description": "Upholstered storage bench for office or home"},
    {"id": 37, "name": "Shelf Unit", "category": "Furniture", "price": 149.99, "stock": 65, "rating": 4.4, "description": "Modular metal shelf unit for flexible storage"},
    {"id": 38, "name": "Conference Table", "category": "Furniture", "price": 499.99, "stock": 20, "rating": 4.8, "description": "Large conference table for meetings"},
    {"id": 39, "name": "Desk Drawer Organizer", "category": "Furniture", "price": 34.99, "stock": 280, "rating": 4.3, "description": "Multi-compartment desk drawer organizer"},
    {"id": 40, "name": "Mobile Storage Cart", "category": "Furniture", "price": 89.99, "stock": 100, "rating": 4.4, "description": "Rolling storage cart with three shelves"},
    
    # Accessories
    {"id": 41, "name": "Phone Stand", "category": "Accessories", "price": 14.99, "stock": 380, "rating": 4.2, "description": "Adjustable phone stand for any smartphone"},
    {"id": 42, "name": "Desk Cable Organizer", "category": "Accessories", "price": 11.99, "stock": 520, "rating": 4.1, "description": "Silicone cable organizer clips for desk"},
    {"id": 43, "name": "Desk Nameplate", "category": "Accessories", "price": 19.99, "stock": 240, "rating": 4.0, "description": "Engraved wooden desk nameplate"},
    {"id": 44, "name": "Desktop Organizer", "category": "Accessories", "price": 29.99, "stock": 290, "rating": 4.3, "description": "Multi-tier desktop organizer for supplies"},
    {"id": 45, "name": "Desk Plant Holder", "category": "Accessories", "price": 12.99, "stock": 340, "rating": 4.1, "description": "Ceramic plant holder for desk decoration"},
    {"id": 46, "name": "Monitor Stand", "category": "Accessories", "price": 44.99, "stock": 200, "rating": 4.4, "description": "Monitor stand with storage drawer underneath"},
    {"id": 47, "name": "Mouse Pad", "category": "Accessories", "price": 16.99, "stock": 450, "rating": 4.2, "description": "Large ergonomic mouse pad with wrist support"},
    {"id": 48, "name": "Desk Drawer Dividers", "category": "Accessories", "price": 8.99, "stock": 600, "rating": 3.9, "description": "Adjustable drawer dividers for organization"},
    {"id": 49, "name": "Headphone Stand", "category": "Accessories", "price": 17.99, "stock": 310, "rating": 4.1, "description": "Minimalist aluminum headphone stand"},
    {"id": 50, "name": "Desk Clock", "category": "Accessories", "price": 24.99, "stock": 270, "rating": 4.3, "description": "Modern digital desk clock with temperature display"},
    {"id": 51, "name": "USB Hub", "category": "Accessories", "price": 32.99, "stock": 220, "rating": 4.5, "description": "7-port USB 3.0 hub for expanded connectivity"},
    {"id": 52, "name": "Document Holder", "category": "Accessories", "price": 13.99, "stock": 380, "rating": 4.0, "description": "Adjustable document holder for typing reference"},
    {"id": 53, "name": "Desk Shelf Riser", "category": "Accessories", "price": 21.99, "stock": 320, "rating": 4.2, "description": "Metal desk shelf riser with storage underneath"},
    {"id": 54, "name": "Cable Management Box", "category": "Accessories", "price": 19.99, "stock": 350, "rating": 4.1, "description": "Wooden cable management box to hide wires"},
    {"id": 55, "name": "Desk Coaster Set", "category": "Accessories", "price": 14.99, "stock": 420, "rating": 4.0, "description": "Set of 4 cork desk coasters"},
]

# ================================================================================
# HELPER FUNCTIONS
# ================================================================================

def get_os_client(cluster_url=CLUSTER_URL, username=DEFAULT_USERNAME, 
                   password=DEFAULT_PASSWORD, use_auth=USE_AUTHENTICATION):
    """
    Create and return an OpenSearch client with SSL configuration.
    Reused from openai_agent_tools.py
    
    Args:
        cluster_url (dict): Dictionary containing host and port information
        username (str): OpenSearch username for authentication
        password (str): OpenSearch password for authentication
        use_auth (bool): Whether to use authentication
        
    Returns:
        OpenSearch: Configured OpenSearch client instance
    """
    if use_auth:
        client = OpenSearch(
            hosts=[cluster_url],
            http_auth=(username, password),
            verify_certs=False,
            ssl_assert_hostname=False,
            ssl_show_warn=False,
            use_ssl=True,
            timeout=300
        )
    else:
        client = OpenSearch(
            hosts=[cluster_url],
            verify_certs=False,
            ssl_assert_hostname=False,
            ssl_show_warn=False,
            use_ssl=False,
            timeout=300
        )
    return client


def wait_for_model_deployment(client, model_id, timeout=300, check_interval=5):
    """
    Wait for a model to reach DEPLOYED state.
    Reused from openai_agent_tools.py
    
    Args:
        client: OpenSearch client instance
        model_id (str): ID of the model to monitor
        timeout (int): Maximum time to wait in seconds
        check_interval (int): Time between status checks in seconds
        
    Returns:
        bool: True if model deployed successfully, False if timeout or error
    """
    start_time = time.time()
    while True:
        status_response = client.transport.perform_request('GET', f'/_plugins/_ml/models/{model_id}')
        current_status = status_response['model_state']
        print(f"   Model status: {current_status}")
        
        if current_status == 'DEPLOYED':
            print("   ✓ Model deployed successfully!")
            return True
        elif current_status == 'FAILED':
            print("   ✗ Model deployment failed!")
            return False
            
        if time.time() - start_time > timeout:
            print("   ✗ Model deployment timeout!")
            return False
            
        time.sleep(check_interval)


def print_mermaid_diagram(diagram_type="overview"):
    """
    Print colorful Mermaid diagrams explaining the workflow to students.
    """
    if diagram_type == "overview":
        print("""
        
╔════════════════════════════════════════════════════════════════════════════════╗
║                    PLAN-EXECUTE-REFLECT AGENT PATTERN                          ║
╚════════════════════════════════════════════════════════════════════════════════╝

┌──────────────────────────────────────────────────────────────────────────────┐
│                         AGENT WORKFLOW MERMAID                                │
└──────────────────────────────────────────────────────────────────────────────┘

flowchart TD
    A["🚀 START: User Question/Task"] --> B["💭 PLAN PHASE"]
    B --> B1["Analyze the problem"]
    B --> B2["Break into sub-tasks"]
    B --> B3["Decide which tools to use"]
    B1 --> C["⚙️ EXECUTE PHASE"]
    B2 --> C
    B3 --> C
    
    C --> C1["🔍 Tool 1: Search Products"]
    C --> C2["📊 Tool 2: Analyze Data"]
    C --> C3["🎯 Tool 3: Calculate Metrics"]
    
    C1 --> D["🤔 REFLECT PHASE"]
    C2 --> D
    C3 --> D
    
    D --> D1{Is Answer Complete?}
    
    D1 -->|❌ No, Need More Info| E["Identify Gaps"]
    E --> B
    
    D1 -->|✅ Yes, Success!| F["📤 FINAL ANSWER"]
    
    style A fill:#4A90E2,stroke:#2E5C8A,stroke-width:3px,color:#fff
    style B fill:#F39C12,stroke:#C87F0A,stroke-width:2px,color:#000
    style C fill:#E74C3C,stroke:#C0392B,stroke-width:2px,color:#fff
    style D fill:#27AE60,stroke:#1E8449,stroke-width:2px,color:#fff
    style F fill:#8E44AD,stroke:#663399,stroke-width:3px,color:#fff
    style D1 fill:#F39C12,stroke:#C87F0A,stroke-width:2px,color:#000

        """)
    
    elif diagram_type == "phases":
        print("""
        
┌──────────────────────────────────────────────────────────────────────────────┐
│                      THREE CRITICAL PHASES                                    │
└──────────────────────────────────────────────────────────────────────────────┘

╔══════════════════════╦════════════════════════╦════════════════════════════╗
║  PHASE 1: PLAN       ║  PHASE 2: EXECUTE      ║  PHASE 3: REFLECT         ║
╠══════════════════════╬════════════════════════╬════════════════════════════╣
║                      ║                        ║                            ║
║  "What should I do?" ║  "Let me do it"        ║  "Did it work?"            ║
║                      ║                        ║                            ║
║  ✓ Understand goal   ║  ✓ Run Tools           ║  ✓ Evaluate Results       ║
║  ✓ List sub-tasks   ║  ✓ Collect output      ║  ✓ Check completeness     ║
║  ✓ Choose tools      ║  ✓ Handle errors       ║  ✓ Identify gaps          ║
║  ✓ Set expectations  ║  ✓ Track progress      ║  ✓ Plan next steps        ║
║                      ║                        ║                            ║
║  Takes 1-2 calls     ║  Takes 1-N calls       ║  Takes 1-2 calls          ║
║  to LLM              ║  to tools              ║  to LLM                    ║
║                      ║                        ║                            ║
╚══════════════════════╩════════════════════════╩════════════════════════════╝

        """)
    
    elif diagram_type == "tool_selection":
        print("""
        
┌──────────────────────────────────────────────────────────────────────────────┐
│                    TOOL SELECTION IN PLANNING                                 │
└──────────────────────────────────────────────────────────────────────────────┘

    User Question
         |
         v
    ┌────────────────────────┐
    │ PLANNING AGENT         │
    │ "Which tools do I      │
    │  need for this task?"  │
    └────────────────────────┘
         |
    ┌────┴────────────────────────────┐
    |                                  |
    v                                  v
┌──────────────┐              ┌──────────────────┐
│ VectorDBTool │              │ SearchIndexTool  │
│              │              │                  │
│ • Semantic   │              │ • Keyword        │
│   search     │              │   search         │
│ • Similarity │              │ • Filters        │
│   matching   │              │ • Aggregations   │
└──────────────┘              └──────────────────┘
    |                                  |
    └────────┬──────────────────────────┘
             |
             v
    ┌──────────────────────────┐
    │ REFLECTION AGENT         │
    │ "Do the results answer   │
    │  the user's question?"   │
    └──────────────────────────┘

        """)

def print_color_section(title, color_code):
    """Print a colored section header for better visualization."""
    colors = {
        "PLAN": "\033[94m",      # Blue
        "EXECUTE": "\033[91m",   # Red
        "REFLECT": "\033[92m",   # Green
        "RESULT": "\033[95m",    # Magenta
    }
    reset = "\033[0m"
    color = colors.get(color_code, "\033[0m")
    print(f"\n{color}{'='*80}")
    print(f"{title}")
    print(f"{'='*80}{reset}\n")


# ================================================================================
# MAIN EXECUTION WORKFLOW
# ================================================================================

def main():
    """
    Main function demonstrating Plan-Execute-Reflect Agent Pattern.
    
    Steps:
    1. Initialize OpenSearch client and configure cluster
    2. Setup embedding model for semantic search
    3. Create ingest pipeline and index with product data
    4. Bulk index 50+ product documents
    5. Create OpenAI connector and deploy model
    6. Register and execute Plan-Execute-Reflect agent
    7. Demonstrate the three phases with multiple queries
    """
    
    print("\n" + "="*80)
    print("PLAN-EXECUTE-REFLECT AGENT - Advanced Agent Workflow Demonstration")
    print("="*80 + "\n")
    
    # Print the main diagram
    print_mermaid_diagram("overview")
    print_mermaid_diagram("phases")
    print_mermaid_diagram("tool_selection")
    
    # ============================================================================
    # STEP 1: INITIALIZE CLIENT AND CONFIGURE CLUSTER
    # ============================================================================
    
    print_color_section("STEP 1: Initializing OpenSearch Client", "PLAN")
    
    client = get_os_client()
    print("   ✓ OpenSearch client initialized\n")
    
    # Configure cluster settings to accept OpenAI as trusted connector endpoint
    print("   Configuring cluster settings for OpenAI connector...")
    cluster_settings = {
        "persistent": {
            "plugins.ml_commons.trusted_connector_endpoints_regex": "^https://api\\.openai\\.com/.*$",
            "plugins.ml_commons.only_run_on_ml_node": "false",
            "plugins.ml_commons.memory_feature_enabled": "true"
        }
    }
    client.cluster.put_settings(body=cluster_settings)
    print("   ✓ Cluster settings configured successfully\n")
    
    # ============================================================================
    # STEP 2: SETUP EMBEDDING MODEL FOR SEMANTIC SEARCH
    # ============================================================================
    
    print_color_section("STEP 2: Setting up Embedding Model", "EXECUTE")
    
    print("   Registering HuggingFace sentence-transformers model...")
    
    embedding_model_body = {
        "name": "huggingface/sentence-transformers/all-MiniLM-L6-v2",
        "version": "1.0.1",
        "model_format": "TORCH_SCRIPT"
    }
    embedding_response = client.transport.perform_request(
        'POST', 
        '/_plugins/_ml/models/_register?deploy=true', 
        body=embedding_model_body
    )
    embedding_task_id = embedding_response['task_id']
    print(f"   Task ID: {embedding_task_id}")
    
    # Wait until the status becomes completed
    print("   ⏳ Waiting for embedding model registration to complete...")
    while True:
        embedding_model_status = client.transport.perform_request(
            method='GET',
            url=f'/_plugins/_ml/tasks/{embedding_task_id}'
        )
        status_state = embedding_model_status['state']
        print(f"      Registration status: {status_state}")
        if status_state == 'COMPLETED':
            embedding_model_id = embedding_model_status['model_id']
            print(f"   ✓ Embedding model registered with ID: {embedding_model_id}")
            break
        time.sleep(10)
    
    # Deploy the embedding model
    print("\n   Deploying embedding model...")
    deploy_body = {
        "deployment_plan": [
            {
                "model_id": embedding_model_id,
                "workers": 1
            }
        ]
    }
    
    try:
        client.transport.perform_request(
            'POST', 
            f'/_plugins/_ml/models/{embedding_model_id}/_deploy', 
            body=deploy_body
        )
    except Exception as e:
        print(f"   ⚠ Error deploying model: {e}")

    # Wait for deployment to complete
    print("   ⏳ Waiting for embedding model deployment...")
    wait_for_model_deployment(client, embedding_model_id)
    print()
    
    # ============================================================================
    # STEP 3: CREATE INGEST PIPELINE AND INDEX
    # ============================================================================
    
    print_color_section("STEP 3: Creating Ingest Pipeline and Product Index", "EXECUTE")
    
    # Create ingest pipeline
    pipeline_body = {
        "description": "A text embedding pipeline for product inventory using HuggingFace model",
        "processors": [
            {
                "text_embedding": {
                    "model_id": embedding_model_id,
                    "field_map": {
                        "name": "name_embedding",
                        "description": "description_embedding"
                    }
                }
            }
        ]
    }
    
    pipeline_id = f"product_inventory_pipeline_{int(time.time())}"
    client.ingest.put_pipeline(id=pipeline_id, body=pipeline_body)
    print(f"   ✓ Ingest pipeline created with ID: {pipeline_id}")
    
    # Create index with vector field for semantic search
    print("   Creating product index with vector fields...")
    index_body = {
        "mappings": {
            "properties": {
                "id": {"type": "integer"},
                "name": {"type": "text"},
                "name_embedding": {
                    "type": "knn_vector",
                    "dimension": 384,
                    "method": {"name": "hnsw", "engine": "lucene"}
                },
                "category": {"type": "keyword"},
                "price": {"type": "float"},
                "stock": {"type": "integer"},
                "rating": {"type": "float"},
                "description": {"type": "text"},
                "description_embedding": {
                    "type": "knn_vector",
                    "dimension": 384,
                    "method": {"name": "hnsw", "engine": "lucene"}
                }
            }
        },
        "settings": {
            "index": {
                "default_pipeline": pipeline_id,
                "knn": "true"
            }
        }
    }
    
    index_name = f"product_inventory_{int(time.time())}"
    client.indices.create(index=index_name, body=index_body)
    print(f"   ✓ Index created with name: {index_name}\n")
    
    # ============================================================================
    # STEP 4: BULK INDEX SAMPLE PRODUCT DATA (50+ Documents)
    # ============================================================================
    
    print_color_section("STEP 4: Bulk Indexing Product Inventory", "EXECUTE")
    
    print(f"   Indexing {len(SAMPLE_PRODUCTS)} product documents...")
    
    bulk_body = []
    for product in SAMPLE_PRODUCTS:
        bulk_body.append({"index": {"_index": index_name, "_id": str(product["id"])}})
        bulk_body.append(product)
    
    client.bulk(body=bulk_body, index=index_name, pipeline=pipeline_id)
    print(f"   ✓ {len(SAMPLE_PRODUCTS)} products indexed successfully\n")
    
    # Wait for indexing to complete and refresh index
    print("   Waiting for index to be ready...")
    time.sleep(5)  # Give time for documents to be indexed
    client.indices.refresh(index=index_name)
    print("   ✓ Index refreshed and ready\n")
    
    # Display sample products
    print("   Sample Products Indexed:")
    for i, product in enumerate(SAMPLE_PRODUCTS[:5]):
        print(f"      {i+1}. {product['name']} - ${product['price']} - Stock: {product['stock']}")
    print(f"      ... and {len(SAMPLE_PRODUCTS) - 5} more products\n")
    
    # ============================================================================
    # STEP 5: CREATE OPENAI CONNECTOR AND MODEL
    # ============================================================================
    
    print_color_section("STEP 5: Creating OpenAI Connector and Model", "EXECUTE")
    
    # Create model group
    model_group_name = f"per_agent_model_group_{int(time.time())}"
    print("   Creating model group...")
    llm_model_group_body = {
        "name": model_group_name,
        "description": "A model group for Plan-Execute-Reflect agent models"
    }
    response = client.transport.perform_request(
        'POST', 
        '/_plugins/_ml/model_groups/_register', 
        body=llm_model_group_body
    )
    llm_model_group_id = response['model_group_id']
    print(f"   ✓ Model group created with ID: {llm_model_group_id}")
    
    # Create OpenAI connector (EXACT SAME AS openai_agent_tools.py)
    print("   Creating OpenAI chat completions connector...")
    llm_connector_body = {
        "name": "OpenAI Chat Connector",
        "description": "The connector to public OpenAI model service for GPT models",
        "version": 1,
        "protocol": "http",
        "parameters": {
            "endpoint": "api.openai.com",
            "model": OPENAI_MODEL
        },
        "credential": {
            "openAI_key": OPENAI_API_KEY
        },
        "actions": [
            {
                "action_type": "predict",
                "method": "POST",
                "url": "https://${parameters.endpoint}/v1/chat/completions",
                "headers": {
                    "Authorization": "Bearer ${credential.openAI_key}",
                    "Content-Type": "application/json"
                },
                "request_body": "{\"model\": \"${parameters.model}\", \"messages\": ${parameters.messages}, \"temperature\": 0.7}"
            }
        ]
    }
    
    response = client.transport.perform_request(
        'POST', 
        '/_plugins/_ml/connectors/_create', 
        body=llm_connector_body
    )
    llm_connector_id = response['connector_id']
    print(f"   ✓ OpenAI connector created with ID: {llm_connector_id}")
    
    # Register the model
    print("   Registering OpenAI model...")
    llm_model_body = {
        "name": f"openai-{OPENAI_MODEL}-per-agent",
        "function_name": "remote",
        "model_group_id": llm_model_group_id,
        "description": f"OpenAI {OPENAI_MODEL} model for Plan-Execute-Reflect agent",
        "connector_id": llm_connector_id
    }
    response = client.transport.perform_request(
        'POST', 
        '/_plugins/_ml/models/_register', 
        body=llm_model_body
    )
    llm_model_id = response['model_id']
    print(f"   ✓ Model registered with ID: {llm_model_id}")
    
    # Deploy the model
    print("   Deploying OpenAI model...")
    llm_deploy_body = {
        "deployment_plan": [
            {
                "model_id": llm_model_id,
                "workers": 1
            }
        ]
    }
    
    try:
        response = client.transport.perform_request(
            'POST', 
            f'/_plugins/_ml/models/{llm_model_id}/_deploy', 
            body=llm_deploy_body
        )
    except Exception as e:
        print(f"   ⚠ Error deploying model: {e}")
    
    print("   ⏳ Waiting for OpenAI model deployment...")
    wait_for_model_deployment(client, llm_model_id)
    print()
    
    # ============================================================================
    # STEP 6: REGISTER PLAN-EXECUTE-REFLECT AGENT
    # ============================================================================
    
    print_color_section("STEP 6: Registering Plan-Execute-Reflect Agent", "PLAN")
    
    print("   The Plan-Execute-Reflect agent architecture:")
    print("   1. PLAN: Agent plans the approach using available tools")
    print("   2. EXECUTE: Agent executes planned steps with tools")
    print("   3. REFLECT: Agent analyzes results and decides on refinements\n")
    
    # Test embedding model works
    print("   Testing embedding model with a sample query...")
    test_search_body = {
        "query": {
            "knn": {
                "name_embedding": {
                    "vector": [0.1] * 384,
                    "k": 3
                }
            }
        }
    }
    try:
        test_result = client.search(index=index_name, body=test_search_body)
        print(f"   ✓ Embedding model test successful - found {len(test_result['hits']['hits'])} products\n")
    except Exception as e:
        print(f"   ⚠ Warning: Embedding model test failed: {e}\n")
    
    # The agent has access to search tools for executing the plan
    agent_register_body = {
        "name": "Plan_Execute_Reflect_Agent",
        "type": "flow",
        "description": "An agent that uses Plan-Execute-Reflect workflow with semantic search",
        "tools": [
            {
                "type": "VectorDBTool",
                "parameters": {
                    "model_id": embedding_model_id,
                    "index": index_name,
                    "embedding_field": "name_embedding",
                    "source_field": [
                        "name",
                        "category",
                        "price",
                        "stock",
                        "rating",
                        "description"
                    ],
                    "input": "${parameters.question}"
                }
            },
            {
                "type": "MLModelTool",
                "description": "A tool using OpenAI GPT for planning, execution coordination, and reflection",
                "parameters": {
                    "model_id": llm_model_id,
                    "messages": "[{\"role\": \"system\", \"content\": \"You are a professional product inventory assistant with Plan-Execute-Reflect capabilities. Your task is to: (1) PLAN: Break down the user question into steps, decide which tools to use. (2) EXECUTE: Use the search results provided. (3) REFLECT: Analyze if you have sufficient information, identify gaps, and provide a comprehensive answer. Always show your thinking process.\"}, {\"role\": \"user\", \"content\": \"Product Search Results:\\n${parameters.VectorDBTool.output}\\n\\nUser Question: ${parameters.question}\"}]"
                }
            }
        ]
    }
    
    agent_response = client.transport.perform_request(
        'POST', 
        '/_plugins/_ml/agents/_register', 
        body=agent_register_body
    )
    agent_id = agent_response['agent_id']
    print(f"   ✓ Agent registered with ID: {agent_id}")
    
    # Inspect the agent
    print("   Inspecting agent configuration...")
    inspect_response = client.transport.perform_request(
        'GET', 
        f'/_plugins/_ml/agents/{agent_id}'
    )
    print(f"   ✓ Agent name: {inspect_response.get('name')}")
    print(f"   ✓ Agent type: {inspect_response.get('type')}")
    print(f"   ✓ Number of tools: {len(inspect_response.get('tools', []))}\n")
    
    # ============================================================================
    # STEP 7: DEMONSTRATE PLAN-EXECUTE-REFLECT WITH SAMPLE QUERIES
    # ============================================================================
    
    print_color_section("STEP 7: Demonstrating Plan-Execute-Reflect Agent", "REFLECT")
    
    # Test questions demonstrating the three phases
    test_scenarios = [
        {
            "question": "What are the best wireless accessories available, and what should a customer consider when choosing between them?",
            "phase": "PLAN-EXECUTE-REFLECT: Product Discovery and Comparison"
        },
        {
            "question": "Find high-rated office furniture items that are currently well-stocked. What are the top recommendations and why?",
            "phase": "PLAN-EXECUTE-REFLECT: Inventory Analysis and Recommendations"
        },
        {
            "question": "What budget-friendly office setup options exist? Provide recommendations for different budget levels.",
            "phase": "PLAN-EXECUTE-REFLECT: Multi-tier Analysis"
        }
    ]
    
    for scenario_idx, scenario in enumerate(test_scenarios, 1):
        question = scenario["question"]
        phase_title = scenario["phase"]
        
        print(f"\n{'-'*80}")
        print(f"Scenario {scenario_idx}: {phase_title}")
        print(f"{'-'*80}\n")
        
        print(f"📋 Question: {question}\n")
        
        execute_body = {
            "parameters": {
                "question": question
            }
        }
        
        try:
            print("🔄 Agent Processing:")
            print("   Phase 1️⃣  PLAN - Analyzing the question and planning approach...")
            print("   Phase 2️⃣  EXECUTE - Running tools and collecting data...")
            print("   Phase 3️⃣  REFLECT - Analyzing results and formulating answer...\n")
            
            execute_response = client.transport.perform_request(
                'POST', 
                f'/_plugins/_ml/agents/{agent_id}/_execute', 
                body=execute_body
            )
            
            # Response format: list of dicts with 'name' and 'result' keys
            answer = None
            
            if isinstance(execute_response, list) and len(execute_response) > 0:
                # Get the MLModelTool result (usually the last item)
                for item in execute_response:
                    if isinstance(item, dict) and item.get('name') == 'MLModelTool':
                        result_str = item.get('result', '')
                        if result_str:
                            try:
                                # Parse the JSON result string
                                result_json = json.loads(result_str)
                                
                                # Try to extract answer from different response formats
                                # Format 1: OpenAI chat completion format (for messages)
                                if 'choices' in result_json:
                                    choices = result_json.get('choices', [])
                                    if choices and len(choices) > 0:
                                        message = choices[0].get('message', {})
                                        answer = message.get('content', '')
                                        break
                                
                                # Format 2: Ollama/text generation format (for prompt)
                                elif 'response' in result_json:
                                    answer = result_json.get('response', '')
                                    break
                                
                                # Format 3: Direct output field
                                elif 'output' in result_json:
                                    answer = result_json.get('output', '')
                                    break
                                    
                            except json.JSONDecodeError:
                                answer = result_str
                                break
            
            if answer and str(answer).strip():
                print(f"✅ Agent Response:\n")
                print(answer)
                print()
                
                # Display in Markdown format if in Jupyter notebook
                if JUPYTER_AVAILABLE:
                    try:
                        display(Markdown(f"### 🤖 Agent Response\n\n{answer}"))
                    except Exception as e:
                        pass  # Silently fail if not in Jupyter context
            else:
                print(f"Response (raw): {json.dumps(execute_response, indent=4)}")
                
        except Exception as e:
            import traceback
            print(f"   ⚠ Error executing agent: {e}")
            print(f"\n   Full error traceback:\n{traceback.format_exc()}")
    
    # ============================================================================
    # FINAL SUMMARY
    # ============================================================================
    
    print("\n" + "="*80)
    print("✓ Plan-Execute-Reflect Agent Demo Completed Successfully!")
    print("="*80 + "\n")
    
    print("""
╔════════════════════════════════════════════════════════════════════════════╗
║                         LEARNING SUMMARY                                   ║
╠════════════════════════════════════════════════════════════════════════════╣
║                                                                             ║
║  KEY CONCEPTS:                                                              ║
║                                                                             ║
║  1. PLANNING PHASE:                                                         ║
║     • Agent analyzes the complex question                                   ║
║     • Breaks it into actionable sub-tasks                                   ║
║     • Selects appropriate tools                                             ║
║     • LLM call count: 1-2                                                   ║
║                                                                             ║
║  2. EXECUTION PHASE:                                                        ║
║     • Agent runs selected tools sequentially                                ║
║     • Collects results from VectorDB and other tools                        ║
║     • Handles tool-specific logic and errors                                ║
║     • Tool call count: Variable (1-N)                                       ║
║                                                                             ║
║  3. REFLECTION PHASE:                                                       ║
║     • Agent evaluates if results answer the question                        ║
║     • Identifies information gaps                                           ║
║     • Decides: Success or try again with refined plan                       ║
║     • LLM call count: 1-2                                                   ║
║                                                                             ║
║  ADVANTAGES:                                                                ║
║     ✓ Better accuracy through structured thinking                           ║
║     ✓ Self-correction and refinement capability                             ║
║     ✓ Transparent decision-making process                                   ║
║     ✓ Reduced hallucinations through validation                             ║
║     ✓ Handles complex, multi-step problems effectively                      ║
║                                                                             ║
║  WHEN TO USE:                                                               ║
║     • Complex, multi-faceted questions                                      ║
║     • Analysis requiring multiple data sources                              ║
║     • Comparisons and recommendations                                       ║
║     • Questions needing validation/verification                             ║
║     • Tasks requiring iterative refinement                                  ║
║                                                                             ║
╚════════════════════════════════════════════════════════════════════════════╝
    """)
    
    # Print summary of created resources
    print("\nSummary of Created Resources:")
    print(f"  • Embedding Model ID: {embedding_model_id}")
    print(f"  • OpenAI Model ID: {llm_model_id}")
    print(f"  • OpenAI Connector ID: {llm_connector_id}")
    print(f"  • Agent ID: {agent_id}")
    print(f"  • Index Name: {index_name}")
    print(f"  • Pipeline ID: {pipeline_id}")
    print(f"  • Product Documents Indexed: {len(SAMPLE_PRODUCTS)}\n")


# ================================================================================
# SCRIPT ENTRY POINT
# ================================================================================

if __name__ == "__main__":
    main()
