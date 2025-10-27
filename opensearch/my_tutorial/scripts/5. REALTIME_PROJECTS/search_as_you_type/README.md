# 🔍 Search-as-you-Type E-commerce Application

A comprehensive, production-ready search-as-you-type application demonstrating real-time product search with multiple frontend implementations (Streamlit, Gradio, React) and a FastAPI backend powered by OpenSearch.

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Architecture](#architecture)
- [Technology Stack](#technology-stack)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Running the Applications](#running-the-applications)
- [API Documentation](#api-documentation)
- [Search Fields](#search-fields)
- [Project Structure](#project-structure)
- [Architecture Diagrams](#architecture-diagrams)
- [Development](#development)
- [Troubleshooting](#troubleshooting)
- [License](#license)

## 🌟 Overview

This project demonstrates a modern search-as-you-type implementation for e-commerce product search with:

- **Multiple Frontend Options**: Choose from Streamlit, Gradio, or React based on your needs
- **Powerful Backend**: FastAPI-based REST API with OpenSearch integration
- **Advanced Search Features**: Phrase prefix matching, fuzzy search, phrase matching with highlighting
- **Real-time Results**: Sub-100ms search response times
- **Production-Ready**: Type-safe code, error handling, health checks, and comprehensive documentation

## ✨ Features

### Search Capabilities

- **🔤 Phrase Prefix Matching**: Autocomplete as you type (e.g., "boo" → "boots")
- **🔧 Fuzzy Matching**: Tolerates typos and spelling mistakes (e.g., "shrt" → "shirt")
- **📝 Phrase Matching**: Finds exact phrases with flexibility
- **🎨 Result Highlighting**: Matched terms highlighted in results
- **⚡ Real-time Updates**: Results update as you type
- **🎯 Multi-field Search**: Search across product names, categories, and manufacturers

### Frontend Options

1. **Streamlit** (`streamlit_app.py`)
   - Python-based UI
   - Great for data science applications
   - Rapid prototyping
   - Port: 8501

2. **Gradio** (`gradio_app.py`)
   - ML model demonstration UI
   - Easy sharing capabilities
   - Interactive widgets
   - Port: 7860

3. **React** (`react-frontend/`)
   - Modern single-page application
   - Responsive design
   - Production-ready
   - Port: 3000

### Backend Features

- **RESTful API**: Clean, well-documented endpoints
- **Auto Documentation**: Swagger UI and ReDoc
- **Type Safety**: Pydantic models for request/response validation
- **CORS Support**: Cross-origin resource sharing enabled
- **Health Checks**: Monitor API and OpenSearch cluster health
- **Error Handling**: Comprehensive error responses

## 🏗️ Architecture

The application follows a modern three-tier architecture:

```
┌─────────────────────────────────────────────┐
│         Frontend Layer (Port 3000)          │
│  Streamlit (8501) | Gradio (7860) | React   │
└─────────────────────┬───────────────────────┘
                      │ HTTP/REST
┌─────────────────────▼───────────────────────┐
│         Backend Layer (Port 8000)           │
│            FastAPI + Uvicorn                │
│  • Search API  • Suggestions  • Health      │
└─────────────────────┬───────────────────────┘
                      │ OpenSearch Protocol
┌─────────────────────▼───────────────────────┐
│         Data Layer (Port 9200)              │
│          OpenSearch Cluster                 │
│      • ecommerce index (9000+ docs)         │
└─────────────────────────────────────────────┘
```

For detailed architecture diagrams, see [ARCHITECTURE.md](ARCHITECTURE.md).

## 🛠️ Technology Stack

### Backend
- **FastAPI**: Modern, fast web framework for building APIs
- **OpenSearch Python Client**: Official OpenSearch SDK
- **Pydantic**: Data validation using Python type annotations
- **Uvicorn**: Lightning-fast ASGI server

### Frontend
- **Streamlit**: Python-based app framework for ML/data science
- **Gradio**: UI library for ML model demos
- **React**: JavaScript library for building user interfaces
- **Axios**: Promise-based HTTP client

### Package Management
- **uv**: Fast Python package installer and resolver

### Search Engine
- **OpenSearch**: Open-source search and analytics engine

## 📦 Prerequisites

Before installation, ensure you have:

1. **Python 3.10+** installed
2. **Node.js 18+** and **npm** (for React frontend)
3. **uv** package manager installed:
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```
4. **OpenSearch** cluster running with the `ecommerce` index loaded
5. **Docker** (optional, for running OpenSearch)

## 🚀 Installation

### 1. Clone the Repository

```bash
cd /home/ubuntu/git-projects/personal/github.com/elasticsearch_opensearch/opensearch/my_tutorial/scripts/5.\ REALTIME_PROJECTS/search_as_you_type/
```

### 2. Set Up Python Environment

```bash
# Create virtual environment and install dependencies using uv
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install all dependencies
uv pip install -e .
```

### 3. Set Up React Frontend (Optional)

```bash
cd react-frontend
npm install
cd ..
```

### 4. Start OpenSearch (if not already running)

Using the provided Docker Compose file:

```bash
cd ..
docker-compose -f 1.\ docker-compose-load-ecommerce.yml up -d
cd search_as_you_type
```

Wait for OpenSearch to be healthy (check http://localhost:9200).

## ⚙️ Configuration

### 1. Create Environment File

Copy the example environment file and customize:

```bash
cp .env.example .env
```

### 2. Edit Configuration

Edit `.env` file with your settings:

```env
# OpenSearch Configuration
OPENSEARCH_HOST=https://localhost:9200
OPENSEARCH_USERNAME=admin
OPENSEARCH_PASSWORD=Developer@123
OPENSEARCH_INDEX=ecommerce
OPENSEARCH_VERIFY_SSL=false

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000

# Frontend Configuration
API_BASE_URL=http://127.0.0.1:8000  # Backend API URL for frontends
STREAMLIT_PORT=8501
GRADIO_PORT=7860
```

**Important Notes:**
- The backend listens on `0.0.0.0:8000` (all network interfaces)
- Frontends connect to backend via `API_BASE_URL` (defaults to `http://127.0.0.1:8000`)
- Use `127.0.0.1` instead of `localhost` to avoid IPv6 resolution issues
- Streamlit usage statistics collection is disabled via `.streamlit/config.toml`

## 🎯 Running the Applications

### Start the Backend (Required)

The backend API must be running for all frontends to work:

```bash
# Option 1: Using Python module
python -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000

# Option 2: Using the main script
python backend/main.py
```

Backend will be available at: http://localhost:8000
- API Documentation: http://localhost:8000/docs
- Alternative Docs: http://localhost:8000/redoc

### Start Frontend (Choose One or All)

#### Option 1: Streamlit

```bash
streamlit run streamlit_app.py --server.address 0.0.0.0 --server.port 8501
```

Access at: http://localhost:8501 (or http://0.0.0.0:8501)

#### Option 2: Gradio

```bash
python gradio_app.py
```

Access at: http://localhost:7860 (or http://0.0.0.0:7860)

#### Option 3: React

```bash
cd react-frontend
HOST=0.0.0.0 npm start
```

Access at: http://localhost:3000 (or http://0.0.0.0:3000)

### Stop All Services

To stop all running services (backend and all frontends):

```bash
./stop.sh
```

This script will gracefully stop:
- FastAPI backend (port 8000)
- Streamlit (port 8501)
- Gradio (port 7860)
- React (port 3000)

## 📚 API Documentation

### Endpoints

#### 1. Search Products

**POST** `/api/search`

Search for products with real-time autocomplete.

**Request Body:**
```json
{
  "query": "shirt",
  "fields": [
    "products.product_name",
    "products.category",
    "products.manufacturer"
  ],
  "size": 10,
  "from": 0
}
```

**Response:**
```json
{
  "total": 150,
  "took": 45,
  "hits": [
    {
      "id": "123",
      "score": 8.5,
      "source": {
        "products": [{
          "product_name": "Basic T-shirt - dark blue/white",
          "category": "Men's Clothing",
          "manufacturer": "Elitelligence",
          "price": 11.99
        }]
      },
      "highlight": {
        "products.product_name": ["Basic T-<mark>shirt</mark> - dark blue/white"]
      }
    }
  ],
  "query": "shirt"
}
```

#### 2. Get Suggestions

**POST** `/api/suggestions`

Get autocomplete suggestions for a field.

**Request Body:**
```json
{
  "query": "boo",
  "field": "products.product_name",
  "size": 5
}
```

**Response:**
```json
{
  "suggestions": [
    "Boots - black",
    "Boots - Midnight Blue",
    "Winter boots - brown",
    "Cowboy/Biker boots - black",
    "Lace-up boots - black"
  ],
  "query": "boo"
}
```

#### 3. Health Check

**GET** `/api/health`

Check API and OpenSearch cluster health.

**Response:**
```json
{
  "status": "healthy",
  "cluster_status": "green",
  "number_of_nodes": 1
}
```

#### 4. Get Search Fields

**GET** `/api/search-fields`

Get available search fields and metadata.

## 🔍 Search Fields

The application searches across the following fields from the ecommerce index:

### Primary Fields

1. **products.product_name**
   - Type: `text` with `keyword` subfield
   - Analyzer: `english`
   - Example: "Basic T-shirt - dark blue/white"
   - Best for: Product name searches

2. **products.category**
   - Type: `text` with `keyword` subfield
   - Example: "Men's Clothing", "Women's Shoes"
   - Best for: Category-based searches

3. **products.manufacturer**
   - Type: `text` with `keyword` subfield
   - Example: "Elitelligence", "Oceanavigations"
   - Best for: Brand searches

### Additional Searchable Fields

4. **customer_full_name**
   - Type: `text` with `keyword` subfield
   - Example: "Eddie Underwood"

5. **category** (order-level)
   - Type: `text` with `keyword` subfield
   - Example: ["Men's Clothing"]

### Field Mapping Details

For complete field mappings, see:
- Source file: `../../../data/ecommerce-field_mappings.json`
- Sample data: `../../../data/ecommerce.json` (9000+ documents)

## 📁 Project Structure

```
search_as_you_type/
├── backend/                      # FastAPI backend
│   ├── __init__.py
│   ├── main.py                   # Main FastAPI application
│   ├── config.py                 # Configuration settings
│   ├── models.py                 # Pydantic models
│   └── opensearch_client.py     # OpenSearch client wrapper
├── react-frontend/               # React frontend application
│   ├── public/
│   │   └── index.html
│   ├── src/
│   │   ├── components/
│   │   │   ├── SearchResults.js
│   │   │   └── Sidebar.js
│   │   ├── App.js
│   │   ├── App.css
│   │   ├── index.js
│   │   └── index.css
│   ├── package.json
│   └── .env                      # React environment config
├── .streamlit/                   # Streamlit configuration
│   └── config.toml               # Server settings (0.0.0.0, no telemetry)
├── streamlit_app.py              # Streamlit frontend
├── gradio_app.py                 # Gradio frontend
├── examples.py                   # API usage examples
├── pyproject.toml                # Python project configuration (uv)
├── .env.example                  # Environment variables template
├── .gitignore                    # Git ignore rules
├── start.sh                      # Startup script (starts backend)
├── stop.sh                       # Stop script (stops all services)
├── README.md                     # This file
├── ARCHITECTURE.md               # Architecture diagrams
├── QUICKSTART.md                 # Quick start guide
├── PROJECT_SUMMARY.md            # Project summary
├── FRONTEND_COMPARISON.md        # Frontend comparison guide
├── NETWORK_CONFIG.md             # Network configuration docs
└── logs/                         # Application logs
    └── .gitkeep

Related files (parent directory):
├── 1. docker-compose-load-ecommerce.yml  # Docker setup
├── ecommerce_load_script.sh              # Data loading script
└── ../../../data/
    ├── ecommerce.json                    # Sample data (9000+ docs)
    └── ecommerce-field_mappings.json     # Index mappings
```

## 📊 Architecture Diagrams

Comprehensive Mermaid diagrams are available in [ARCHITECTURE.md](ARCHITECTURE.md):

1. **Business User Workflow**: High-level user journey
2. **Technical Architecture**: System components and interactions
3. **Search Flow**: Detailed request/response flow
4. **Data Flow**: Data transformation pipeline
5. **Deployment Architecture**: Infrastructure and deployment
6. **Component Interaction Matrix**: Technology stack overview

## 👨‍💻 Development

### Running in Development Mode

```bash
# Backend with auto-reload
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000

# Streamlit with auto-reload (listens on all interfaces)
streamlit run streamlit_app.py --server.address 0.0.0.0 --server.port 8501

# Gradio (already listens on 0.0.0.0)
python gradio_app.py

# React with hot-reload (listens on all interfaces)
cd react-frontend && HOST=0.0.0.0 npm start
```

### Code Quality

```bash
# Format code with black
black backend/ streamlit_app.py gradio_app.py

# Lint with ruff
ruff check backend/ streamlit_app.py gradio_app.py
```

### Adding New Features

1. **New Search Field**: 
   - Update `opensearch_client.py` search query
   - Add field to `get_search_fields()` endpoint
   - Update frontend field selectors

2. **New Frontend**:
   - Create new app file (e.g., `flask_app.py`)
   - Follow same API call patterns
   - Update documentation

## 🔧 Troubleshooting

### Common Issues

#### 1. Backend won't start

```bash
# Check OpenSearch is running
curl -k -u admin:Developer@123 https://localhost:9200

# Check Python dependencies
uv pip list

# Verify environment variables
cat .env

# Stop any existing processes
./stop.sh
```

#### 2. No search results

```bash
# Verify index exists and has data
curl -k -u admin:Developer@123 https://localhost:9200/ecommerce/_count

# Check index mappings
curl -k -u admin:Developer@123 https://localhost:9200/ecommerce/_mapping
```

#### 3. CORS errors (React)

- Ensure backend is running on port 8000
- Check CORS middleware in `backend/main.py`
- Verify proxy setting in `react-frontend/package.json`

#### 4. Import errors

```bash
# Reinstall dependencies
uv pip install -e .

# For React
cd react-frontend && npm install
```

#### 5. Port already in use

If you see errors like "Address already in use":

```bash
# Stop all services
./stop.sh

# Or manually check and kill processes on specific ports
lsof -ti:8000  # Backend
lsof -ti:8501  # Streamlit
lsof -ti:7860  # Gradio
lsof -ti:3000  # React

# Kill specific port (replace PORT with actual port number)
kill -9 $(lsof -ti:PORT)
```

### Performance Optimization

1. **Increase OpenSearch heap**: Edit `docker-compose-load-ecommerce.yml`
   ```yaml
   OPENSEARCH_JAVA_OPTS: "-Xms8192m -Xmx8192m"
   ```

2. **Reduce search size**: Lower `num_results` in frontend

3. **Add caching**: Implement Redis for frequent queries

## 📖 Example Searches

Try these searches to test the application:

### Product Names
- `shirt` - Find all shirts
- `boot` - Find boots (tests autocomplete)
- `jacket` - Winter jackets
- `dress` - Women's dresses

### Categories
- `Men's Clothing`
- `Women's Shoes`
- `Accessories`

### Manufacturers
- `Elitelligence`
- `Oceanavigations`
- `Pyramidustries`

### Partial/Fuzzy Searches
- `swe` → sweatshirt
- `boo` → boots
- `jakt` → jacket (typo tolerance)

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is part of an OpenSearch tutorial and is available for educational purposes.

## 🙏 Acknowledgments

- OpenSearch team for the excellent search engine
- FastAPI team for the amazing web framework
- Streamlit, Gradio, and React communities

---

## 🎓 Learning Resources

### OpenSearch
- [OpenSearch Documentation](https://opensearch.org/docs/latest/)
- [Search API Reference](https://opensearch.org/docs/latest/api-reference/search/)
- [Query DSL](https://opensearch.org/docs/latest/query-dsl/)

### FastAPI
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Pydantic Documentation](https://docs.pydantic.dev/)

### Frontend Frameworks
- [Streamlit Documentation](https://docs.streamlit.io/)
- [Gradio Documentation](https://www.gradio.app/docs/)
- [React Documentation](https://react.dev/)

---

**Built with ❤️ for demonstrating modern search applications**
