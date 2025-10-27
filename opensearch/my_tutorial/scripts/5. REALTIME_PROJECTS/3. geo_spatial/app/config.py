"""Configuration settings for the Geospatial Learning App"""

import os

# OpenSearch Connection Settings
OPENSEARCH_HOST = "localhost"
OPENSEARCH_PORT = 9200
USE_SSL = True
VERIFY_CERTS = False
USERNAME = "admin"
PASSWORD = "Developer@123"

# Data Settings
# Get absolute path to data file
_CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(_CURRENT_DIR)))))
DATA_PATH = os.path.join(_PROJECT_ROOT, "data", "uscities.csv")

# Index Names
GEOPOINT_INDEX = "learning_points"
GEOSHAPE_INDEX = "learning_locations"

# App Settings
APP_TITLE = "🌍 OpenSearch Geospatial Learning App"
APP_DESCRIPTION = """
Learn OpenSearch geospatial queries through interactive examples!

This app demonstrates GeoPoint and GeoShape queries with real US cities data.
"""

# Map Settings
DEFAULT_MAP_CENTER = [39.8283, -98.5795]  # Center of USA
DEFAULT_ZOOM = 4

# Query Examples
EXAMPLE_CITIES = {
    "Chicago, IL": {"lat": 41.8375, "lon": -87.6866},
    "Raleigh, NC": {"lat": 35.8324, "lon": -78.6429},
    "Richmond, VA": {"lat": 37.5295, "lon": -77.4756},
    "Minneapolis, MN": {"lat": 44.9635, "lon": -93.2678},
    "Norfolk, VA": {"lat": 36.8945, "lon": -76.259},
    "Buffalo, NY": {"lat": 42.9018, "lon": -78.8487},
    "Cincinnati, OH": {"lat": 39.1413, "lon": -84.506},
}
