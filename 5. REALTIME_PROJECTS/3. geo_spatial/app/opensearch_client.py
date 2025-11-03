"""OpenSearch client wrapper for geospatial operations"""

from opensearchpy import OpenSearch, helpers
from typing import Dict, List, Any, Optional
import config


class OpenSearchGeoClient:
    """Wrapper class for OpenSearch geospatial operations"""
    
    def __init__(self):
        """Initialize OpenSearch client"""
        if config.USE_SSL:
            self.client = OpenSearch(
                hosts=[{'host': config.OPENSEARCH_HOST, 'port': config.OPENSEARCH_PORT}],
                http_auth=(config.USERNAME, config.PASSWORD),
                use_ssl=True,
                verify_certs=config.VERIFY_CERTS,
                ssl_show_warn=False
            )
        else:
            self.client = OpenSearch(
                hosts=[{'host': config.OPENSEARCH_HOST, 'port': config.OPENSEARCH_PORT}],
                use_ssl=False,
                verify_certs=False,
                ssl_assert_hostname=False,
                ssl_show_warn=False
            )
    
    def test_connection(self) -> tuple[bool, str]:
        """Test OpenSearch connection"""
        try:
            info = self.client.info()
            return True, f"Connected to OpenSearch {info['version']['number']}"
        except Exception as e:
            return False, f"Connection failed: {str(e)}"
    
    def create_geopoint_index(self, index_name: str = config.GEOPOINT_INDEX) -> tuple[bool, str]:
        """Create index with geo_point mapping"""
        try:
            if self.client.indices.exists(index=index_name):
                self.client.indices.delete(index=index_name)
            
            mapping = {
                "mappings": {
                    "properties": {
                        "GeoJSON": {"type": "geo_point"},
                        "CITY": {"type": "text"},
                        "STATE_CODE": {"type": "keyword"}
                    }
                }
            }
            
            self.client.indices.create(index=index_name, body=mapping)
            return True, f"Created index '{index_name}' with geo_point mapping"
        except Exception as e:
            return False, f"Failed to create index: {str(e)}"
    
    def create_geoshape_index(self, index_name: str = config.GEOSHAPE_INDEX) -> tuple[bool, str]:
        """Create index with geo_shape mapping"""
        try:
            if self.client.indices.exists(index=index_name):
                self.client.indices.delete(index=index_name)
            
            mapping = {
                "mappings": {
                    "properties": {
                        "geoshape_geojson": {"type": "geo_shape"},
                        "name": {"type": "text"},
                        "description": {"type": "text"}
                    }
                }
            }
            
            self.client.indices.create(index=index_name, body=mapping)
            return True, f"Created index '{index_name}' with geo_shape mapping"
        except Exception as e:
            return False, f"Failed to create index: {str(e)}"
    
    def bulk_load_points(self, documents: List[Dict], index_name: str = config.GEOPOINT_INDEX) -> tuple[int, str]:
        """Bulk load GeoPoint documents"""
        try:
            actions = [
                {
                    "_index": index_name,
                    "_source": doc,
                    "_id": doc.get("ID", None)
                }
                for doc in documents
            ]
            
            success, errors = helpers.bulk(
                self.client, 
                actions,
                raise_on_error=False,
                raise_on_exception=False
            )
            
            return success, f"Loaded {success} documents"
        except Exception as e:
            return 0, f"Bulk load failed: {str(e)}"
    
    def bulk_load_shapes(self, documents: List[Dict], index_name: str = config.GEOSHAPE_INDEX) -> tuple[int, str]:
        """Bulk load GeoShape documents"""
        return self.bulk_load_points(documents, index_name)
    
    def geo_bounding_box_query(
        self, 
        top_left: List[float], 
        bottom_right: List[float],
        field: str = "GeoJSON",
        index_name: str = config.GEOPOINT_INDEX
    ) -> tuple[List[Dict], str]:
        """Execute geo_bounding_box query"""
        try:
            query = {
                "query": {
                    "bool": {
                        "must": {"match_all": {}},
                        "filter": {
                            "geo_bounding_box": {
                                field: {
                                    "top_left": top_left,
                                    "bottom_right": bottom_right
                                }
                            }
                        }
                    }
                }
            }
            
            response = self.client.search(index=index_name, body=query, size=1000)
            hits = response["hits"]["hits"]
            results = [hit["_source"] for hit in hits]
            
            return results, f"Found {len(results)} results"
        except Exception as e:
            return [], f"Query failed: {str(e)}"
    
    def geo_distance_query(
        self,
        center: List[float],
        distance: str,
        field: str = "GeoJSON",
        index_name: str = config.GEOPOINT_INDEX
    ) -> tuple[List[Dict], str]:
        """Execute geo_distance query"""
        try:
            query = {
                "query": {
                    "bool": {
                        "must": {"match_all": {}},
                        "filter": {
                            "geo_distance": {
                                "distance": distance,
                                field: center
                            }
                        }
                    }
                }
            }
            
            response = self.client.search(index=index_name, body=query, size=1000)
            hits = response["hits"]["hits"]
            results = [hit["_source"] for hit in hits]
            
            return results, f"Found {len(results)} results within {distance}"
        except Exception as e:
            return [], f"Query failed: {str(e)}"
    
    def count_documents(self, index_name: str) -> int:
        """Count documents in index"""
        try:
            response = self.client.count(index=index_name)
            return response["count"]
        except:
            return 0
