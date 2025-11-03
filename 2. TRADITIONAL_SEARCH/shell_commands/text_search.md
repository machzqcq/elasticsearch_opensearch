# Text Search Scenarios - ElasticSearch/OpenSearch

## 1. Basic Mapping & Search
Get index mapping and perform basic match_all query on the ecommerce index.

**Key Operations:**
- `GET ecommerce/_mapping` - View field mappings
- `GET /ecommerce/_search` - Basic match_all query

---

## 2. Collapse & Sort
Match specific category and collapse results by type, then sort by day of week.

**Key Parameters:**
- `match` - Find category "Men's Shoes"
- `collapse` - Collapse on type field
- `sort` - Sort by day_of_week

---

## 3. Pagination with Offset
Retrieve paginated results using from/size parameters or query string.

**Key Parameters:**
- `from`: Starting position
- `size`: Number of results per page
- Use with match query for specific manufacturer

---

## 4. Scroll for Large Result Sets
Maintain a consistent view while scrolling through large result sets using keep_alive.

**Key Concepts:**
- `scroll` - Set scroll window (e.g., 10m)
- `scroll_id` - Identify scroll context
- Useful for exporting large datasets

---

## 5. Search After for Deep Pagination
Use search_after with sort for stateless pagination across consistent result sets.

**Key Parameters:**
- `search_after` - Array of sort values from last document
- `sort` - Must include _id for uniqueness
- More efficient than offset-based pagination

---

## 6. Point In Time (PIT)
Use PIT for consistent pagination without drift, particularly for frequently updated indices.

**Key Steps:**
1. Create PIT with `POST /ecommerce/_search/point_in_time?keep_alive=100m`
2. Use returned PIT ID in subsequent searches
3. Include PIT id and keep_alive in search requests

---

## 7. Sort Results
Sort results by multiple fields with ascending/descending order.

**Key Operations:**
- Single field sort by manufacturer.keyword descending
- Multiple field sorting in array format

---

## 8. Highlight Search Terms
Highlight matched terms in results with default or custom tags.

**Key Parameters:**
- `highlight` - Enable highlighting
- `fields` - Specify which fields to highlight
- `pre_tags`/`post_tags` - Custom HTML tags (default: `<em></em>`)

---

## 9. Autocomplete with Edge N-grams
Enable prefix-based search using edge n-gram analyzer.

**Key Concepts:**
- Use Python script to create mapping with autocomplete analyzer
- `POST _analyze` - Test analyzer behavior
- Use autocomplete analyzer at index time, standard at search time to avoid over-matching

---

## 10. Completion Suggester
Use completion datatype for fast, prefix-based suggestions.

**Key Features:**
- `completion` type - Optimized for suggestions
- `suggest` query with prefix
- Fast prefix matching

---

## 11. Fuzzy Suggestions
Add fuzzy matching to completion suggester to handle misspellings.

**Key Parameters:**
- `fuzzy` with `fuzziness: "AUTO"`
- Works with completion suggester
- Handles typos like "smmer" for "summer"

---

## 12. Search as You Type
Real-time search suggestions using search_as_you_type datatype with n-grams.

**Key Concepts:**
- `search_as_you_type` type - Generates n-gram fields automatically
- `multi_match` with `bool_prefix` type
- Query multiple n-gram fields for progressive matching

---

## 13. Analyze Text
Analyze how text is tokenized by a specific field's analyzer.

**Key Usage:**
- `POST _analyze` - Test tokenization
- Specify analyzer and text
- Useful for debugging search issues

---

## 14. Spell Check - Term Suggester
Suggest corrections for misspelled words using term suggester.

**Key Parameters:**
- `term` suggester type
- `text` - Misspelled input
- `field` - Field to suggest from

---

## 15. Multiple Spell Check Suggestions
Run multiple spell check suggestions in a single query.

**Key Feature:**
- Multiple suggest clauses (spell-check1, spell-check2)
- Process multiple misspellings at once

---

## 16. Phrase Suggester
Suggest corrections for multi-word phrases using phrase suggester.

**Key Setup:**
- Custom trigram analyzer with shingle filter
- Phrase suggester type
- Handles multi-word corrections

---

## 17. Phrase Suggester with Highlighting
Phrase suggester with visual highlighting of corrected terms.

**Key Parameters:**
- `gram_size` - Size of shingles to consider
- `highlight` - Custom pre/post tags for corrections
- Shows exact correction suggestions

---

## 18. Retrieve Specific Fields
Control which fields are returned in search results.

**Key Scenarios:**
- Disable source entirely with `"_source": false`
- Include/exclude specific fields via source filtering
- Use `fields` parameter with wildcards

---

## 19. Match Query
Basic text search matching on analyzed fields.

**Key Behavior:**
- Tokenizes search term based on field analyzer
- Returns partial token matches
- Matches "Code optimization" and variations

---

## 20. Match on Substring
Match queries find substrings after tokenization.

**Key Example:**
- "Ui5 code optimization" returns results containing any of those tokens

---

## 21. Single Token Match
Match a single token within multi-token field.

**Key Point:**
- "Ui5" matches documents containing that token
- Useful for substring matching within larger values

---

## 22. Exact Match with Keyword Field
Use .keyword field for exact string matching.

**Key Requirement:**
- Field must have both text and keyword mapping
- Avoids tokenization

---

## 23. Match Phrase Query
Match exact phrase without intervening words.

**Key Behavior:**
- Returns only documents with exact phrase sequence
- More restrictive than match

---

## 24. Match Phrase with Slop
Allow words between phrase terms using slop parameter.

**Key Parameters:**
- `slop: 1` - Allow 1 word between terms
- Handles word order variations

---

## 25. Reverse Phrase Matching with Slop
Match phrase with reversed word order using appropriate slop value.

**Key Concept:**
- `slop: 3` for reverse of 2-word phrase
- Formula: slop = 2 + number of intervening words for reverse

---

## 26. Proximity Search
Find documents where terms appear within specified distance but score closer matches higher.

**Key Use Case:**
- Large slop value (e.g., 100) for loose proximity
- Scores based on actual distance between terms

---

## 27. Match Phrase Prefix
Match documents starting with a phrase prefix.

**Key Feature:**
- Last term treated as prefix
- Useful for partial phrase matching

---

## 28. Term Query
Exact term matching without analysis on keyword fields.

**Key Characteristics:**
- No tokenization or analysis
- Match exact term value
- Two syntax variations shown

---

## 29. Terms Query
Match documents containing any of multiple exact terms.

**Key Feature:**
- At least one term must match
- Useful for categorical matching

---

## 30. Filter Clause
Apply filtering without affecting scoring.

**Key Concepts:**
- Filter runs after query phase
- Reduces result set but doesn't boost/reduce scores
- Queries in filter return score of 0

---

## 31. Bool Query - Must/Filter
Combine must clauses with filters for scoring and pruning.

**Key Structure:**
- `must` - Contributes to score
- `filter` - Prunes results without scoring

---

## 32. Bool Query - Complex Mix
Combine must, should, and must_not clauses with minimum_should_match.

**Key Parameters:**
- `must` - All conditions required
- `should` - Boost matching documents
- `must_not` - Exclude documents
- `minimum_should_match` - At least N should conditions

---

## 33. Pagination with From/Size
Basic offset-based pagination.

**Key Limitation:**
- Deep pagination performance degrades
- Every result must be scored and sorted

---

## 34. Sort by Score
Sort results by relevance score in ascending order.

**Key Parameter:**
- `_score` field with order direction

---

## 35. Sort by Date Field
Sort results by timestamp field in descending order.

**Key Usage:**
- Works on keyword and numeric fields
- Cannot sort on analyzed text fields

---

## 36. Multi-field Sort
Sort by multiple fields with different orders.

**Key Syntax:**
- Array of sort clauses
- Applied in order

---

## 37. Cannot Sort on Text Field
Demonstrates error when attempting to sort on analyzed text field.

**Key Issue:**
- Text fields are tokenized and cannot be sorted
- Causes illegal_argument_exception

---

## 38. Sort Using Keyword Field
Workaround for sorting using .keyword sub-field.

**Key Requirement:**
- Field must have keyword mapping
- Existing text fields cannot be updated without reindexing

---

## 39. Fuzzy Matching - Keyword Field
Fuzzy matching on keyword fields using Levenshtein edit distance.

**Key Concepts:**
- Only works on keyword/term queries
- Handles typos and misspellings
- `fuzziness: "AUTO"` recommended

---

## 40. Fuzzy on Text Field (Fails)
Demonstrates that fuzzy matching doesn't work on text fields.

**Key Limitation:**
- Text fields are analyzed/tokenized
- Fuzzy only works on exact keyword matches

---

## 41. Fuzzy on Keyword Field (Success)
Fuzzy matching successfully works on keyword fields.

**Key Example:**
- "code optmization" matches "code optimization"
- Uses edit distance algorithm

---

## 42. Compound Bool Query
Complex bool query with must, filter, must_not, should, and boost.

**Key Structure:**
- Multiple conditions across all clause types
- `boost` parameter adjusts overall query score

---

## 43. Bool Filter (No Scoring)
Use bool with only filter clause for pruning without scoring.

**Key Behavior:**
- Filter returns score of 0
- Just removes non-matching documents

---

## 44. Bool with Match All and Filter
Match all documents then apply filter.

**Key Difference:**
- match_all contributes score
- filter prunes results

---

## 45. Constant Score Query
Apply constant score to filtered results with optional boost.

**Key Parameters:**
- `constant_score` wraps filter
- `boost` - Fixed score multiplier
- Useful for equal-weight results

---

## 46. Named Queries
Name query clauses to identify their contribution to final score.

**Key Usage:**
- `_name` parameter on each clause
- Helps debug scoring behavior

---

## 47. Named Queries with Score Breakdown
View score contribution of each named clause.

**Key Parameter:**
- `?include_named_queries_score` - Show per-clause scores
- Helps understand relevance scoring

---

## 48. Intervals Query - Basic
Advanced positional query with all_of and any_of conditions.

**Key Concepts:**
- Match terms must appear in specified order
- `all_of` - All conditions required
- `any_of` - Any of listed intervals match

---

## 49. Intervals with Basic Terms
Intervals matching two specific terms within document.

**Key Structure:**
- `ordered: true` - Maintain word order
- `max_gaps: 0` - No intervening words

---

## 50. Intervals with Multi-word Phrase
Match multi-word phrase as single unit with any_of alternatives.

**Key Feature:**
- Phrase treated as unit
- Alternatives provided via any_of

---

## 51. Intervals with Fuzzy Matching
Combine intervals with fuzzy term matching.

**Key Mix:**
- Fuzzy on one interval
- Standard match on others
- Avoid mixing fuzziness with wildcards

---

## 52. Intervals with Prefix Matching
Use prefix intervals combined with standard term intervals.

**Key Feature:**
- Prefix partial term matching within interval structure

---

## 53. Intervals with Wildcard Matching
Wildcard pattern matching within interval queries.

**Key Operators:**
- `?` - Any single character
- `*` - Zero or more characters

---

## 54. Intervals with Filter
Filter intervals to exclude specific terms from results.

**Key Parameter:**
- `filter.not_containing` - Exclude matching intervals
- Returns matches without salty

---

## 55. Query String Query - AND Operator
Parse and execute query string with AND logic.

**Key Syntax:**
- Parentheses for grouping
- AND/OR/NOT operators
- Returns invalid syntax error for bad input

---

## 56. Query String Query - OR Operator
Query string with OR logic between terms.

**Key Usage:**
- Multiple alternatives
- Returns documents matching any term

---

## 57. Query String with Multi-word OR
OR logic with multi-word search terms.

**Key Example:**
- Match "Civil engineering" OR "theses"

---

## 58. Query String with Field Wildcards
Query string with wildcard field matching.

**Key Feature:**
- `fields: ["RELATED_TASKS*"]` - Match multiple fields
- Apply query across multiple fields

---

## 59. Query String with Escaped Wildcard
Escape wildcard characters to search for literal asterisks.

**Key Syntax:**
- `\\*` - Escaped asterisk
- Differentiates from wildcard usage

---
