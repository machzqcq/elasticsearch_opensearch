# 🌍 OpenSearch Geospatial Learning App - Project Summary

## Overview
An interactive Gradio web application that teaches OpenSearch geospatial queries through hands-on practice with real US cities data.

## 🎯 Learning Objectives
- Master GeoPoint and GeoShape data types
- Execute geo_bounding_box and geo_distance queries
- Visualize geospatial data on interactive maps
- Understand GeoJSON coordinate format
- Practice real-world geospatial use cases

## 📁 Project Structure

```
geo_spatial/
├── app.py                      # Main Gradio application (470+ lines)
├── config.py                   # Configuration settings (40 lines)
├── opensearch_client.py        # OpenSearch wrapper (146 lines)
├── data_loader.py              # Data preparation utilities (114 lines)
├── visualizations.py           # Folium map generation (172 lines)
├── pyproject.toml              # uv package manager config
├── run.sh                      # Quick start script
├── README.md                   # Installation & overview
├── USER_GUIDE.md               # Complete learning guide (320+ lines)
└── geo_spatial_data.ipynb      # Original learning notebook
```

## 🛠️ Technology Stack

### Core Technologies
- **Python**: 3.10+
- **Package Manager**: uv (modern, fast dependency management)
- **Web Framework**: Gradio 4.44.0+ (interactive UI)
- **Search Engine**: OpenSearch 2.4.0+
- **Visualization**: Folium 0.15.0+ (interactive maps)

### Dependencies
```toml
    "gradio==5.49.1",
    "opensearch-py==3.0.0",
    "pandas==2.2.3",
    "folium==0.20.0",
    "plotly==6.3.0",
    "chardet==5.2.0"
```

## 🚀 Quick Start

### 1. Install uv
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 2. Setup OpenSearch
Ensure OpenSearch is running on `localhost:9200` with default credentials.

### 3. Launch App
```bash
# Quick start
./run.sh

# Or manually
uv sync
uv run python app.py
```

### 4. Access App
Open browser at: http://localhost:7860

## 📚 Application Features

### Tab 1: 🔧 Setup & Connection
- **Test Connection**: Verify OpenSearch cluster connectivity
- **Load Data**: Index 100 US cities as GeoPoint documents
- **Create Indices**: Setup `learning_points` and `learning_locations`

### Tab 2: 📍 GeoPoint Basics
- **Learn Concepts**: GeoPoint data type explanation
- **View Examples**: Sample city coordinates in GeoJSON format
- **Create Points**: Convert city names to GeoJSON coordinates
- **Understand Format**: `[longitude, latitude]` order

### Tab 3: 🔍 GeoPoint Queries
#### Bounding Box Query
- Define rectangular search areas
- Specify top-left and bottom-right corners
- Example: Find all cities in California
- Visualization: Red rectangle + blue city markers

#### Distance Query
- Search within radius of center point
- Specify distance in miles (10-500)
- Example: Cities within 100 miles of New York
- Visualization: Green circle + blue city markers

### Tab 4: 🗺️ GeoShape Basics
- **Polygon Concepts**: Multi-vertex closed shapes
- **GeoJSON Structure**: Coordinate arrays for polygons
- **Sample Shapes**: California triangle example
- **Use Cases**: Delivery zones, boundaries, geofences

### Tab 5: 🔎 GeoShape Queries
- **Bounding Box on Polygons**: Find intersecting shapes
- **Visual Results**: Purple polygons on map
- **Spatial Relationships**: Understand shape queries

## 🎓 Learning Modules

### Module 1: Fundamentals
- Coordinate systems (longitude, latitude)
- GeoJSON format specification
- Data type differences (GeoPoint vs GeoShape)

### Module 2: Querying
- Bounding box queries (rectangular areas)
- Distance queries (circular radius)
- Polygon intersection queries

### Module 3: Visualization
- Interactive Folium maps
- Query result overlays
- Spatial relationship visualization

## 📊 Data Source

**US Cities Dataset** (`uscities.csv`)
- **Records**: ~30,000 US cities
- **Fields**: CITY, STATE_CODE, LAT, LNG, POPULATION
- **Location**: `../../../../data/uscities.csv`
- **Format**: CSV with UTF-8/Windows-1252 encoding

## 🔍 Example Queries

### Bounding Box Examples

**California Region**
```python
{
  "top_left": [-124.4096, 42.0095],
  "bottom_right": [-114.1312, 32.5343]
}
```

**East Coast**
```python
{
  "top_left": [-80.0, 45.0],
  "bottom_right": [-70.0, 35.0]
}
```

### Distance Query Examples

**Cities Near New York**
```python
{
  "center": "New York",
  "distance": "100mi"
}
```

**Cities Near Los Angeles**
```python
{
  "center": "Los Angeles",
  "distance": "200mi"
}
```

## 🏗️ Code Architecture

### opensearch_client.py
**Class**: `OpenSearchGeoClient`
- `connect()`: Establish OpenSearch connection
- `create_geopoint_index()`: Create GeoPoint index with mappings
- `create_geoshape_index()`: Create GeoShape index with mappings
- `geo_bounding_box_query()`: Execute bounding box search
- `geo_distance_query()`: Execute distance search
- `bulk_load_points()`: Bulk index GeoPoint documents

### data_loader.py
**Functions**:
- `load_us_cities_data()`: Load CSV with encoding detection
- `prepare_geopoint_documents()`: Convert to GeoJSON format
- `create_polygon_from_cities()`: Build polygon from coordinates
- `get_city_coordinates()`: Lookup city coordinates
- `create_sample_polygons()`: Generate example shapes

### visualizations.py
**Functions**:
- `create_base_map()`: Initialize Folium map
- `add_points_to_map()`: Add city markers
- `add_bounding_box_to_map()`: Draw search rectangle
- `add_distance_circle_to_map()`: Draw search radius
- `add_polygon_to_map()`: Render GeoShape polygons
- `visualize_geopoint_bounding_box()`: Complete bbox visualization
- `visualize_geopoint_distance()`: Complete distance visualization

### app.py
**Gradio Interface**:
- Multi-tab layout for progressive learning
- Interactive form inputs with validation
- Real-time query execution
- Map rendering with Folium HTML
- Educational content with Markdown

## 🎨 UI Components

### Input Controls
- **Textbox**: City names, polygon names
- **Number**: Latitude, longitude coordinates
- **Slider**: Distance in miles (10-500)
- **Button**: Execute queries, load data

### Output Components
- **Textbox**: Query results, status messages
- **Markdown**: Educational explanations
- **Code**: GeoJSON formatted output
- **JSON**: Sample data, cluster info
- **HTML**: Interactive Folium maps

## 🔒 Security Configuration

```python
# config.py
OPENSEARCH_HOST = "localhost"
OPENSEARCH_PORT = 9200
USE_SSL = True
VERIFY_CERTS = False  # Development only!
USERNAME = "admin"
PASSWORD = "Developer@123"
```

⚠️ **Production**: Enable certificate verification and use secrets management!

## 📈 Performance Considerations

### Query Optimization
- Limit initial data load to 100 cities
- Use index refresh for immediate search availability
- Implement bulk loading for multiple documents

### Map Rendering
- Folium generates static HTML (fast initial render)
- CircleMarker for performance with many points
- Appropriate zoom levels for different queries

## 🧪 Testing the App

### 1. Setup Validation
```bash
# Test OpenSearch connection
curl -k -u admin:Developer@123 https://localhost:9200

# Verify indices exist
curl -k -u admin:Developer@123 https://localhost:9200/_cat/indices?v
```

### 2. Query Testing
- Run bounding box with known coordinates
- Execute distance query with familiar cities
- Verify map visualizations render correctly

### 3. Data Validation
- Check document count in indices
- Verify GeoJSON format in stored documents
- Confirm coordinate order (lon, lat)

## 🐛 Troubleshooting

### Common Issues

**Import Errors (folium, gradio)**
```bash
uv sync  # Re-sync dependencies
```

**Connection Failed**
- Verify OpenSearch is running
- Check credentials in config.py
- Test with curl command

**No Query Results**
- Verify data was loaded in Setup tab
- Check coordinate order (lon, lat)
- Expand search area

**Map Not Displaying**
- Check browser console for errors
- Verify Folium HTML generation
- Try different browser

## 🔄 Future Enhancements

### Potential Features
1. **Heatmaps**: Density visualization of cities
2. **Clustering**: Marker clustering for performance
3. **Export**: Download query results as CSV/JSON
4. **Custom Data**: Upload your own geospatial datasets
5. **Advanced Queries**: geo_polygon, geo_shape relations
6. **Analytics**: Query performance metrics
7. **Multi-language**: Internationalization support

### Integration Ideas
- OpenSearch Dashboards integration
- Real-time data streaming
- Machine learning predictions
- Weather data overlay
- Population analytics

## 📖 Educational Value

### Learning Outcomes
✅ Understand geospatial data types
✅ Execute real OpenSearch queries
✅ Interpret query results visually
✅ Debug coordinate issues
✅ Apply to real-world scenarios

### Real-World Applications
- **Delivery Services**: Route optimization, zone definition
- **Real Estate**: Property search by location
- **Emergency Services**: Nearest resource location
- **Retail**: Store locator, service area mapping
- **Urban Planning**: Demographic analysis, zoning

## 📚 Additional Resources

- **Notebook**: `geo_spatial_data.ipynb` - Code walkthrough
- **User Guide**: `USER_GUIDE.md` - Step-by-step tutorial
- **README**: `README.md` - Installation & setup
- **OpenSearch Docs**: https://opensearch.org/docs/latest/search-plugins/geographic-and-xy/

## ✨ Success Criteria

The application successfully teaches geospatial concepts if students can:

1. ✅ Create GeoJSON coordinates from city names
2. ✅ Execute bounding box queries independently
3. ✅ Run distance queries with custom parameters
4. ✅ Interpret map visualizations correctly
5. ✅ Understand coordinate order (lon, lat)
6. ✅ Explain GeoPoint vs GeoShape differences
7. ✅ Apply concepts to real-world use cases

---

## 🙏 Credits

- **Data Source**: SimpleMaps US Cities Database
- **Visualization**: Folium (Python mapping library)
- **UI Framework**: Gradio (Hugging Face)
- **Search Engine**: OpenSearch (AWS)
- **Package Manager**: uv (Astral)

## 📄 License

Educational project - Use for learning purposes.

---

**Ready to Learn? Start the app and explore!** 🚀
