# 📚 Complete User Guide

## Getting Started

### Step 1: Launch the Application

```bash
# Quick start
./run.sh

# Or manually
uv run python app.py
```

Access the app at: http://localhost:7860

### Step 2: Setup Your Environment

Navigate to the **🔧 Setup & Connection** tab.

#### Test OpenSearch Connection
1. Click **Test Connection** button
2. Verify you see: ✅ Successfully connected to OpenSearch!
3. Check the cluster information displayed

#### Load Sample Data
1. Click **Load Data** button
2. This will:
   - Create two indices: `learning_points` and `learning_locations`
   - Load 100 US cities as GeoPoint documents
   - Create sample polygon shapes as GeoShape documents
3. Review the sample data preview

---

## Module 1: GeoPoint Basics (📍 Tab)

### What You'll Learn
- GeoPoint data type fundamentals
- GeoJSON coordinate format
- Converting city names to coordinates

### Activities

#### 1. Learn the Concept
Click **Show Explanation** to see:
- What is a GeoPoint?
- GeoJSON format: `[longitude, latitude]`
- Common use cases
- Sample city coordinates

#### 2. Create Your Own GeoPoint
1. Enter a city name (e.g., "Los Angeles", "Chicago")
2. Click **Create GeoPoint**
3. View the generated GeoJSON:
```json
{
  "type": "Point",
  "coordinates": [-118.2437, 34.0522]
}
```

### Key Takeaways
- ⚠️ **Longitude comes first**: `[lon, lat]` not `[lat, lon]`
- Longitude ranges from -180° to 180° (West to East)
- Latitude ranges from -90° to 90° (South to North)

---

## Module 2: GeoPoint Queries (🔍 Tab)

### Query Type 1: Bounding Box

**What It Does**: Finds all points within a rectangular area.

#### How to Use
1. Navigate to **Bounding Box Query** sub-tab
2. Define your search area:
   - **Top-Left**: Northwest corner `[longitude, latitude]`
   - **Bottom-Right**: Southeast corner `[longitude, latitude]`

#### Try These Examples

**Example 1: California Cities**
```
Top-Left: [-124.4096, 42.0095]
Bottom-Right: [-114.1312, 32.5343]
```

**Example 2: East Coast Cities**
```
Top-Left: [-80.0, 45.0]
Bottom-Right: [-70.0, 35.0]
```

**Example 3: Texas Cities**
```
Top-Left: [-106.65, 36.5]
Bottom-Right: [-93.5, 25.85]
```

#### Understanding the Results
- **Text Output**: List of cities found with their coordinates
- **Map Visualization**: 
  - Red rectangle = search area (bounding box)
  - Blue markers = cities found within the box

### Query Type 2: Distance Search

**What It Does**: Finds all points within a radius of a center point.

#### How to Use
1. Navigate to **Distance Query** sub-tab
2. Enter a **Center City** (e.g., "New York")
3. Set **Distance** in miles using the slider

#### Try These Examples

**Example 1: Cities Near New York**
```
Center City: New York
Distance: 100 miles
```

**Example 2: Cities Near Los Angeles**
```
Center City: Los Angeles
Distance: 200 miles
```

**Example 3: Cities Near Chicago**
```
Center City: Chicago
Distance: 150 miles
```

#### Understanding the Results
- **Text Output**: Cities found within the specified radius
- **Map Visualization**:
  - Red marker = center point
  - Green circle = search radius
  - Blue markers = cities within radius

---

## Module 3: GeoShape Basics (🗺️ Tab)

### What You'll Learn
- GeoShape data type for complex shapes
- Creating polygons with multiple vertices
- Difference between GeoPoint and GeoShape

### Activities

#### 1. Learn About GeoShape
Click **Show Explanation** to see:
- What is a GeoShape?
- Polygon structure
- LineString format
- Use cases (delivery zones, boundaries, geofences)

#### 2. View Sample Polygon
Review the sample polygon GeoJSON:
```json
{
  "type": "Polygon",
  "coordinates": [[
    [-122.4194, 37.7749],  // San Francisco
    [-118.2437, 34.0522],  // Los Angeles
    [-121.8863, 37.3382],  // San Jose
    [-122.4194, 37.7749]   // Close the polygon!
  ]]
}
```

### Key Takeaways
- Polygons must **close** (first point = last point)
- Coordinates are still `[longitude, latitude]`
- Use cases: delivery zones, restricted areas, city boundaries

---

## Module 4: GeoShape Queries (🔎 Tab)

### Bounding Box Query on Polygons

**What It Does**: Finds polygons that intersect with a rectangular area.

#### How to Use
1. Enter a **Polygon Name** (optional, for reference)
2. Define the bounding box:
   - Top-Left corner
   - Bottom-Right corner
3. Click **Run GeoShape Query**

#### Try This Example

**Search for California Polygons**
```
Polygon Name: California Triangle
Top-Left: [-124.0, 42.0]
Bottom-Right: [-114.0, 32.0]
```

#### Understanding the Results
- **Text Output**: Polygons that intersect with the box
- **Map Visualization**:
  - Red rectangle = search bounding box
  - Purple polygon = found polygon shapes

---

## Common Queries Reference

### Finding Cities in a Region

**New England States**
```
Bounding Box:
Top-Left: [-73.5, 47.5]
Bottom-Right: [-66.9, 41.0]
```

**Pacific Northwest**
```
Bounding Box:
Top-Left: [-125.0, 49.0]
Bottom-Right: [-116.0, 42.0]
```

**Florida**
```
Bounding Box:
Top-Left: [-87.6, 31.0]
Bottom-Right: [-80.0, 24.5]
```

### Finding Nearby Cities

**Cities Near Major Hubs**
- Seattle: 150 miles radius
- Denver: 200 miles radius
- Miami: 100 miles radius
- Boston: 125 miles radius

---

## Tips & Best Practices

### 1. Map Navigation
- **Zoom**: Use mouse wheel or +/- buttons
- **Pan**: Click and drag the map
- **Markers**: Click on city markers to see names

### 2. Coordinate Input
- Use negative values for West longitude (USA)
- Use positive values for North latitude (USA)
- Example: New York = `[-74.0060, 40.7128]`

### 3. Query Optimization
- Start with smaller bounding boxes for faster results
- Use distance queries for circular search areas
- Use bounding box for rectangular regions

### 4. Understanding Results
- **Total Count**: Number of matches found
- **Preview**: First 10 results displayed
- **Map**: Visual representation of all results

---

## Troubleshooting

### No Results Found
- **Check coordinates**: Verify longitude/latitude order
- **Expand search area**: Increase bounding box or distance
- **Verify data**: Ensure data was loaded in Setup tab

### Connection Errors
```bash
# Test OpenSearch is running
curl -k -u admin:Developer@123 https://localhost:9200

# Should return cluster information
```

### Map Not Displaying
- **Check browser console**: Look for JavaScript errors
- **Reload page**: Refresh the application
- **Clear cache**: Try incognito/private mode

### Slow Query Performance
- **Reduce search area**: Use smaller bounding boxes
- **Limit distance**: Start with smaller radius searches
- **Check cluster**: Verify OpenSearch is not overloaded

---

## Advanced Exercises

### Exercise 1: Multi-City Distance Search
1. Pick 3 different cities
2. Run distance queries with varying radii
3. Compare which cities have more neighbors

### Exercise 2: Coast-to-Coast Bounding Box
1. Create a bounding box spanning entire USA
2. Gradually narrow it to find specific regions
3. Identify which region has most cities

### Exercise 3: Custom Polygon Creation
1. Pick 4-5 cities forming a region
2. Get their coordinates
3. Create a custom polygon in GeoJSON format
4. Use it to query the index

---

## Next Steps

After completing this tutorial, you can:

1. **Explore the Notebook**: Review `geo_spatial_data.ipynb` for code details
2. **Modify Queries**: Edit `app.py` to add new query types
3. **Add Features**: Extend the app with heatmaps, clustering, etc.
4. **Real Data**: Load your own geospatial datasets
5. **Production**: Deploy to production with proper security

---

## Resources

- [OpenSearch Geospatial Documentation](https://opensearch.org/docs/latest/search-plugins/geographic-and-xy/)
- [GeoJSON Specification](https://geojson.org/)
- [Gradio Documentation](https://gradio.app/docs/)
- [Folium Maps Documentation](https://python-visualization.github.io/folium/)

## Need Help?

- Check the **Setup & Connection** tab for cluster status
- Review error messages in the UI
- Inspect browser console for JavaScript errors
- Verify OpenSearch logs for query errors
