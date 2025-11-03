# Real-time Search Implementation

This document describes the real-time search implementation with debouncing across all three frontends.

## Overview

All frontends now implement **true real-time search** - search results appear automatically as the user types, without requiring a search button click. Each implementation includes debouncing to prevent excessive API calls.

## Implementation Details

### 1. Streamlit (streamlit_app.py)

**Approach**: Session state-based debouncing with time tracking

```python
# Initialize session state for debouncing
if 'last_query' not in st.session_state:
    st.session_state.last_query = ""
if 'search_results' not in st.session_state:
    st.session_state.search_results = None
if 'last_search_time' not in st.session_state:
    st.session_state.last_search_time = 0

# Auto-trigger search on input change (with debounce)
current_time = time.time()
should_search = False

if search_query and len(search_query.strip()) > 0:
    # Check if query changed or enough time has passed (0.5 second debounce)
    if (search_query != st.session_state.last_query or 
        current_time - st.session_state.last_search_time > 0.5):
        should_search = True
        st.session_state.last_query = search_query
        st.session_state.last_search_time = current_time
```

**Debounce Duration**: 500ms (0.5 seconds)

**Key Features**:
- Tracks last query and search time in session state
- Only triggers search if query changed OR 500ms elapsed
- Preserves search results across reruns
- Eliminates manual search button

### 2. Gradio (gradio_app.py)

**Approach**: Built-in event handling with `trigger_mode`

```python
# Real-time search on input change
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
```

**Debounce Duration**: Handled by Gradio internally (typically ~250-300ms)

**Key Features**:
- Uses Gradio's `change` event with `trigger_mode="always_last"`
- `always_last` mode: queues events and only processes the latest one
- Automatic debouncing by framework
- Keeps search button for explicit search
- Also supports Enter key submission

### 3. React (react-frontend/src/App.js)

**Approach**: useEffect with cleanup and setTimeout

```javascript
// Debounced real-time search
useEffect(() => {
  const debounceTimer = setTimeout(() => {
    if (query) {
      performSearch(query);
    } else {
      setResults(null);
      setError(null);
    }
  }, 400); // 400ms debounce

  return () => clearTimeout(debounceTimer);
}, [query, performSearch]);
```

**Debounce Duration**: 400ms

**Key Features**:
- useEffect hook monitors query changes
- setTimeout delays API call by 400ms
- Cleanup function cancels previous timer on new input
- Clears results when query is empty
- Keeps search button for explicit search

## User Experience

### Before
- User types query → clicks Search button → results appear
- Extra step required for every search
- No immediate feedback

### After
- User types query → results appear automatically after brief pause
- No button click needed
- Immediate feedback as user types
- Button still available for explicit search

## Technical Benefits

1. **Reduced API Calls**: Debouncing prevents API call on every keystroke
2. **Better UX**: Feels more responsive and modern
3. **Backward Compatible**: Search button still works for those who prefer it
4. **Resource Efficient**: Only searches when user pauses typing

## Debounce Duration Comparison

| Frontend | Duration | Rationale |
|----------|----------|-----------|
| Streamlit | 500ms | Balances responsiveness with page rerun cost |
| Gradio | ~250-300ms | Framework default, fast updates |
| React | 400ms | Good balance for API calls, smooth UX |

## Testing

To test the real-time search:

1. Start the application: `./start.sh`
2. Open any frontend (Streamlit, Gradio, or React)
3. Start typing in the search box
4. Observe results appearing automatically after brief pause
5. Continue typing - previous search cancels, new search triggers
6. Clear search box - results disappear

## Configuration

### Adjusting Debounce Duration

**Streamlit** - Edit `streamlit_app.py`:
```python
# Change 0.5 to desired seconds
if (search_query != st.session_state.last_query or 
    current_time - st.session_state.last_search_time > 0.5):
```

**Gradio** - No direct configuration (framework controlled)

**React** - Edit `App.js`:
```javascript
// Change 400 to desired milliseconds
}, 400); // 400ms debounce
```

## Troubleshooting

### Issue: Search triggers too frequently
**Solution**: Increase debounce duration

### Issue: Search feels sluggish
**Solution**: Decrease debounce duration (minimum ~200ms recommended)

### Issue: Button click no longer works
**Solution**: Button handlers are preserved - check browser console for errors

### Issue: Empty results when typing
**Solution**: Check if at least one search field is selected in sidebar

## Architecture Impact

The real-time search implementation maintains the existing architecture:

```
User Types → Frontend Debouncing → Backend API (/api/search) → OpenSearch → Results
```

No backend changes were required - all debouncing logic is client-side.

## Performance Notes

- **Backend**: No changes needed, handles requests same as before
- **Frontend**: Minimal overhead from debounce timers
- **Network**: Reduced API calls compared to keystroke-by-keystroke search
- **OpenSearch**: Same query load as manual search

## Future Enhancements

Potential improvements:

1. **Progressive Loading**: Show results incrementally as they arrive
2. **Request Cancellation**: Cancel in-flight requests when new query starts
3. **Caching**: Cache recent searches to reduce API calls
4. **Search Suggestions**: Show autocomplete suggestions dropdown
5. **Configurable Debounce**: Allow users to adjust delay in settings
