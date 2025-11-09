"""Data loading and preparation utilities"""

import pandas as pd
import chardet
from typing import List, Dict, Tuple
import config


def load_us_cities_data() -> Tuple[pd.DataFrame, str]:
    """Load and transform US cities data"""
    try:
        # Detect file encoding
        with open(config.DATA_PATH, 'rb') as f:
            result = chardet.detect(f.read())
        encoding = result['encoding']
        
        # Load CSV
        df = pd.read_csv(config.DATA_PATH, encoding=encoding)
        
        # Transform data
        df['LATITUDE'] = df['lat'].astype(float)
        df['LONGITUDE'] = df['lng'].astype(float)
        df["GeoJSON"] = df.apply(
            lambda x: {
                "type": "Point", 
                "coordinates": [x["LONGITUDE"], x["LATITUDE"]]
            }, 
            axis=1
        )
        
        # Rename columns
        df.rename(columns={
            "city": "CITY",
            "state_id": "STATE_CODE",
            "id": "ID"
        }, inplace=True)
        
        # Keep only needed columns
        df = df[["ID", "CITY", "STATE_CODE", "GeoJSON"]]
        
        return df, f"Loaded {len(df)} cities"
    except Exception as e:
        return pd.DataFrame(), f"Failed to load data: {str(e)}"


def create_polygon_from_cities(df: pd.DataFrame, cities_states: Dict[str, str]) -> Dict:
    """Create a polygon GeoShape from city coordinates"""
    try:
        # Extract rows for specified cities
        polygon_df = df[
            df.apply(
                lambda row: row['CITY'] in cities_states and 
                           row['STATE_CODE'] == cities_states[row['CITY']], 
                axis=1
            )
        ]
        
        # Extract coordinates
        coordinates = [
            row['GeoJSON']['coordinates'] 
            for _, row in polygon_df.iterrows()
        ]
        
        # Close the polygon
        coordinates.append(coordinates[0])
        
        # Create GeoJSON polygon
        geoshape = {
            "type": "Polygon",
            "coordinates": [coordinates]
        }
        
        return geoshape
    except Exception as e:
        raise ValueError(f"Failed to create polygon: {str(e)}")


def prepare_geopoint_documents(df: pd.DataFrame) -> List[Dict]:
    """Prepare documents for GeoPoint index"""
    return df.to_dict('records')


def prepare_geoshape_documents(df: pd.DataFrame, polygons: List[Dict]) -> List[Dict]:
    """Prepare documents for GeoShape index"""
    documents = []
    for i, polygon_info in enumerate(polygons):
        doc = {
            "ID": i,
            "name": polygon_info.get("name", f"Polygon {i}"),
            "description": polygon_info.get("description", ""),
            "geoshape_geojson": polygon_info["shape"]
        }
        documents.append(doc)
    return documents


def get_city_coordinates(df: pd.DataFrame, city: str, state: str) -> Tuple[float, float]:
    """Get coordinates for a specific city"""
    try:
        city_data = df[
            (df['CITY'] == city) & (df['STATE_CODE'] == state)
        ].iloc[0]
        coords = city_data['GeoJSON']['coordinates']
        return coords[0], coords[1]  # lon, lat
    except:
        return None, None


def lookup_city_coordinates(city_name: str) -> List[float]:
    """
    Lookup city coordinates by name only.
    Returns [lon, lat] or None if not found.
    First checks EXAMPLE_CITIES, then searches the database.
    """
    # Check EXAMPLE_CITIES first
    for city_key, coords_dict in config.EXAMPLE_CITIES.items():
        if city_name.lower() in city_key.lower():
            return [coords_dict['lon'], coords_dict['lat']]
    
    # If not in EXAMPLE_CITIES, search the database
    try:
        df, _ = load_us_cities_data()
        if not df.empty:
            # Try exact match first
            city_data = df[df['CITY'].str.lower() == city_name.lower()]
            if not city_data.empty:
                coords = city_data.iloc[0]['GeoJSON']['coordinates']
                return coords
            
            # Try partial match
            city_data = df[df['CITY'].str.contains(city_name, case=False, na=False)]
            if not city_data.empty:
                coords = city_data.iloc[0]['GeoJSON']['coordinates']
                return coords
    except:
        pass
    
    return None


def create_sample_polygons(df: pd.DataFrame) -> List[Dict]:
    """Create sample polygons for learning"""
    polygons = []
    
    # Polygon 1: Chicago - Buffalo - Raleigh - Cincinnati
    polygon1 = {
        "name": "Midwest-East Polygon",
        "description": "Polygon connecting Chicago, Buffalo, Raleigh, and Cincinnati",
        "cities": {
            'Chicago': 'IL',
            'Buffalo': 'NY',
            'Raleigh': 'NC',
            'Cincinnati': 'OH',
        }
    }
    polygon1["shape"] = create_polygon_from_cities(df, polygon1["cities"])
    polygons.append(polygon1)
    
    return polygons
