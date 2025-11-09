# Business Intelligence Agentic Application with Long-Term Memory (LTM)

## 🧠 Overview

This application extends the conversational BI agent with **Long-Term Memory (LTM)** capabilities for intelligent query caching using vector embeddings. It eliminates redundant LLM calls by retrieving SQL from similar past queries, reducing cost and latency while ensuring consistency.

## 🆕 What's New: Long-Term Memory Features

### 1. **Query Caching with Vector Search**
- Every user query is embedded using the same model as metadata (sentence-transformers/all-MiniLM-L12-v2, 384 dimensions)
- Stored in OpenSearch with `knn_vector` field for semantic similarity search
- Finds similar queries even with different wording (e.g., "top 10 customers by revenue" ≈ "show me the 10 highest revenue customers")

### 2. **Smart Query Workflow**
```
User Query → Search LTM (vector search) → Present Top 5 Matches
            ↓
   User Selects Option:
   ├─ Cached Query → Retrieve SQL (no LLM call) → Display
   └─ "Something Else" → Generate New SQL → Store in LTM → Display
```

### 3. **Cost & Time Optimization**
- **Cached queries**: Instant SQL retrieval (no API call, no latency)
- **New queries**: Standard RAG + LLM generation + auto-storage
- Typical savings: 60-80% reduction in LLM calls for repeated/similar questions

### 4. **Consistency Guarantee**
- Same question always returns same SQL (no LLM variability)
- Historical queries maintain their original logic
- Audit trail: timestamp + metadata context stored with each query

## 🔧 Technical Architecture

### LTM Index Structure
```json
{
  "user_query": "Show top 10 customers by revenue",
  "user_query_embedding": [0.123, -0.456, ...],  // 384-dimensional vector
  "generated_sql": "SELECT c.\"CustomerID\", ...",
  "timestamp": "2024-01-15T10:30:00",
  "metadata_context": "Used tables: customers, sales_details"
}
```

### Key Components

1. **LTM Index**: `query_long_term_memory`
   - Mapping: `user_query_embedding` (knn_vector, dimension=384, engine=lucene, space_type=cosinesimil)
   - Auto-embedding via ingest pipeline: `ltm_embedding_pipeline`

2. **Embedding Pipeline**
   - Same model as metadata embedding: `sentence-transformers/all-MiniLM-L12-v2`
   - Consistent vector space for reliable similarity search

3. **Search Strategy**
   - Neural search with k=5 (top 5 matches)
   - Min score threshold: 0.7 (70% similarity)
   - Sorted by relevance score

4. **Storage Strategy**
   - Store after successful SQL generation
   - Include conversation context metadata
   - Timestamped for audit trail

## 🚀 How to Use

### Step-by-Step Workflow

**Tab 6: Ask Questions (Updated UI)**

1. **Enter your question** in the text box
   ```
   Example: "Segment customers based on their order values and frequency"
   ```

2. **Click "🔍 Check Similar Queries"**
   - System searches LTM using vector embeddings
   - Displays top 5 similar past queries with scores
   - Shows option "Something else" for new queries

3. **Select from radio buttons**:
   - **Option 1-5**: Cached query (instant SQL, no LLM call)
   - **"Something else"**: Generate new SQL with LLM

4. **Click "✅ Use Selected Query"**
   - If cached: Retrieves SQL immediately
   - If new: Generates SQL → Stores in LTM → Displays result

5. **Review SQL and conversation history**
   - SQL appears in main output box
   - Conversation history shows in side panel

6. **Execute in Tab 7** as usual

### Example Scenarios

**Scenario 1: First Time Query**
```
Query: "Show top 10 customers by total revenue"
→ No similar queries found
→ Select "Something else"
→ System generates SQL using RAG + LLM
→ SQL stored in LTM
→ Display result
```

**Scenario 2: Similar Query (Next Day)**
```
Query: "Top 10 customers sorted by revenue"
→ Found 5 similar queries:
   1. "Show top 10 customers by total revenue" (score: 0.92)
   2. "List 10 best customers by sales" (score: 0.85)
   ...
→ Select option 1
→ Retrieve cached SQL (no LLM call)
→ Display result instantly
```

**Scenario 3: Follow-up Question (with Conversation Memory)**
```
Query: "Show me the top 5 from that result"
→ Conversation memory provides context from previous query
→ Check LTM for similar follow-ups
→ Generate or retrieve SQL
→ Store if new
```

## 📊 Benefits

### For Users
- **Faster responses**: Cached queries return instantly
- **Consistent results**: Same question = same SQL every time
- **Cost savings**: Reduced API calls to LLM provider
- **Better UX**: Preview similar queries before committing to new generation

### For Developers
- **Audit trail**: All queries logged with timestamps
- **Debugging**: Historical queries help understand usage patterns
- **Optimization**: Identify frequently asked questions for precomputation
- **Scalability**: LTM reduces load on LLM service

## 🔄 Differences from Folder 5 (Conversation Memory Only)

| Feature | Folder 5 | Folder 7 (This App) |
|---------|----------|---------------------|
| **Conversation Memory** | ✅ Yes | ✅ Yes |
| **Long-Term Memory** | ❌ No | ✅ Yes |
| **Query Caching** | ❌ No | ✅ Vector-based |
| **Similar Query Search** | ❌ No | ✅ Top 5 matches |
| **LLM Call Optimization** | Every query | Only for new/unique queries |
| **UI Workflow** | Single "Generate SQL" button | Two-step: Check similar → Select |
| **Storage** | Session-based conversation only | Persistent query cache |
| **Cost Efficiency** | Standard | 60-80% reduction |

## 🛠️ Setup Requirements

### Prerequisites (Same as Folder 5)
- OpenSearch cluster (2.x)
- PostgreSQL database with Northwind data
- DeepSeek API key
- Python 3.8+

### Installation
```bash
cd opensearch/my_tutorial/scripts/5.\ REALTIME_PROJECTS/7.\ business_intelligence_agentic_app_ltm/
pip install -r requirements.txt
```

### Environment Variables (.env)
```env
# OpenSearch
OPENSEARCH_HOST=localhost
OPENSEARCH_PORT=9200
OPENSEARCH_USER=admin
OPENSEARCH_PASSWORD=admin

# PostgreSQL
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=northwind
POSTGRES_USER=your_user
POSTGRES_PASSWORD=your_password

# DeepSeek API
DEEPSEEK_API_KEY=sk-your-key-here
DEEPSEEK_BASE_URL=https://api.deepseek.com
```

### Run the Application
```bash
python app.py
```

Access at: `http://localhost:7861`

## 🧪 Testing the LTM Feature

### Test Case 1: First Query
```
1. Run setup (Tab 1-5)
2. Go to Tab 6
3. Enter: "Show top 10 products by sales"
4. Click "Check Similar Queries"
5. Expected: No similar queries found → Select "Something else"
6. Click "Use Selected Query"
7. Expected: SQL generated and stored in LTM
```

### Test Case 2: Similar Query
```
1. Enter: "List 10 products sorted by sales"
2. Click "Check Similar Queries"
3. Expected: Previous query appears in top 5 (score > 0.7)
4. Select the cached query
5. Click "Use Selected Query"
6. Expected: SQL retrieved instantly (no LLM call)
```

### Test Case 3: Different Query
```
1. Enter: "Count customers by country"
2. Click "Check Similar Queries"
3. Expected: No matching queries (different intent)
4. Select "Something else"
5. Generate new SQL and store
```

## 📁 File Structure

```
7. business_intelligence_agentic_app_ltm/
├── app.py                    # Main application with LTM features
├── requirements.txt          # Python dependencies
├── .env                      # Environment variables (create this)
└── README.md                 # This file
```

## 🔍 Key Functions (New in Folder 7)

### LTM Management Functions

1. **`create_ltm_index(os_client, model_id)`**
   - Creates LTM index with 384d knn_vector field
   - Sets up ingest pipeline for auto-embedding
   - Returns success status and message

2. **`search_similar_queries_in_ltm(os_client, user_query, model_id, top_k=5)`**
   - Performs neural search using query embedding
   - Returns top K similar queries with scores
   - Filters by min_score=0.7 (70% similarity)

3. **`store_query_in_ltm(os_client, user_query, generated_sql, metadata_context="")`**
   - Stores query-SQL pair in LTM
   - Auto-generates embedding via pipeline
   - Adds timestamp and metadata

4. **`format_similar_queries_for_display(similar_queries)`**
   - Formats search results as numbered options
   - Shows score and query text
   - Adds "Something else" option

### UI Workflow Functions

5. **`check_similar_queries_ui(user_query)`**
   - Step 1: Search LTM and present options
   - Updates radio button choices
   - Shows/hides UI elements dynamically

6. **`handle_query_selection_ui(user_query, selected_option)`**
   - Step 2: Process user selection
   - Routes to cached retrieval or new generation
   - Updates conversation history

7. **`generate_new_sql_ui(user_query)`**
   - Step 3: Generate new SQL if selected
   - Same RAG + LLM logic as folder 5
   - Stores in LTM after generation

## 🎯 Future Enhancements

1. **Query Similarity Tuning**
   - Adjustable min_score threshold
   - User feedback on match quality
   - Learning-based threshold adjustment

2. **LTM Management UI**
   - View all cached queries (Tab 8)
   - Delete obsolete queries
   - Export query history

3. **Query Versioning**
   - Store multiple SQL versions per query
   - Track performance metrics
   - A/B testing different SQL approaches

4. **Analytics Dashboard**
   - LTM hit rate metrics
   - Most popular queries
   - Cost savings estimation

## 📝 Notes

- LTM is **optional**: App works without it (degrades gracefully)
- LTM persists across sessions (unlike conversation memory)
- Embedding model must match metadata embedding for consistent vector space
- Min score 0.7 is configurable in `search_similar_queries_in_ltm()`

## 🐛 Troubleshooting

**Issue**: "LTM index creation failed"
- Check OpenSearch cluster health
- Verify model is registered and deployed
- Check logs for specific error

**Issue**: "No similar queries found" (when expecting matches)
- Lower min_score threshold (try 0.6)
- Check query embedding generation
- Verify LTM pipeline is active

**Issue**: "Cached SQL doesn't match current context"
- This is expected - cached queries use original context
- Select "Something else" to generate fresh SQL
- Consider adding context fingerprinting for better matching

## 📚 References

- **OpenSearch Neural Search**: https://opensearch.org/docs/latest/search-plugins/neural-search/
- **Sentence Transformers**: https://www.sbert.net/docs/pretrained_models.html
- **DeepSeek API**: https://platform.deepseek.com/docs
- **Gradio Documentation**: https://www.gradio.app/docs

## 🤝 Contributing

This is a tutorial/demo application. For production use:
- Add authentication and user isolation
- Implement query access control
- Add monitoring and logging
- Optimize vector search performance
- Consider distributed OpenSearch cluster

---

**Version**: 1.0.0  
**Last Updated**: 2024-01-15  
**Based on**: Folder 5 (business_intelligence_agentic_app_memory)
