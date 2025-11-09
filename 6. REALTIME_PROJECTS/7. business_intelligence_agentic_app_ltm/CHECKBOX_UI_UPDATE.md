# Checkbox UI Update for Long-Term Memory

## 🎯 Overview
Updated the LTM UI to use **checkboxes** instead of radio buttons, allowing users to:
- Select multiple cached queries to view their SQL side-by-side
- Always see "Something else" option to generate new SQL
- Compare different SQL approaches for similar questions

## 🔄 What Changed

### 1. UI Component Change
**Before**: Radio buttons (single selection)
```python
query_selection = gr.Radio(
    label="Select a query or choose 'Something else' to generate new SQL",
    choices=[],
    visible=False
)
```

**After**: Checkbox group (multiple selection)
```python
query_selection = gr.CheckboxGroup(
    label="📋 Select one or more cached queries to view their SQL, or choose 'Something else' to generate new SQL",
    choices=[],
    visible=False
)
```

### 2. Updated `check_similar_queries_ui()` Function

**Key Changes**:
- Checkbox options now include similarity score in label
- Format: `"Query 1 (Score: 0.95): What are the top customers..."`
- Always adds `"🆕 Something else - Generate new SQL"` option
- Returns empty list `[]` as default value (no pre-selection)

**New Status Message**:
```
"👇 Check one or more queries below to view their SQL, or select 'Something else' to generate new SQL"
```

### 3. Updated `handle_query_selection_ui()` Function

**Before**: Single selection handling
```python
def handle_query_selection_ui(query_text, selected_option):
    # Handle single radio button selection
    if "Generate new SQL" in selected_option:
        return generate_new_sql_ui(query_text)
    # Extract option number and show SQL
```

**After**: Multiple selection handling
```python
def handle_query_selection_ui(query_text, selected_options):
    # Handle checkbox list selections
    if not selected_options or len(selected_options) == 0:
        return "❌ Please select at least one option", "", ""
    
    # Check if "Something else" is selected
    has_something_else = any("Something else" in opt for opt in selected_options)
    
    if has_something_else:
        return generate_new_sql_ui(query_text)
    
    # Show SQL for all selected queries
    combined_sql = ""
    for selected_option in selected_options:
        # Extract query number and append SQL with header
        combined_sql += f"-- Query {i}: {query_text}\n{sql}\n\n"
```

### 4. Button Label Update
**Before**: `"✅ Use Selected Query"`  
**After**: `"✅ View Selected SQL / Generate New"`

More accurate description for multi-select behavior.

## 📊 New Features

### Feature 1: View Multiple SQL Queries
Users can select multiple checkboxes to see SQL for all selected queries:

```
-- ========================================
-- Query 1: Show top 10 customers by revenue
-- Similarity Score: 0.95
-- Date: 2024-11-01T10:30:00
-- ========================================

SELECT c."CustomerID", c."CompanyName", ...

-- ========================================
-- Query 2: List 10 best customers by sales
-- Similarity Score: 0.87
-- Date: 2024-11-01T11:15:00
-- ========================================

SELECT c."CustomerID", c."CompanyName", ...
```

### Feature 2: Compare SQL Approaches
Users can compare different SQL implementations for similar questions:
- Check query 1 and query 3
- See both SQL queries side-by-side
- Learn different approaches or pick the best one

### Feature 3: Always Available "Something Else"
The "Something else" option is always present in the checkbox list:
- Appears at the bottom of the list
- Clearly marked with 🆕 emoji
- When selected, generates new SQL (ignoring other selections)

## 🎨 UI Workflow

### Step-by-Step User Experience

1. **Enter Query**
   ```
   User types: "Show top performing products"
   ```

2. **Click "Check Similar Queries"**
   ```
   Status: 🔍 Found 3 similar queries in history!
   
   👇 Check one or more queries below to view their SQL...
   ```

3. **See Checkbox Options**
   ```
   ☐ Query 1 (Score: 0.92): Show best selling products by revenue
   ☐ Query 2 (Score: 0.85): List top products by sales volume
   ☐ Query 3 (Score: 0.78): What are the most popular products
   ☐ 🆕 Something else - Generate new SQL
   ```

4. **Select Options** (Multiple choices)
   
   **Option A**: Select one cached query
   ```
   ☑ Query 1 (Score: 0.92): Show best selling products by revenue
   ☐ Query 2 (Score: 0.85): List top products by sales volume
   ☐ Query 3 (Score: 0.78): What are the most popular products
   ☐ 🆕 Something else - Generate new SQL
   ```
   Result: Shows SQL for Query 1

   **Option B**: Select multiple cached queries
   ```
   ☑ Query 1 (Score: 0.92): Show best selling products by revenue
   ☑ Query 2 (Score: 0.85): List top products by sales volume
   ☐ Query 3 (Score: 0.78): What are the most popular products
   ☐ 🆕 Something else - Generate new SQL
   ```
   Result: Shows SQL for both Query 1 and Query 2 with headers

   **Option C**: Select "Something else"
   ```
   ☐ Query 1 (Score: 0.92): Show best selling products by revenue
   ☐ Query 2 (Score: 0.85): List top products by sales volume
   ☐ Query 3 (Score: 0.78): What are the most popular products
   ☑ 🆕 Something else - Generate new SQL
   ```
   Result: Generates new SQL using LLM + RAG

5. **Click "View Selected SQL / Generate New"**
   - If cached queries selected: Display their SQL instantly
   - If "Something else" selected: Generate new SQL with LLM

## 💡 Benefits

### 1. Better User Control
- **Freedom to explore**: Check multiple queries to find the best one
- **Learn by comparison**: See different SQL approaches side-by-side
- **No commitment**: Preview SQL before deciding to use it

### 2. Enhanced Learning
- Compare SQL patterns across similar queries
- Understand different ways to solve the same problem
- Identify the most efficient query structure

### 3. Flexibility
- Mix and match: Select any combination of queries
- Always have "Something else" option available
- No forced choice between cached or new

### 4. Cost Optimization
- View multiple cached queries without LLM calls
- Only generate new SQL when explicitly requested
- Maximize reuse of existing queries

## 🧪 Testing Scenarios

### Test Case 1: Single Selection
```
1. Enter query: "Show customer orders"
2. Check similar queries
3. Select ONE checkbox (Query 1)
4. Click "View Selected SQL"
5. Expected: Display SQL for Query 1 with header
```

### Test Case 2: Multiple Selection
```
1. Enter query: "Show customer orders"
2. Check similar queries
3. Select THREE checkboxes (Query 1, 2, 3)
4. Click "View Selected SQL"
5. Expected: Display all 3 SQL queries with separators
```

### Test Case 3: Something Else
```
1. Enter query: "Show customer orders"
2. Check similar queries
3. Select ONLY "Something else" checkbox
4. Click "View Selected SQL"
5. Expected: Generate new SQL using LLM
```

### Test Case 4: Mixed Selection (Something Else Wins)
```
1. Enter query: "Show customer orders"
2. Check similar queries
3. Select Query 1 + Query 2 + "Something else"
4. Click "View Selected SQL"
5. Expected: Generate new SQL (Something else takes precedence)
```

### Test Case 5: No Selection
```
1. Enter query: "Show customer orders"
2. Check similar queries
3. Select NO checkboxes
4. Click "View Selected SQL"
5. Expected: Error message "Please select at least one option"
```

## 📝 Implementation Notes

### Global State Update
```python
global_state['similar_queries_cache'] = [
    {
        'query': 'Original query text',
        'sql': 'SELECT ...',
        'score': 0.95,
        'timestamp': '2024-11-01T10:30:00'
    },
    ...
]
```

### Checkbox Value Format
Checkbox selections return list of strings:
```python
selected_options = [
    "Query 1 (Score: 0.95): Show top customers...",
    "Query 3 (Score: 0.82): List best customers..."
]
```

### SQL Combination Logic
```python
combined_sql = ""
for selected_option in selected_options:
    query_num = extract_number(selected_option)
    sql_data = similar_queries[query_num]
    
    combined_sql += f"-- ========================================\n"
    combined_sql += f"-- Query {query_num + 1}: {sql_data['query']}\n"
    combined_sql += f"-- ========================================\n\n"
    combined_sql += sql_data['sql'] + "\n\n\n"
```

### First Query Priority
The first selected query's SQL is stored in `global_state['last_sql']` for execution in Tab 7:
```python
first_query_num = int(selected_options[0].split("(")[0].replace("Query", "").strip()) - 1
global_state['last_sql'] = similar_queries[first_query_num]['sql']
```

## 🔧 Configuration

### Adjustable Parameters
```python
# In check_similar_queries_ui()
top_k = 5  # Number of similar queries to show

# In handle_query_selection_ui()
# No limit on number of selections (all checkboxes can be checked)
```

### UI Customization
```python
# Checkbox label format
label = f"Query {i+1} (Score: {score:.2f}): {preview_text}"

# Something else label
something_else = "🆕 Something else - Generate new SQL"

# SQL separator
separator = "-- ========================================"
```

## 🚀 Usage Tips

### For Users
1. **Start broad**: Check multiple queries to see options
2. **Narrow down**: Compare SQL and pick the most relevant
3. **Fall back**: Use "Something else" if none match your needs
4. **Learn**: Study different SQL approaches in cached queries

### For Developers
1. **Monitor selections**: Track which queries users select most
2. **Optimize storage**: Consider query popularity for caching
3. **Improve matching**: Adjust similarity threshold based on usage
4. **Add analytics**: Log multi-selection patterns for insights

## 🐛 Known Limitations

1. **No preview in checkbox label**: Full SQL not visible until selection
   - Mitigation: Detailed text shown in "Similar Queries Found" section

2. **First query priority**: Only first selected SQL goes to Tab 7
   - Mitigation: Clear message in status and history display

3. **Something else precedence**: Overrides all other selections
   - Mitigation: Clear behavior documented in UI

## 📚 References

- **Gradio CheckboxGroup**: https://www.gradio.app/docs/checkboxgroup
- **Previous Radio implementation**: See `LTM_IMPLEMENTATION.md`
- **Vector Search**: See `README.md` for LTM architecture

---

**Update Date**: November 2, 2024  
**Version**: 1.1.0  
**Change Type**: UI Enhancement (Radio → CheckboxGroup)  
**Status**: ✅ Complete and ready for testing
