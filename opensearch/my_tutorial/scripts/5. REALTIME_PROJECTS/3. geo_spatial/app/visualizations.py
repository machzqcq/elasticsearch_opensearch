"""Map visualization utilities using Folium"""

import folium
from typing import List, Dict, Tuple
import config


def create_base_map(center: List[float] = None, zoom: int = None) -> folium.Map:
    """Create a base Folium map"""
    if center is None:
        center = config.DEFAULT_MAP_CENTER
    if zoom is None:
        zoom = config.DEFAULT_ZOOM
    
    m = folium.Map(
        location=center,
        zoom_start=zoom,
        tiles='OpenStreetMap'
    )
    return m


def add_points_to_map(m: folium.Map, points: List[Dict], color: str = 'blue') -> folium.Map:
    """Add GeoPoint markers to map"""
    for point in points:
        coords = point['GeoJSON']['coordinates']
        lat, lon = coords[1], coords[0]  # GeoJSON is [lon, lat]
        
        popup_text = f"{point.get('CITY', 'Unknown')}, {point.get('STATE_CODE', '')}"
        
        folium.CircleMarker(
            location=[lat, lon],
            radius=5,
            popup=popup_text,
            color=color,
            fill=True,
            fillColor=color,
            fillOpacity=0.7
        ).add_to(m)
    
    return m


def add_bounding_box_to_map(
    m: folium.Map, 
    top_left: List[float], 
    bottom_right: List[float]
) -> folium.Map:
    """Add bounding box rectangle to map"""
    # top_left and bottom_right are [lon, lat]
    bounds = [
        [top_left[1], top_left[0]],  # NW corner [lat, lon]
        [bottom_right[1], bottom_right[0]]  # SE corner [lat, lon]
    ]
    
    folium.Rectangle(
        bounds=bounds,
        color='red',
        fill=True,
        fillColor='red',
        fillOpacity=0.2,
        popup='Search Area (Bounding Box)'
    ).add_to(m)
    
    return m


def add_distance_circle_to_map(
    m: folium.Map,
    center: List[float],
    distance_miles: float
) -> folium.Map:
    """Add distance circle to map"""
    # center is [lon, lat]
    lat, lon = center[1], center[0]
    
    # Convert miles to meters
    radius_meters = distance_miles * 1609.34
    
    folium.Circle(
        location=[lat, lon],
        radius=radius_meters,
        color='green',
        fill=True,
        fillColor='green',
        fillOpacity=0.2,
        popup=f'Search Radius: {distance_miles} miles'
    ).add_to(m)
    
    # Add center marker
    folium.Marker(
        location=[lat, lon],
        popup='Center Point',
        icon=folium.Icon(color='red', icon='info-sign')
    ).add_to(m)
    
    return m


def add_polygon_to_map(m: folium.Map, polygon: Dict, color: str = 'purple') -> folium.Map:
    """Add GeoShape polygon to map"""
    if polygon['type'] == 'Polygon':
        # polygon['coordinates'] is [[[lon, lat], [lon, lat], ...]]
        coords = polygon['coordinates'][0]
        # Convert to [lat, lon] for Folium
        folium_coords = [[coord[1], coord[0]] for coord in coords]
        
        folium.Polygon(
            locations=folium_coords,
            color=color,
            fill=True,
            fillColor=color,
            fillOpacity=0.3,
            popup='Polygon Shape'
        ).add_to(m)
    
    return m


def visualize_geopoint_bounding_box(
    top_left: List[float],
    bottom_right: List[float],
    results: List[Dict]
) -> str:
    """Create map visualization for bounding box query"""
    # Calculate center for map
    center_lat = (top_left[1] + bottom_right[1]) / 2
    center_lon = (top_left[0] + bottom_right[0]) / 2
    
    m = create_base_map(center=[center_lat, center_lon], zoom=6)
    m = add_bounding_box_to_map(m, top_left, bottom_right)
    m = add_points_to_map(m, results, color='blue')
    
    return m._repr_html_()


def visualize_geopoint_distance(
    center: List[float],
    distance: float,
    results: List[Dict]
) -> str:
    """Create map visualization for distance query"""
    m = create_base_map(center=[center[1], center[0]], zoom=6)
    m = add_distance_circle_to_map(m, center, distance)
    m = add_points_to_map(m, results, color='blue')
    
    return m._repr_html_()


def visualize_geoshape_query(
    polygon: Dict,
    query_type: str,
    query_params: Dict,
    results: List[Dict]
) -> str:
    """Create map visualization for GeoShape query"""
    m = create_base_map(zoom=5)
    
    # Add the polygon
    m = add_polygon_to_map(m, polygon, color='purple')
    
    # Add query visualization
    if query_type == 'bounding_box':
        m = add_bounding_box_to_map(
            m, 
            query_params['top_left'], 
            query_params['bottom_right']
        )
    elif query_type == 'distance':
        m = add_distance_circle_to_map(
            m,
            query_params['center'],
            query_params['distance']
        )
    
    return m._repr_html_()
