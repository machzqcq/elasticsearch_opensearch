# 🌍 Geospatial Learning App

An interactive Gradio-based application for learning OpenSearch geospatial queries and concepts.

## Features

- **Interactive Map Visualizations**: See GeoPoint and GeoShape queries in action
- **Step-by-Step Learning**: Learn concepts progressively from basic to advanced
- **Live Query Execution**: Run real OpenSearch queries against a live cluster
- **Visual Feedback**: See query results on interactive maps
- **Hands-on Practice**: Try different queries and see immediate results

## Prerequisites

- Python 3.10 or higher
- OpenSearch cluster running (default: localhost:9200)
- `uv` package manager installed

## Installation

1. **Install uv** (if not already installed):
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

2. **Install dependencies**:
```bash
uv sync
```

3. **Prepare data**:
Ensure the US cities CSV file is available at:
```
../../../../data/uscities.csv
```

## Running the App

```bash
uv run python app.py
```

The app will start on `http://localhost:7860`

## Configuration

Edit the OpenSearch connection settings in `config.py`:

```python
OPENSEARCH_HOST = "localhost"
OPENSEARCH_PORT = 9200
USE_SSL = True
VERIFY_CERTS = False
USERNAME = "admin"
PASSWORD = "Developer@123"
```

## Learning Modules

1. **GeoPoint Basics**
   - Understanding coordinate systems
   - Creating GeoJSON points
   - Indexing geospatial data

2. **GeoPoint Queries**
   - `geo_bounding_box`: Find points in a rectangle
   - `geo_distance`: Find points within a radius

3. **GeoShape Basics**
   - Creating polygons
   - Understanding complex shapes
   - GeoShape vs GeoPoint

4. **GeoShape Queries**
   - Bounding box queries on shapes
   - Distance queries on shapes
   - Shape intersections

## Project Structure

```
.
├── app.py                 # Main Gradio application
├── config.py             # Configuration settings
├── opensearch_client.py  # OpenSearch client wrapper
├── data_loader.py        # Data loading and preparation
├── query_builder.py      # Query construction helpers
├── visualizations.py     # Map and chart generation
├── pyproject.toml        # Project dependencies
└── README.md            # This file
```

## Troubleshooting

### OpenSearch Connection Error
- Verify OpenSearch is running: `curl -k -u admin:password https://localhost:9200`
- Check credentials in `config.py`

### Missing Data File
- Download from: https://simplemaps.com/data/us-cities
- Place in: `../../../../data/uscities.csv`

### Port Already in Use
- Change port in `app.py`: `demo.launch(server_port=7861)`

## License

MIT License
