"""FastAPI application for search-as-you-type."""
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
from typing import List

from .models import (
    SearchRequest,
    SearchResponse,
    SuggestionRequest,
    SuggestionResponse,
    HealthResponse,
    SearchHit
)
from .opensearch_client import get_opensearch_client, OpenSearchClient
from .config import get_settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Search-as-you-Type API",
    description="Real-time search API with autocomplete functionality",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", tags=["Root"])
async def root():
    """Root endpoint with API information."""
    return {
        "name": "Search-as-you-Type API",
        "version": "1.0.0",
        "endpoints": {
            "search": "/api/search",
            "suggestions": "/api/suggestions",
            "health": "/api/health"
        }
    }


@app.get("/api/health", response_model=HealthResponse, tags=["Health"])
async def health_check(client: OpenSearchClient = Depends(get_opensearch_client)):
    """Check API and OpenSearch health."""
    health_info = client.health_check()
    return HealthResponse(**health_info)


@app.post("/api/search", response_model=SearchResponse, tags=["Search"])
async def search(
    request: SearchRequest,
    client: OpenSearchClient = Depends(get_opensearch_client)
):
    """
    Perform search-as-you-type query.
    
    This endpoint searches across multiple fields with support for:
    - Phrase prefix matching (for autocomplete)
    - Fuzzy matching (for typo tolerance)
    - Phrase matching with slop (for flexible phrase searches)
    - Highlighting of matched terms
    """
    try:
        results = client.search_as_you_type(
            query=request.query,
            fields=request.fields,
            size=request.size,
            from_=request.from_
        )
        
        # Transform results
        hits = []
        for hit in results.get("hits", {}).get("hits", []):
            hits.append(
                SearchHit(
                    id=hit["_id"],
                    score=hit["_score"],
                    source=hit["_source"],
                    highlight=hit.get("highlight")
                )
            )
        
        return SearchResponse(
            total=results["hits"]["total"]["value"],
            took=results["took"],
            hits=hits,
            query=request.query
        )
    except Exception as e:
        logger.error(f"Search error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")


@app.post("/api/suggestions", response_model=SuggestionResponse, tags=["Search"])
async def get_suggestions(
    request: SuggestionRequest,
    client: OpenSearchClient = Depends(get_opensearch_client)
):
    """
    Get autocomplete suggestions for a field.
    
    This endpoint provides real-time suggestions as the user types,
    helping to guide users to relevant search terms.
    """
    try:
        suggestions = client.get_suggestions(
            query=request.query,
            field=request.field,
            size=request.size
        )
        
        return SuggestionResponse(
            suggestions=suggestions,
            query=request.query
        )
    except Exception as e:
        logger.error(f"Suggestion error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Suggestion failed: {str(e)}")


@app.get("/api/search-fields", tags=["Metadata"])
async def get_search_fields():
    """Get available search fields."""
    return {
        "fields": [
            {
                "name": "products.product_name",
                "display_name": "Product Name",
                "description": "Name of the product"
            },
            {
                "name": "products.category",
                "display_name": "Product Category",
                "description": "Product category"
            },
            {
                "name": "products.manufacturer",
                "display_name": "Manufacturer",
                "description": "Product manufacturer"
            },
            {
                "name": "customer_full_name",
                "display_name": "Customer Name",
                "description": "Full name of the customer"
            },
            {
                "name": "category",
                "display_name": "Order Category",
                "description": "Overall order category"
            }
        ]
    }


if __name__ == "__main__":
    import uvicorn
    settings = get_settings()
    uvicorn.run(
        "backend.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=True
    )
