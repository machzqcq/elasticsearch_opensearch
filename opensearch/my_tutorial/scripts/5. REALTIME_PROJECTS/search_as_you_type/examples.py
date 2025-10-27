"""
Example usage of the Search-as-you-Type API
Demonstrates how to call the API programmatically
"""
import httpx
import asyncio
from typing import List, Dict, Any


API_BASE_URL = "http://localhost:8000"


async def check_health() -> Dict[str, Any]:
    """Check API health status."""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{API_BASE_URL}/api/health")
        return response.json()


async def search_products(
    query: str,
    fields: List[str] = None,
    size: int = 10
) -> Dict[str, Any]:
    """
    Search for products.
    
    Args:
        query: Search query string
        fields: List of fields to search (defaults to common fields)
        size: Number of results to return
        
    Returns:
        Search results dictionary
    """
    if fields is None:
        fields = [
            "products.product_name",
            "products.category",
            "products.manufacturer"
        ]
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            f"{API_BASE_URL}/api/search",
            json={
                "query": query,
                "fields": fields,
                "size": size,
                "from": 0
            }
        )
        response.raise_for_status()
        return response.json()


async def get_suggestions(
    query: str,
    field: str = "products.product_name",
    size: int = 5
) -> List[str]:
    """
    Get autocomplete suggestions.
    
    Args:
        query: Partial query string
        field: Field to get suggestions from
        size: Number of suggestions
        
    Returns:
        List of suggestions
    """
    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.post(
            f"{API_BASE_URL}/api/suggestions",
            json={
                "query": query,
                "field": field,
                "size": size
            }
        )
        response.raise_for_status()
        data = response.json()
        return data.get("suggestions", [])


async def main():
    """Run example searches."""
    print("=" * 60)
    print("Search-as-you-Type API Examples")
    print("=" * 60)
    print()
    
    # 1. Health check
    print("1. Checking API health...")
    health = await check_health()
    print(f"   Status: {health['status']}")
    print(f"   Cluster: {health.get('cluster_status', 'N/A')}")
    print()
    
    # 2. Simple search
    print("2. Searching for 'shirt'...")
    results = await search_products("shirt", size=5)
    print(f"   Found {results['total']} results in {results['took']}ms")
    print(f"   Top result: ", end="")
    if results['hits']:
        first_hit = results['hits'][0]
        products = first_hit['source'].get('products', [])
        if products:
            print(products[0].get('product_name', 'N/A'))
    print()
    
    # 3. Category search
    print("3. Searching for 'Men's Clothing'...")
    results = await search_products("Men's Clothing", size=3)
    print(f"   Found {results['total']} results")
    for idx, hit in enumerate(results['hits'][:3], 1):
        products = hit['source'].get('products', [])
        if products:
            product = products[0]
            print(f"   {idx}. {product.get('product_name', 'N/A')} "
                  f"(€{product.get('price', 0):.2f})")
    print()
    
    # 4. Autocomplete suggestions
    print("4. Getting suggestions for 'boo'...")
    suggestions = await get_suggestions("boo")
    print(f"   Suggestions:")
    for idx, suggestion in enumerate(suggestions, 1):
        print(f"   {idx}. {suggestion}")
    print()
    
    # 5. Multi-field search
    print("5. Searching across multiple fields for 'blue'...")
    results = await search_products(
        "blue",
        fields=[
            "products.product_name",
            "products.category"
        ],
        size=3
    )
    print(f"   Found {results['total']} results")
    for idx, hit in enumerate(results['hits'][:3], 1):
        products = hit['source'].get('products', [])
        if products:
            product = products[0]
            print(f"   {idx}. {product.get('product_name', 'N/A')}")
            if hit.get('highlight'):
                print(f"      Highlighted: {hit['highlight']}")
    print()
    
    # 6. Manufacturer search
    print("6. Searching for manufacturer 'Elitelligence'...")
    results = await search_products(
        "Elitelligence",
        fields=["products.manufacturer"],
        size=3
    )
    print(f"   Found {results['total']} results")
    print()
    
    print("=" * 60)
    print("Examples completed successfully!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
