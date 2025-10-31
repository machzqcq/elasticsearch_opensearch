# 🚀 Business Intelligence RAG Application

A complete Gradio-based web application that transforms natural language questions into SQL queries, executes them, creates visualizations, and generates business insights using RAG (Retrieval-Augmented Generation).

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Architecture](#architecture)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage Guide](#usage-guide)
- [Workflow Steps](#workflow-steps)
- [Troubleshooting](#troubleshooting)
- [API Information](#api-information)

## 🎯 Overview

This application provides a complete business intelligence workflow:

1. **Extract** database metadata from PostgreSQL
2. **Enhance** metadata with AI-generated descriptions using LLM
3. **Ingest** enhanced metadata into OpenSearch with vector embeddings
4. **Query** your database using natural language questions
5. **Generate** SQL queries automatically using RAG
6. **Execute** SQL queries and view results
7. **Visualize** data with automatic chart generation
8. **Analyze** results with AI-generated business insights

## ✨ Features

### 🔍 Intelligent Metadata Management
- Extract complete database schema (tables, columns, data types)
- AI-powered column and table descriptions
- Downloadable metadata documentation (Excel format)

### 🤖 RAG-Powered Text-to-SQL
- Natural language to SQL conversion
- Hybrid search (keyword + semantic) for relevant metadata
- Context-aware SQL generation using DeepSeek LLM

### 📊 Automatic Visualization
- Intelligent chart type selection
- Interactive Plotly visualizations
- Adapts to different data types

### 💡 Business Intelligence Insights
- AI-generated analysis of query results
- Key findings and trends
- Actionable recommendations
- Suggested next steps

### 🎨 User-Friendly Interface
- Step-by-step guided workflow
- Progress indicators
- Clear status messages
- Built with Gradio for easy interaction

## 🏗️ Architecture

```
┌─────────────────┐
│   User Query    │
│  (Natural Lang) │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   OpenSearch    │◄───── Enhanced Metadata
│  (Vector Store) │        with Embeddings
└────────┬────────┘
         │ Hybrid Search (BM25 + k-NN)
         ▼
┌─────────────────┐
│  DeepSeek LLM   │◄───── Retrieved Metadata Context
│  (SQL Gen)      │
└────────┬────────┘
         │ Generated SQL
         ▼
┌─────────────────┐
│   PostgreSQL    │
│   (Database)    │
└────────┬────────┘
         │ Query Results
         ▼
┌─────────────────┐
│  Visualization  │
│   & Insights    │
└─────────────────┘
```

## 📦 Prerequisites

### Required Software
- Python 3.8 or higher
- PostgreSQL database (running and accessible)
- OpenSearch 2.x (running locally or remote)
- DeepSeek API key (or other LLM provider)

### System Requirements
- 4GB RAM minimum (8GB recommended)
- Internet connection (for LLM API calls)

## 🔧 Installation

### 1. Clone or Navigate to the Directory

```bash
cd /path/to/5.\ business_intelligence_app
```

### 2. Create Virtual Environment (Recommended)

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Verify OpenSearch is Running

```bash
curl -k -u admin:Developer@123 https://localhost:9200
```

Expected response: JSON with cluster information

## ⚙️ Configuration

### 1. Edit .env File

The `.env` file contains all configuration:

```properties
# LLM API Keys
DEEPSEEK_API_KEY=your_deepseek_api_key_here
OPENAI_API_KEY=your_openai_key_optional
GOOGLE_API_KEY=your_google_key_optional
ANTHROPIC_API_KEY=your_anthropic_key_optional

# PostgreSQL Connection
POSTGRES_HOST=localhost
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_PORT=5432
POSTGRES_DB=Adventureworks

# OpenSearch (defaults in code, can override here)
# OPENSEARCH_HOST=localhost
# OPENSEARCH_PORT=9200
# OPENSEARCH_USERNAME=admin
# OPENSEARCH_PASSWORD=Developer@123
```

### 2. Database Setup

Ensure your PostgreSQL database:
- Is running and accessible
- Has tables with data
- User has read permissions
- Network access is allowed (if remote)

### 3. OpenSearch Setup

Ensure OpenSearch:
- Is running (check with curl command above)
- Has ML Commons plugin enabled
- Accepts the configured credentials
- Has sufficient disk space for embeddings

## 📖 Usage Guide

### Starting the Application

```bash
python app.py
```

The application will start on `http://localhost:7860`

Open your browser and navigate to the URL.

## 🔄 Workflow Steps

### Tab 1: 🔌 Setup & Connect

**Purpose**: Establish connections to database and OpenSearch

**Steps**:
1. Click "Connect to Database"
   - Connects to PostgreSQL using credentials from .env
   - Verifies connection is successful
   - Wait for ✅ success message

2. Click "Setup OpenSearch"
   - Initializes OpenSearch client
   - Configures cluster settings
   - Registers embedding model (sentence-transformers/all-MiniLM-L12-v2)
   - Deploys model for use
   - Wait for ✅ success message

**Expected Time**: 30-60 seconds

**Troubleshooting**:
- Database connection fails → Check credentials in .env
- OpenSearch setup fails → Verify OpenSearch is running
- Model deployment fails → Check OpenSearch has ML Commons plugin

---

### Tab 2: 📊 Extract Metadata

**Purpose**: Extract database schema information

**Steps**:
1. Click "Extract Metadata"
   - Queries information_schema tables
   - Retrieves all table and column information
   - Excludes system schemas (information_schema, pg_catalog)
   - Creates unique IDs for each column

2. Review the preview
   - Shows first 20 rows of metadata
   - Includes: schema, table, column, data type, nullability, etc.

**Expected Time**: 5-10 seconds

**What You'll See**:
- Message: "✅ Extracted metadata: X columns from Y tables"
- Preview table with columns:
  - table_schema
  - table_name
  - column_name
  - data_type
  - is_nullable
  - character_maximum_length
  - etc.

---

### Tab 3: 🤖 Enhance with AI

**Purpose**: Add AI-generated descriptions to make metadata meaningful

**Two Options Available**:

---

#### Option A: Generate Fresh AI Descriptions (Takes Time)

**Use when**: First time running, or want to regenerate descriptions

**Steps**:

##### Part A: Enhance Column Descriptions
1. Click "Enhance Column Descriptions"
   - For EACH column, the system:
     - Samples 10 random values from the database
     - Sends samples to DeepSeek LLM
     - Generates a concise description (max 40 words)
     - Adds description to metadata

2. Monitor progress
   - Progress bar shows completion percentage
   - Status shows current column being processed

**Expected Time**: 5-10 minutes (depends on number of columns and API speed)

##### Part B: Add Table Descriptions
1. Click "Add Table Descriptions"
   - For EACH table, the system:
     - Samples 5 random rows
     - Analyzes table structure
     - Sends to LLM for description
     - Generates business-purpose description (max 60 words)

2. Review enhanced metadata
   - Now includes both column and table descriptions

**Expected Time**: 2-5 minutes (depends on number of tables)

**Cost Consideration**: 
- These steps make multiple API calls
- DeepSeek pricing: ~$0.14 per million input tokens, ~$0.28 per million output tokens
- For a 100-column database: ~$0.50-$2.00

**What Descriptions Look Like**:
- Column: "Unique identifier for customer records, automatically generated integer primary key"
- Table: "Stores customer master data including contact information, demographics, and account status for CRM operations"

---

#### Option B: Upload Previously Generated Metadata (Fast - RECOMMENDED for repeat use!)

**Use when**: You already have enhanced metadata from a previous run

**Steps**:
1. Click "Choose File" under "Upload Metadata Excel File"
2. Select your previously saved metadata file (e.g., `metadata_Adventureworks.xlsx`)
3. Click "Upload and Load"

**What happens**:
- Reads the Excel file
- Validates it has required columns
- Loads metadata into memory
- Detects if it has AI descriptions
- Shows preview

**Expected Time**: 2-5 seconds

**Advantages**:
- ✅ Instant loading (no API calls)
- ✅ Zero cost (no LLM usage)
- ✅ Perfect for testing or repeat runs
- ✅ Same quality as freshly generated

**File Requirements**:
- Must be Excel format (.xlsx or .xls)
- Must have columns: table_schema, table_name, column_name, data_type
- Ideally has: inferred_column_description, inferred_table_description
- Can be the file downloaded from Tab 4 in previous run

**Tip**: After your first complete run, always use Option B to save time and money!

---

### Tab 4: 💾 Download

**Purpose**: Save enhanced metadata as documentation

**Steps**:
1. Click "Download Metadata as Excel"
   - Creates .xlsx file with all metadata
   - Includes all AI-generated descriptions
   - Formatted for easy reading

2. Save the file
   - Filename: `metadata_[database_name].xlsx`
   - Sheet name: "Enhanced_Metadata"

**Uses for Downloaded File**:
- Database documentation
- Team onboarding
- Schema reference
- Backup before changes

---

### Tab 5: 🔄 Ingest to OpenSearch

**Purpose**: Enable semantic search over metadata

**Steps**:
1. Click "Ingest to OpenSearch"
   
   **What happens**:
   - Creates embedding pipeline
     - Configures text_embedding processor
     - Maps text fields to embedding fields
   
   - Creates index with mappings
     - Defines field types
     - Creates knn_vector fields (384 dimensions)
     - Sets default pipeline
   
   - Ingests documents
     - Sends metadata in batches
     - Pipeline automatically generates embeddings
     - Each text field gets corresponding _embedding field
   
   - Refreshes index for searching

2. Monitor progress
   - Status updates show each step
   - Final message shows document count

**Expected Time**: 5-15 minutes (depends on dataset size)

**What Gets Indexed**:
- All metadata fields
- Plus vector embeddings for:
  - full_column_name
  - inferred_column_description
  - inferred_table_description
  - table_name

**Why This Matters**:
- Enables semantic search ("find tables about customers" works!)
- Hybrid search (keyword + meaning) finds best matches
- Critical for accurate SQL generation

---

### Tab 6: 🎯 Ask Questions

**Purpose**: Convert natural language questions to SQL

**Steps**:
1. Enter your business question
   
   **Example Questions**:
   - "What are the top 10 products by sales revenue?"
   - "Show me customer segmentation by order frequency"
   - "Which product categories have the highest profit margins?"
   - "List employees by department with their salaries"
   - "Compare monthly sales trends for the last year"

2. Click "Generate SQL"
   
   **What happens**:
   - Query sent to OpenSearch
   - Hybrid search retrieves top 10 relevant metadata entries
   - Metadata formatted as context
   - Sent to DeepSeek LLM with prompt
   - LLM generates PostgreSQL query
   - SQL cleaned and formatted

3. Review generated SQL
   - Check table names are correct
   - Verify JOINs make sense
   - Ensure columns exist

**Expected Time**: 5-10 seconds

**Tips for Better Results**:
- Be specific (not "show sales" but "show total sales by product category")
- Use business terms from your domain
- Mention time periods if relevant
- Specify sorting/limits if wanted

**Example Flow**:
```
Question: "Who are my top 5 customers by total order value?"

Retrieved Metadata:
- sales.salesorderheader table (description, columns)
- sales.customer table (description, columns)
- Relevant columns: customerid, totaldue, etc.

Generated SQL:
SELECT 
    c.customerid,
    c.firstname || ' ' || c.lastname as customer_name,
    SUM(soh.totaldue) as total_order_value
FROM sales.customer c
JOIN sales.salesorderheader soh ON c.customerid = soh.customerid
GROUP BY c.customerid, customer_name
ORDER BY total_order_value DESC
LIMIT 5;
```

---

### Tab 7: ▶️ Execute Query

**Purpose**: Run the SQL query and get results

**Steps**:
1. Review the SQL query
   - Automatically populated from previous tab
   - Edit if needed

2. Click "Execute SQL"
   - Runs query on PostgreSQL
   - Returns results as DataFrame
   - Performs statistical analysis

3. View results
   - **Query Results**: First 50 rows displayed
   - **Statistical Analysis**: 
     - Dataset overview (rows, columns)
     - Numeric column statistics (mean, std, min, max)
     - Categorical column info (unique values)

**Expected Time**: 1-30 seconds (depends on query complexity)

**What Analysis Shows**:
```
Dataset Overview
- Rows: 238
- Columns: 4
- Column Names: productid, name, category, total_sales

Numeric Columns (2)
- productid: mean=119.50, std=68.79, min=1.00, max=238.00
- total_sales: mean=25847.38, std=15234.67, min=450.00, max=95837.22

Categorical Columns (2)
- name: 238 unique values
- category: 4 unique values
```

---

### Tab 8: 📊 Visualize

**Purpose**: Create visualizations from query results

**Steps**:
1. Click "Create Visualization"
   
   **Automatic Chart Selection**:
   - 2+ numeric columns → Scatter plot
   - 1 numeric + 1 categorical → Bar chart
   - 1 numeric only → Histogram
   - Categorical only → Value counts bar chart

2. Interact with visualization
   - Hover for values
   - Zoom and pan
   - Download as image

**Example Visualizations**:
- Sales by product category: Bar chart
- Revenue vs. profit margin: Scatter plot
- Order count distribution: Histogram
- Customer segmentation: Grouped bar chart

**Expected Time**: 2-5 seconds

---

### Tab 9: 🧠 Business Insights

**Purpose**: Get AI-powered analysis and recommendations

**Steps**:
1. Click "Generate Business Insights"
   
   **What the AI analyzes**:
   - Original question
   - SQL query used
   - Statistical analysis
   - Actual data (first 5 rows)
   - Data patterns and trends

2. Read the comprehensive report
   
   **Report Sections**:
   - **🔍 Key Findings**: Main insights from the data
   - **📈 Trends**: Patterns and trends observed
   - **💡 Recommendations**: Actionable business advice
   - **🎯 Next Steps**: Suggested follow-up analysis

**Expected Time**: 10-20 seconds

**Example Insights**:

For question: "Top 10 products by revenue"

```markdown
## 🔍 Key Findings

- Product "Mountain-200 Black, 46" leads with $1.2M in revenue
- Top 10 products account for 35% of total revenue
- Mountain bikes category dominates with 7 out of top 10
- Average selling price in top 10: $2,385

## 📈 Trends

- Premium products (>$2000) generate higher total revenue
- Black color variants outsell other colors 2:1
- Larger frame sizes (44-46) preferred in top sellers
- Seasonal spike in Q2 and Q4

## 💡 Recommendations

1. Increase inventory of top-performing SKUs
2. Consider expanding Mountain bike line
3. Focus marketing on black color variants
4. Prepare for Q2/Q4 demand spikes

## 🎯 Next Steps

- Analyze profit margins for top products
- Compare performance across regions
- Investigate why certain sizes sell better
- Review pricing strategy for premium products
```

**Expected Time**: 15-30 seconds

---

### Tab 10: ℹ️ Help & Guide

**Purpose**: Quick reference and troubleshooting

**Contains**:
- Complete workflow summary
- Tips for success
- Example questions
- Troubleshooting guide
- Technical architecture details

---

## 🎯 Complete Example Walkthrough

### Scenario: Analyzing Customer Orders

**Tab 1**: Setup
- ✅ Connected to PostgreSQL (Adventureworks database)
- ✅ Initialized OpenSearch with embedding model

**Tab 2**: Extract Metadata
- ✅ Extracted 850 columns from 68 tables

**Tab 3**: Enhance with AI
- ✅ Generated AI descriptions for all 850 columns (8 minutes)
- ✅ Added table descriptions for all 68 tables (3 minutes)

**Tab 4**: Download
- ✅ Downloaded metadata_Adventureworks.xlsx

**Tab 5**: Ingest to OpenSearch
- ✅ Created embedding pipeline
- ✅ Ingested 850 documents with embeddings (12 minutes)

**Tab 6**: Ask Question
- Question: *"Show me the top 10 customers by total order value, including their contact information"*
- ✅ Generated SQL in 6 seconds

**Tab 7**: Execute
- ✅ Query returned 10 rows with customer names, emails, and total order values
- ✅ Statistical analysis showed order values range from $45K to $287K

**Tab 8**: Visualize
- ✅ Created bar chart showing customer names vs. total order value
- Interactive chart with hover details

**Tab 9**: Insights
- ✅ AI identified VIP customers representing 15% of revenue
- ✅ Recommended personalized retention program
- ✅ Suggested cross-sell opportunities based on order patterns

---

## 🔍 Troubleshooting

### Common Issues and Solutions

#### Issue: "Database connection failed"
**Causes**:
- Wrong credentials in .env
- PostgreSQL not running
- Network/firewall blocking connection
- Wrong host/port

**Solutions**:
```bash
# Check PostgreSQL is running
sudo systemctl status postgresql

# Test connection manually
psql -h localhost -U postgres -d Adventureworks

# Verify .env values match your setup
cat .env | grep POSTGRES
```

#### Issue: "OpenSearch initialization failed"
**Causes**:
- OpenSearch not running
- Wrong credentials
- ML Commons plugin not installed

**Solutions**:
```bash
# Check OpenSearch status
curl -k -u admin:Developer@123 https://localhost:9200

# Check ML Commons plugin
curl -k -u admin:Developer@123 https://localhost:9200/_cat/plugins

# Restart OpenSearch if needed
sudo systemctl restart opensearch
```

#### Issue: "Model registration failed"
**Causes**:
- Insufficient memory
- Network issues downloading model
- ML Commons not configured

**Solutions**:
- Increase OpenSearch heap size (edit jvm.options)
- Check internet connectivity
- Verify ML Commons settings in opensearch.yml

#### Issue: "API Error 401" or "API key invalid"
**Causes**:
- Invalid DeepSeek API key
- API key expired
- API key not set in .env

**Solutions**:
```bash
# Verify API key is set
cat .env | grep DEEPSEEK_API_KEY

# Test API key manually
curl https://api.deepseek.com/v1/models \
  -H "Authorization: Bearer YOUR_KEY"

# Get new API key from https://platform.deepseek.com
```

#### Issue: "No relevant metadata found"
**Causes**:
- Metadata not ingested to OpenSearch
- Index doesn't exist
- Query too vague

**Solutions**:
- Complete Tab 5 (Ingest to OpenSearch) first
- Verify index exists: `curl -k -u admin:Developer@123 https://localhost:9200/_cat/indices`
- Make query more specific

#### Issue: "SQL execution failed"
**Causes**:
- Generated SQL has syntax errors
- Table/column names incorrect
- Permissions insufficient

**Solutions**:
- Review generated SQL for obvious errors
- Try simpler question first
- Check database user has SELECT permissions
- Manually test SQL in database client

#### Issue: "Visualization creation failed"
**Causes**:
- No data to visualize (empty results)
- Data types incompatible
- Column names have special characters

**Solutions**:
- Check Tab 7 shows data
- Ensure query returns numeric data
- Try different query if needed

#### Issue: "Process is slow"
**Causes**:
- Large dataset
- API rate limits
- Insufficient memory

**Solutions**:
- Be patient (LLM calls take time)
- For Tab 3: Process in smaller batches
- Increase system RAM
- Use faster LLM model if available

---

## 🔑 API Information

### DeepSeek API

**Obtaining API Key**:
1. Visit https://platform.deepseek.com
2. Sign up or log in
3. Navigate to API keys section
4. Create new API key
5. Copy key to .env file

**Pricing** (as of 2024):
- Input: ~$0.14 per million tokens
- Output: ~$0.28 per million tokens
- Typical workflow cost: $2-5 for complete metadata enhancement

**Rate Limits**:
- Requests per minute: Varies by plan
- If you hit limits: Add delays or upgrade plan

**Models**:
- `deepseek-chat`: General purpose (used in this app)
- `deepseek-coder`: For code generation

### Alternative LLM Providers

The app is designed for DeepSeek but can be adapted for:
- OpenAI GPT-4/GPT-3.5
- Anthropic Claude
- Google Gemini
- Local models (Ollama, LM Studio)

---

## 📁 Project Structure

```
5. business_intelligence_app/
├── app.py                  # Main Gradio application
├── requirements.txt        # Python dependencies
├── .env                    # Configuration (API keys, DB credentials)
├── README.md              # This file
└── metadata_*.xlsx        # Generated metadata files (after Tab 4)
```

---

## 🚀 Quick Start Checklist

- [ ] PostgreSQL database running with data
- [ ] OpenSearch running (localhost:9200)
- [ ] Python 3.8+ installed
- [ ] Virtual environment created
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] .env file configured with:
  - [ ] DEEPSEEK_API_KEY
  - [ ] POSTGRES_* credentials
- [ ] Run `python app.py`
- [ ] Open http://localhost:7860
- [ ] Follow tabs 1-9 in order

---

## 🎓 Learning Resources

### RAG (Retrieval-Augmented Generation)
- [What is RAG?](https://aws.amazon.com/what-is/retrieval-augmented-generation/)
- [RAG for SQL Generation](https://medium.com/@bijit211987/rag-for-text-to-sql-a-comprehensive-tutorial-7fa5a7a3ae90)

### OpenSearch
- [OpenSearch Documentation](https://opensearch.org/docs/latest/)
- [ML Commons Plugin](https://opensearch.org/docs/latest/ml-commons-plugin/index/)
- [Neural Search](https://opensearch.org/docs/latest/search-plugins/neural-search/)

### DeepSeek
- [DeepSeek Platform](https://platform.deepseek.com)
- [API Documentation](https://platform.deepseek.com/api-docs/)

---

## 📝 Notes

### Security Considerations
- **.env file**: Never commit to version control (add to .gitignore)
- **API keys**: Rotate regularly
- **Database credentials**: Use read-only user for production
- **Network**: Consider VPN for remote database access

### Performance Optimization
- **Metadata enhancement**: Process in batches if dataset is large
- **OpenSearch ingestion**: Adjust chunk_size based on system resources
- **Caching**: Consider caching frequent queries
- **Model choice**: Smaller models = faster but less accurate

### Limitations
- Requires active internet connection for LLM API calls
- SQL generation accuracy depends on metadata quality
- Complex queries may need manual refinement
- Works best with well-structured databases

---

## 🤝 Support

For issues or questions:
1. Check this README's Troubleshooting section
2. Review error messages carefully
3. Verify all prerequisites are met
4. Check logs in terminal where app is running

---

## 📄 License

Based on the opensearch-POSTGRES-RAG notebooks from the parent project.

---

## 🙏 Acknowledgments

- Built on OpenSearch and PostgreSQL
- Powered by DeepSeek LLM
- UI created with Gradio
- Based on RAG techniques from the AI/ML community

---

**Happy Querying! 🎉**

Remember: The more descriptive your metadata, the better your SQL generation will be. Take time to properly enhance metadata in Tab 3!
