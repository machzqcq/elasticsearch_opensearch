"""OpenSearch client and search operations."""
from opensearchpy import OpenSearch
from typing import List, Dict, Any, Optional
import logging
from .config import get_settings

logger = logging.getLogger(__name__)


class OpenSearchClient:
    """OpenSearch client wrapper for search operations."""
    
    def __init__(self):
        """Initialize OpenSearch client."""
        settings = get_settings()
        
        self.client = OpenSearch(
            hosts=[settings.opensearch_host],
            http_auth=(settings.opensearch_username, settings.opensearch_password),
            use_ssl=True,
            verify_certs=settings.opensearch_verify_ssl,
            ssl_show_warn=False,
        )
        self.index_name = settings.opensearch_index
        
    def search_as_you_type(
        self,
        query: str,
        fields: List[str],
        size: int = 10,
        from_: int = 0,
    ) -> Dict[str, Any]:
        """
        Perform search-as-you-type query across multiple fields.
        
        Args:
            query: Search query string
            fields: List of fields to search in
            size: Number of results to return
            from_: Starting offset for pagination
            
        Returns:
            Search results with hits and aggregations
        """
        if not query or not query.strip():
            return {"hits": {"total": {"value": 0}, "hits": []}, "took": 0}
        
        # Build multi-match query for search-as-you-type
        search_body = {
            "query": {
                "bool": {
                    "should": [
                        {
                            "multi_match": {
                                "query": query,
                                "fields": fields,
                                "type": "phrase_prefix",
                                "boost": 2.0
                            }
                        },
                        {
                            "multi_match": {
                                "query": query,
                                "fields": fields,
                                "type": "best_fields",
                                "fuzziness": "AUTO"
                            }
                        },
                        {
                            "multi_match": {
                                "query": query,
                                "fields": fields,
                                "type": "phrase",
                                "slop": 2,
                                "boost": 1.5
                            }
                        }
                    ]
                }
            },
            "size": size,
            "from": from_,
            "_source": {
                "includes": [
                    "products.product_name",
                    "products.category",
                    "products.manufacturer",
                    "products.price",
                    "category",
                    "manufacturer",
                    "customer_full_name",
                    "order_date"
                ]
            },
            "highlight": {
                "fields": {field: {} for field in fields},
                "pre_tags": ["<mark>"],
                "post_tags": ["</mark>"]
            }
        }
        
        try:
            response = self.client.search(
                index=self.index_name,
                body=search_body
            )
            return response
        except Exception as e:
            logger.error(f"Search error: {str(e)}")
            raise
    
    def get_suggestions(
        self,
        query: str,
        field: str,
        size: int = 5
    ) -> List[str]:
        """
        Get autocomplete suggestions for a specific field.
        
        Args:
            query: Partial query string
            field: Field to get suggestions from
            size: Number of suggestions to return
            
        Returns:
            List of suggestion strings
        """
        if not query or not query.strip():
            return []
        
        search_body = {
            "query": {
                "match_phrase_prefix": {
                    field: {
                        "query": query,
                        "max_expansions": 10
                    }
                }
            },
            "size": size,
            "_source": [field],
            "collapse": {
                "field": f"{field}.keyword"
            }
        }
        
        try:
            response = self.client.search(
                index=self.index_name,
                body=search_body
            )
            
            suggestions = []
            for hit in response.get("hits", {}).get("hits", []):
                source = hit.get("_source", {})
                if field in source:
                    suggestions.append(source[field])
            
            return list(set(suggestions))[:size]
        except Exception as e:
            logger.error(f"Suggestion error: {str(e)}")
            return []
    
    def health_check(self) -> Dict[str, Any]:
        """Check OpenSearch cluster health."""
        try:
            health = self.client.cluster.health()
            return {
                "status": "healthy",
                "cluster_status": health.get("status"),
                "number_of_nodes": health.get("number_of_nodes")
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e)
            }


# Singleton instance
_client: Optional[OpenSearchClient] = None


def get_opensearch_client() -> OpenSearchClient:
    """Get or create OpenSearch client instance."""
    global _client
    if _client is None:
        _client = OpenSearchClient()
    return _client
