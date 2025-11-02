# 🚀 Quick Start Guide

## 5-Minute Setup

### Step 1: Install Dependencies (1 min)
```bash
cd "5. business_intelligence_app"
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Step 2: Configure .env (1 min)
Edit `.env` and add your credentials:
```properties
DEEPSEEK_API_KEY=your_actual_api_key_here
POSTGRES_HOST=localhost
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_password
POSTGRES_DB=Adventureworks
```

### Step 3: Verify Prerequisites (1 min)
```bash
# Check PostgreSQL is running
psql -h localhost -U postgres -d Adventureworks -c "SELECT 1"

# Check OpenSearch is running
curl -k -u admin:Developer@123 https://localhost:9200
```

### Step 4: Launch App (1 min)
```bash
python app.py
```

Open browser: http://localhost:7860

### Step 5: Follow UI Workflow (1 min to understand)
1. **Tab 1**: Connect to Database & Setup OpenSearch
2. **Tab 2**: Extract Metadata
3. **Tab 3**: Enhance with AI (takes time - optional for first test)
4. **Tab 4**: Download metadata (optional)
5. **Tab 5**: Ingest to OpenSearch (required)
6. **Tab 6**: Ask your question
7. **Tab 7**: Execute SQL
8. **Tab 8**: Visualize results
9. **Tab 9**: Get business insights

---

## First Test Query (Fast Options)

### Option 1: Use Previously Generated Metadata (Fastest!)
If you have metadata from a previous run:

1. Complete Tabs 1-2 (Setup & Extract)
2. At **Tab 3**: Click "Choose File" and upload your saved `metadata_*.xlsx`
3. Click "Upload and Load" (takes 2 seconds!)
4. Skip to Tab 5 and continue

### Option 2: Skip AI Enhancement (Quick Test)
If you want to test quickly without waiting for AI enhancement:

1. Complete Tabs 1-2 (Setup & Extract)
2. **Skip Tab 3** (or run it in background later)
3. At Tab 5, use basic metadata (without AI descriptions)
4. Proceed to Tab 6 and ask: "Show me all tables"

This works with basic metadata, though SQL quality improves with AI descriptions.

---

## Example Questions to Try

After completing all steps:

```
"What are the top 10 products by sales revenue?"
"Show me customer segmentation by order frequency"
"Which product categories have the highest profit margins?"
"List all employees with their departments and salaries"
"What is the average order value by month?"
```

---

## Troubleshooting

**App won't start**: Check Python version (3.8+)
```bash
python --version
```

**Can't connect to DB**: Verify credentials
```bash
psql -h localhost -U postgres -l
```

**OpenSearch error**: Check if running
```bash
sudo systemctl status opensearch
```

**API key error**: Get key from https://platform.deepseek.com

---

## Full Documentation

See [README.md](README.md) for:
- Complete workflow guide
- Detailed troubleshooting
- API information
- Architecture details
- Example walkthroughs

---

## Support

Check logs in terminal where app is running for detailed error messages.
