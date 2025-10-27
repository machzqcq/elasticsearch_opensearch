"""Gradio Interactive Learning App for OpenSearch Geospatial Queries"""

import gradio as gr
import pandas as pd
from typing import List, Dict
import json

from opensearch_client import OpenSearchGeoClient
from data_loader import (
    load_us_cities_data,
    prepare_geopoint_documents,
    prepare_geoshape_documents,
    get_city_coordinates,
    lookup_city_coordinates,
    create_sample_polygons
)
from visualizations import (
    visualize_geopoint_bounding_box,
    visualize_geopoint_distance,
    visualize_geoshape_query
)
import config


# Initialize OpenSearch client
os_client = OpenSearchGeoClient()


# ============================================================================
# TAB 1: SETUP & CONNECTION
# ============================================================================

def test_connection():
    """Test OpenSearch connection"""
    success, message = os_client.test_connection()
    if success:
        try:
            info = os_client.client.info()
            return f"✅ {message}", info
        except Exception as e:
            return f"✅ {message}", {"error": str(e)}
    else:
        return f"❌ {message}", {}


def setup_data():
    """Load data and create indices"""
    try:
        # Load US cities data
        df, load_msg = load_us_cities_data()
        
        if df.empty:
            return f"❌ {load_msg}", []
        
        # Create indices
        success_gp, msg_gp = os_client.create_geopoint_index()
        if not success_gp:
            return f"❌ Failed to create GeoPoint index: {msg_gp}", []
        
        success_gs, msg_gs = os_client.create_geoshape_index()
        if not success_gs:
            return f"❌ Failed to create GeoShape index: {msg_gs}", []
        
        # Prepare and load GeoPoint documents
        geopoint_docs = prepare_geopoint_documents(df.head(100))  # Load first 100 cities
        count_gp, msg_bulk = os_client.bulk_load_points(geopoint_docs)
        
        # Create sample polygons and prepare GeoShape documents
        sample_polygons = create_sample_polygons(df)
        geoshape_docs = prepare_geoshape_documents(df, sample_polygons)
        for doc in geoshape_docs:
            os_client.client.index(
                index=config.GEOSHAPE_INDEX,
                body=doc,
                refresh=True
            )
        
        return f"✅ Successfully loaded {count_gp} GeoPoint documents and {len(geoshape_docs)} GeoShape documents!", df.head(10).to_dict('records')
    
    except Exception as e:
        return f"❌ Error: {str(e)}", []


# ============================================================================
# TAB 2: GEOPOINT BASICS
# ============================================================================

def explain_geopoint():
    """Explain GeoPoint concept"""
    explanation = """
# 📍 GeoPoint Data Type

## What is GeoPoint?
A **GeoPoint** represents a single geographical location on Earth using latitude and longitude coordinates.

## GeoJSON Format
In OpenSearch, GeoPoint uses GeoJSON format:
```json
{
  "type": "Point",
  "coordinates": [longitude, latitude]
}
```

⚠️ **Important**: GeoJSON uses `[longitude, latitude]` order (not lat, lon!)

## Use Cases
- Store city locations
- Track user locations
- Map points of interest
- Delivery addresses
- Store/restaurant locations

## Example
New York City: `[-74.0060, 40.7128]`
- Longitude: -74.0060 (West)
- Latitude: 40.7128 (North)
    """
    
    # Get sample data
    df, load_msg = load_us_cities_data()
    if not df.empty:
        # Need to check if original columns exist
        sample_cols = []
        if 'CITY' in df.columns:
            sample_cols.append('CITY')
        if 'STATE_CODE' in df.columns:
            sample_cols.append('STATE_CODE')
        if 'LATITUDE' in df.columns:
            df['LAT'] = df['LATITUDE']
            sample_cols.append('LAT')
        if 'LONGITUDE' in df.columns:
            df['LNG'] = df['LONGITUDE']
            sample_cols.append('LNG')
        
        if sample_cols:
            sample = df.head(5)[sample_cols].to_dict('records')
        else:
            sample = df.head(5).to_dict('records')
    else:
        sample = []
    
    return explanation, sample


def create_geopoint_example(city_name: str):
    """Create GeoPoint from city name"""
    try:
        coords = lookup_city_coordinates(city_name)
        if coords:
            geopoint = {
                "type": "Point",
                "coordinates": coords
            }
            return f"✅ GeoPoint for {city_name}:", json.dumps(geopoint, indent=2)
        else:
            return f"❌ City '{city_name}' not found in database", ""
    except Exception as e:
        return f"❌ Error: {str(e)}", ""


# ============================================================================
# TAB 3: GEOPOINT QUERIES
# ============================================================================

def run_bounding_box_query(
    top_left_lon: float,
    top_left_lat: float,
    bottom_right_lon: float,
    bottom_right_lat: float
):
    """Execute geo_bounding_box query"""
    try:
        top_left = [top_left_lon, top_left_lat]
        bottom_right = [bottom_right_lon, bottom_right_lat]
        
        results, message = os_client.geo_bounding_box_query(
            field='GeoJSON',
            top_left=top_left,
            bottom_right=bottom_right
        )
        
        if not results:
            return f"❌ {message}", None
        
        # Create visualization
        map_html = visualize_geopoint_bounding_box(
            top_left,
            bottom_right,
            results
        )
        
        # Format results
        result_text = f"Found {len(results)} cities in bounding box:\n\n"
        for i, city in enumerate(results[:10], 1):
            result_text += f"{i}. {city['CITY']}, {city['STATE_CODE']} - {city['GeoJSON']['coordinates']}\n"
        
        return result_text, map_html
    
    except Exception as e:
        return f"❌ Error: {str(e)}", None


def run_distance_query(
    center_city: str,
    distance_miles: float
):
    """Execute geo_distance query"""
    try:
        coords = lookup_city_coordinates(center_city)
        if not coords:
            return f"❌ City '{center_city}' not found", None
        
        results, message = os_client.geo_distance_query(
            field='GeoJSON',
            center=coords,
            distance=f"{distance_miles}mi"
        )
        
        if not results:
            return f"❌ {message}", None
        
        # Create visualization
        map_html = visualize_geopoint_distance(
            coords,
            distance_miles,
            results
        )
        
        # Format results
        result_text = f"Found {len(results)} cities within {distance_miles} miles of {center_city}:\n\n"
        for i, city in enumerate(results[:10], 1):
            result_text += f"{i}. {city['CITY']}, {city['STATE_CODE']}\n"
        
        return result_text, map_html
    
    except Exception as e:
        return f"❌ Error: {str(e)}", None


# ============================================================================
# TAB 4: GEOSHAPE BASICS
# ============================================================================

def explain_geoshape():
    """Explain GeoShape concept"""
    explanation = """
# 🗺️ GeoShape Data Type

## What is GeoShape?
A **GeoShape** represents complex geographical shapes like polygons, lines, and multipolygons.

## Common GeoShape Types

### 1. Polygon
A closed shape with multiple vertices:
```json
{
  "type": "Polygon",
  "coordinates": [
    [
      [lon1, lat1],
      [lon2, lat2],
      [lon3, lat3],
      [lon1, lat1]  // Must close the polygon
    ]
  ]
}
```

### 2. LineString
A line connecting multiple points:
```json
{
  "type": "LineString",
  "coordinates": [[lon1, lat1], [lon2, lat2]]
}
```

## Use Cases
- Define delivery zones
- Mark restricted areas
- Draw boundaries (city limits, zip codes)
- Create geofences
- Map routes and paths

## Example: Triangle in California
```json
{
  "type": "Polygon",
  "coordinates": [[
    [-122.4194, 37.7749],  // San Francisco
    [-118.2437, 34.0522],  // Los Angeles
    [-121.8863, 37.3382],  // San Jose
    [-122.4194, 37.7749]   // Close polygon
  ]]
}
```
    """
    
    # Create sample polygon
    df, _ = load_us_cities_data()
    if not df.empty:
        polygons = create_sample_polygons(df)
        sample = polygons[0] if polygons else {}
    else:
        sample = {
            "name": "Example Polygon",
            "shape": {
                "type": "Polygon",
                "coordinates": [[
                    [-122.4194, 37.7749],
                    [-118.2437, 34.0522],
                    [-121.8863, 37.3382],
                    [-122.4194, 37.7749]
                ]]
            }
        }
    
    return explanation, json.dumps(sample, indent=2)


# ============================================================================
# TAB 5: GEOSHAPE QUERIES
# ============================================================================

def run_geoshape_bounding_box_query(
    polygon_name: str,
    top_left_lon: float,
    top_left_lat: float,
    bottom_right_lon: float,
    bottom_right_lat: float
):
    """Execute geo_bounding_box query on GeoShape"""
    try:
        top_left = [top_left_lon, top_left_lat]
        bottom_right = [bottom_right_lon, bottom_right_lat]
        
        # Query GeoShape index
        query = {
            "query": {
                "geo_bounding_box": {
                    "geoshape_geojson": {
                        "top_left": top_left,
                        "bottom_right": bottom_right
                    }
                }
            }
        }
        
        response = os_client.client.search(
            index=config.GEOSHAPE_INDEX,
            body=query
        )
        
        results = [hit['_source'] for hit in response['hits']['hits']]
        
        # Create visualization
        if results:
            map_html = visualize_geoshape_query(
                results[0]['geoshape_geojson'],
                'bounding_box',
                {'top_left': top_left, 'bottom_right': bottom_right},
                results
            )
        else:
            map_html = None
        
        result_text = f"Found {len(results)} polygons intersecting with bounding box:\n\n"
        for i, result in enumerate(results, 1):
            result_text += f"{i}. {result.get('name', 'Unnamed')}\n"
        
        return result_text, map_html
    
    except Exception as e:
        return f"❌ Error: {str(e)}", None


# ============================================================================
# GRADIO INTERFACE
# ============================================================================

def create_app():
    """Create Gradio application"""
    
    with gr.Blocks(title="OpenSearch Geospatial Learning App", theme=gr.themes.Soft()) as app:
        gr.Markdown("""
# 🌍 OpenSearch Geospatial Learning App
        
Welcome to the interactive learning app for OpenSearch Geospatial Queries!
        
This app teaches you:
- 📍 **GeoPoint**: Single location coordinates
- 🗺️ **GeoShape**: Complex polygons and shapes
- 🔍 **Geo Queries**: Bounding box and distance searches
        """)
        
        # ====================================================================
        # TAB 1: SETUP
        # ====================================================================
        with gr.Tab("🔧 Setup & Connection"):
            gr.Markdown("## Step 1: Test OpenSearch Connection")
            
            with gr.Row():
                test_btn = gr.Button("Test Connection", variant="primary")
            
            connection_output = gr.Textbox(label="Connection Status", lines=2)
            cluster_info = gr.JSON(label="Cluster Information")
            
            test_btn.click(
                fn=test_connection,
                outputs=[connection_output, cluster_info]
            )
            
            gr.Markdown("## Step 2: Load Sample Data")
            gr.Markdown("This will create indices and load US cities data.")
            
            with gr.Row():
                setup_btn = gr.Button("Load Data", variant="primary")
            
            setup_output = gr.Textbox(label="Setup Status", lines=2)
            sample_data = gr.JSON(label="Sample Data Preview")
            
            setup_btn.click(
                fn=setup_data,
                outputs=[setup_output, sample_data]
            )
        
        # ====================================================================
        # TAB 2: GEOPOINT BASICS
        # ====================================================================
        with gr.Tab("📍 GeoPoint Basics"):
            with gr.Row():
                with gr.Column():
                    gr.Markdown("### Learn About GeoPoint")
                    explain_btn = gr.Button("Show Explanation", variant="primary")
                    explanation_output = gr.Markdown()
                    sample_output = gr.JSON(label="Sample Cities")
                    
                    explain_btn.click(
                        fn=explain_geopoint,
                        outputs=[explanation_output, sample_output]
                    )
                
                with gr.Column():
                    gr.Markdown("### Create GeoPoint")
                    city_input = gr.Textbox(
                        label="Enter City Name",
                        value="New York",
                        placeholder="e.g., Los Angeles"
                    )
                    create_btn = gr.Button("Create GeoPoint", variant="primary")
                    status_output = gr.Textbox(label="Status")
                    geopoint_output = gr.Code(label="GeoJSON Output", language="json")
                    
                    create_btn.click(
                        fn=create_geopoint_example,
                        inputs=[city_input],
                        outputs=[status_output, geopoint_output]
                    )
        
        # ====================================================================
        # TAB 3: GEOPOINT QUERIES
        # ====================================================================
        with gr.Tab("🔍 GeoPoint Queries"):
            gr.Markdown("## Query GeoPoint Data")
            
            with gr.Tab("Bounding Box Query"):
                gr.Markdown("""
### 📦 Geo Bounding Box Query
Find all points within a rectangular area defined by top-left and bottom-right corners.
                
**Example**: California area
- Top-Left: [-124.4096, 42.0095] (Northwest corner)
- Bottom-Right: [-114.1312, 32.5343] (Southeast corner)
                """)
                
                with gr.Row():
                    with gr.Column():
                        tl_lon = gr.Number(label="Top-Left Longitude", value=-124.4096)
                        tl_lat = gr.Number(label="Top-Left Latitude", value=42.0095)
                    with gr.Column():
                        br_lon = gr.Number(label="Bottom-Right Longitude", value=-114.1312)
                        br_lat = gr.Number(label="Bottom-Right Latitude", value=32.5343)
                
                bbox_btn = gr.Button("Run Bounding Box Query", variant="primary")
                bbox_result = gr.Textbox(label="Query Results", lines=10)
                bbox_map = gr.HTML(label="Map Visualization")
                
                bbox_btn.click(
                    fn=run_bounding_box_query,
                    inputs=[tl_lon, tl_lat, br_lon, br_lat],
                    outputs=[bbox_result, bbox_map]
                )
            
            with gr.Tab("Distance Query"):
                gr.Markdown("""
### 📏 Geo Distance Query
Find all points within a specified distance from a center point.
                
**Example**: Find cities within 100 miles of New York
                """)
                
                center_city = gr.Textbox(
                    label="Center City",
                    value="New York",
                    placeholder="e.g., Los Angeles"
                )
                distance = gr.Slider(
                    label="Distance (miles)",
                    minimum=10,
                    maximum=500,
                    value=100,
                    step=10
                )
                
                dist_btn = gr.Button("Run Distance Query", variant="primary")
                dist_result = gr.Textbox(label="Query Results", lines=10)
                dist_map = gr.HTML(label="Map Visualization")
                
                dist_btn.click(
                    fn=run_distance_query,
                    inputs=[center_city, distance],
                    outputs=[dist_result, dist_map]
                )
        
        # ====================================================================
        # TAB 4: GEOSHAPE BASICS
        # ====================================================================
        with gr.Tab("🗺️ GeoShape Basics"):
            gr.Markdown("### Learn About GeoShape")
            geoshape_explain_btn = gr.Button("Show Explanation", variant="primary")
            geoshape_explanation = gr.Markdown()
            geoshape_sample = gr.Code(label="Sample Polygon (GeoJSON)", language="json")
            
            geoshape_explain_btn.click(
                fn=explain_geoshape,
                outputs=[geoshape_explanation, geoshape_sample]
            )
        
        # ====================================================================
        # TAB 5: GEOSHAPE QUERIES
        # ====================================================================
        with gr.Tab("🔎 GeoShape Queries"):
            gr.Markdown("""
## Query GeoShape Data
            
Search for polygons that intersect with a bounding box.
            """)
            
            polygon_name = gr.Textbox(label="Polygon Name (optional)", value="California Triangle")
            
            with gr.Row():
                with gr.Column():
                    gs_tl_lon = gr.Number(label="Top-Left Longitude", value=-124.0)
                    gs_tl_lat = gr.Number(label="Top-Left Latitude", value=42.0)
                with gr.Column():
                    gs_br_lon = gr.Number(label="Bottom-Right Longitude", value=-114.0)
                    gs_br_lat = gr.Number(label="Bottom-Right Latitude", value=32.0)
            
            geoshape_btn = gr.Button("Run GeoShape Query", variant="primary")
            geoshape_result = gr.Textbox(label="Query Results", lines=10)
            geoshape_map = gr.HTML(label="Map Visualization")
            
            geoshape_btn.click(
                fn=run_geoshape_bounding_box_query,
                inputs=[polygon_name, gs_tl_lon, gs_tl_lat, gs_br_lon, gs_br_lat],
                outputs=[geoshape_result, geoshape_map]
            )
    
    return app


if __name__ == "__main__":
    app = create_app()
    app.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False
    )
