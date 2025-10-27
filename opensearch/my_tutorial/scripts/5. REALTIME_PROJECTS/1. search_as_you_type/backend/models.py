"""Pydantic models for API requests and responses."""
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional


class SearchRequest(BaseModel):
    """Request model for search-as-you-type."""
    query: str = Field(..., description="Search query string", min_length=1)
    fields: List[str] = Field(
        default=["products.product_name", "products.category", "products.manufacturer"],
        description="Fields to search in"
    )
    size: int = Field(default=10, ge=1, le=100, description="Number of results")
    from_: int = Field(default=0, ge=0, alias="from", description="Offset for pagination")


class SuggestionRequest(BaseModel):
    """Request model for autocomplete suggestions."""
    query: str = Field(..., description="Partial query string", min_length=1)
    field: str = Field(
        default="products.product_name",
        description="Field to get suggestions from"
    )
    size: int = Field(default=5, ge=1, le=20, description="Number of suggestions")


class ProductInfo(BaseModel):
    """Product information model."""
    product_name: Optional[str] = None
    category: Optional[str] = None
    manufacturer: Optional[str] = None
    price: Optional[float] = None


class SearchHit(BaseModel):
    """Individual search result."""
    id: str
    score: float
    source: Dict[str, Any]
    highlight: Optional[Dict[str, List[str]]] = None


class SearchResponse(BaseModel):
    """Response model for search results."""
    total: int
    took: int
    hits: List[SearchHit]
    query: str


class SuggestionResponse(BaseModel):
    """Response model for suggestions."""
    suggestions: List[str]
    query: str


class HealthResponse(BaseModel):
    """Response model for health check."""
    status: str
    cluster_status: Optional[str] = None
    number_of_nodes: Optional[int] = None
    error: Optional[str] = None
