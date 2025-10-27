# Quick Start Guide

This is a quick reference for getting started with the Search-as-you-Type application.

## Prerequisites Checklist

- [ ] Python 3.10+ installed
- [ ] uv package manager installed
- [ ] OpenSearch running (port 9200)
- [ ] ecommerce index loaded with data
- [ ] Node.js 18+ (only for React frontend)

## 5-Minute Quick Start

### 1. Setup (First time only)

```bash
# Navigate to project directory
cd search_as_you_type

# Create virtual environment and install dependencies
uv venv
source .venv/bin/activate
uv pip install -e .

# Create environment file
cp .env.example .env
```

### 2. Start Backend

```bash
python -m uvicorn backend.main:app --reload --port 8000
```

Backend is ready when you see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### 3. Start Frontend (Choose One)

**Option A: Streamlit** (Recommended for quick start)
```bash
streamlit run streamlit_app.py --server.address 0.0.0.0 --server.port 8501
```
Open: http://localhost:8501 or http://0.0.0.0:8501

**Option B: Gradio**
```bash
python gradio_app.py
```
Open: http://localhost:7860 or http://0.0.0.0:7860

**Option C: React** (Requires npm install first)
```bash
cd react-frontend
npm install  # First time only
HOST=0.0.0.0 npm start
```
Open: http://localhost:3000 or http://0.0.0.0:3000

## Common Commands

### View API Documentation
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Check Health
```bash
curl http://localhost:8000/api/health
```

### Test Search API
```bash
curl -X POST http://localhost:8000/api/search \
  -H "Content-Type: application/json" \
  -d '{
    "query": "shirt",
    "fields": ["products.product_name"],
    "size": 5
  }'
```

### Run Examples
```bash
python examples.py
```

### Stop All Services
```bash
# Stop all running services (backend and frontends)
./stop.sh
```

## Troubleshooting Quick Fixes

### Port already in use
```bash
# Stop all services
./stop.sh
```

### Backend won't start
```bash
# Check OpenSearch
curl -k -u admin:Developer@123 https://localhost:9200

# Reinstall dependencies
uv pip install -e .
```

### Frontend connection error
1. Ensure backend is running on port 8000
2. Check .env configuration
3. Verify CORS settings in backend/main.py

### No search results
```bash
# Verify index has data
curl -k -u admin:Developer@123 https://localhost:9200/ecommerce/_count
```

## Next Steps

1. Read the full [README.md](README.md) for detailed information
2. Explore [ARCHITECTURE.md](ARCHITECTURE.md) for system design
3. Try example searches (see README.md)
4. Customize search fields and behavior

## Support

For issues, check:
- README.md Troubleshooting section
- Backend logs: `logs/backend.log`
- OpenSearch logs: `docker logs opensearch-node1`
