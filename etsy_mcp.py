import os
import httpx
from fastmcp import FastMCP

# Initialize FastMCP Server
mcp = FastMCP(
    "Etsy Store Manager",
    description="Manage Etsy shop listings, check API connection, and retrieve store details.",
)

ETSY_API_BASE = "https://openapi.etsy.com"
ETSY_KEYSTRING = os.getenv("ETSY_KEYSTRING", "jymzktxl4g6unybpjp3944e3")
ETSY_SHARED_SECRET = os.getenv("ETSY_SHARED_SECRET", "ain5jyhmja")
ETSY_ACCESS_TOKEN = os.getenv("ETSY_ACCESS_TOKEN", "")

def get_headers(need_oauth: bool = False) -> dict:
    headers = {
        "x-api-key": f"{ETSY_KEYSTRING}:{ETSY_SHARED_SECRET}",
        "Accept": "application/json",
    }
    if need_oauth and ETSY_ACCESS_TOKEN:
        headers["Authorization"] = f"Bearer {ETSY_ACCESS_TOKEN}"
    return headers

@mcp.tool()
async def ping_etsy() -> dict:
    """Verify connectivity to Etsy Open API v3 and get your application ID."""
    url = f"{ETSY_API_BASE}/v3/application/openapi-ping"
    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=get_headers())
        if response.status_code == 200:
            return response.json()
        return {"error": f"HTTP {response.status_code}", "details": response.text}

@mcp.tool()
async def get_seller_taxonomy() -> dict:
    """Get the seller taxonomy categories to find valid category IDs for your products."""
    url = f"{ETSY_API_BASE}/v3/application/seller-taxonomy/nodes"
    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=get_headers())
        if response.status_code == 200:
            return response.json()
        return {"error": f"HTTP {response.status_code}", "details": response.text}

@mcp.tool()
async def get_shop(shop_id: int) -> dict:
    """Retrieve public details for an Etsy shop by its numeric shop ID."""
    url = f"{ETSY_API_BASE}/v3/application/shops/{shop_id}"
    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=get_headers())
        if response.status_code == 200:
            return response.json()
        return {"error": f"HTTP {response.status_code}", "details": response.text}

@mcp.tool()
async def get_shop_listings(shop_id: int, state: str = "active", limit: int = 25) -> dict:
    """Get listings for an Etsy shop. State can be 'active', 'draft', or 'expired'."""
    url = f"{ETSY_API_BASE}/v3/application/shops/{shop_id}/listings"
    params = {"state": state, "limit": limit}
    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=get_headers(need_oauth=True), params=params)
        if response.status_code == 200:
            return response.json()
        return {"error": f"HTTP {response.status_code}", "details": response.text}

@mcp.tool()
async def get_shipping_profiles(shop_id: int) -> dict:
    """List shipping profiles configured for an Etsy shop."""
    url = f"{ETSY_API_BASE}/v3/application/shops/{shop_id}/shipping-profiles"
    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=get_headers(need_oauth=True))
        if response.status_code == 200:
            return response.json()
        return {"error": f"HTTP {response.status_code}", "details": response.text}

@mcp.tool()
async def create_draft_listing(
    shop_id: int,
    title: str,
    description: str,
    price: float,
    quantity: int,
    taxonomy_id: int,
    who_made: str = "i_did",
    when_made: str = "2020_2026",
    item_type: str = "physical",
    shipping_profile_id: int = None,
) -> dict:
    """Create a draft product listing in your Etsy shop."""
    url = f"{ETSY_API_BASE}/v3/application/shops/{shop_id}/listings"
    payload = {
        "title": title,
        "description": description,
        "price": price,
        "quantity": quantity,
        "who_made": who_made,
        "when_made": when_made,
        "taxonomy_id": taxonomy_id,
        "type": item_type,
    }
    if shipping_profile_id:
        payload["shipping_profile_id"] = shipping_profile_id

    async with httpx.AsyncClient() as client:
        response = await client.post(url, headers=get_headers(need_oauth=True), json=payload)
        if response.status_code in (200, 201):
            return response.json()
        return {"error": f"HTTP {response.status_code}", "details": response.text}

# FastMCP ASGI application exposing both /mcp and /sse
app = mcp.http_app()

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
