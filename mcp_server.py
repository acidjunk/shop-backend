"""
MCP Server for the ShopVirge Backend API.

Exposes the key CRUD operations of the ShopVirge FastAPI backend as MCP tools,
allowing AI assistants (Claude Desktop, Claude Code, etc.) to interact with
shop data via natural language.

Usage:
    # Start the API server first:
    PYTHONPATH=. uvicorn server.main:app --reload --port 8080

    # Run the MCP server (stdio transport):
    python mcp_server.py

    # Or test interactively with the MCP inspector:
    mcp dev mcp_server.py

Environment variables:
    SHOP_API_BASE_URL  - Base URL of the running API (default: http://localhost:8080)
    SHOP_API_TOKEN     - Optional JWT token for authenticated endpoints
"""

import json
import os
from typing import Any, Optional

import httpx
from mcp.server.fastmcp import FastMCP

# --- Configuration ---

API_BASE_URL = os.environ.get("SHOP_API_BASE_URL", "http://localhost:8080")
API_TOKEN = os.environ.get("SHOP_API_TOKEN", "")

mcp = FastMCP(
    "ShopVirge Backend",
    instructions=(
        "MCP server for the ShopVirge shop management API. "
        "Use these tools to manage shops, products, categories, tags, attributes, and orders. "
        "Most endpoints require a shop_id (UUID). Use list_shops first to discover available shops."
    ),
)

# --- HTTP helper ---


async def _api_request(
    method: str,
    path: str,
    params: dict[str, Any] | None = None,
    json_body: dict[str, Any] | None = None,
) -> str:
    """Make an HTTP request to the ShopVirge API and return the response as a formatted string."""
    headers: dict[str, str] = {}
    if API_TOKEN:
        headers["Authorization"] = f"Bearer {API_TOKEN}"

    url = f"{API_BASE_URL}/api{path}"

    # Remove None values from params
    if params:
        params = {k: v for k, v in params.items() if v is not None}

    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.request(method, url, params=params, json=json_body, headers=headers)
        except httpx.ConnectError:
            return json.dumps({"error": f"Cannot connect to API at {API_BASE_URL}. Is the server running?"})
        except httpx.TimeoutException:
            return json.dumps({"error": f"Request timed out: {method} {url}"})

    if response.status_code == 204:
        return json.dumps({"status": "deleted", "message": "Resource deleted successfully"})

    try:
        data = response.json()
    except Exception:
        data = response.text

    if response.status_code >= 400:
        return json.dumps({"error": True, "status_code": response.status_code, "detail": data}, default=str)

    return json.dumps(data, default=str)


# =============================================================================
# SHOP TOOLS
# =============================================================================


@mcp.tool()
async def list_shops(skip: int = 0, limit: int = 20) -> str:
    """List all shops. Returns shop IDs, names, and descriptions. Use skip/limit for pagination."""
    return await _api_request("GET", "/shops/", params={"skip": skip, "limit": limit})


@mcp.tool()
async def get_shop(shop_id: str) -> str:
    """Get detailed information about a specific shop by its UUID, including prices and configuration."""
    return await _api_request("GET", f"/shops/{shop_id}")


@mcp.tool()
async def create_shop(
    name: str,
    description: str,
    vat_standard: float = 21.0,
    vat_lower_1: float = 9.0,
    vat_lower_2: float = 0.0,
    vat_lower_3: float = 0.0,
    vat_special: float = 0.0,
    vat_zero: float = 0.0,
    internal_url: Optional[str] = None,
    external_url: Optional[str] = None,
) -> str:
    """Create a new shop. Requires admin authentication. Returns the created shop."""
    body = {
        "name": name,
        "description": description,
        "vat_standard": vat_standard,
        "vat_lower_1": vat_lower_1,
        "vat_lower_2": vat_lower_2,
        "vat_lower_3": vat_lower_3,
        "vat_special": vat_special,
        "vat_zero": vat_zero,
        "internal_url": internal_url,
        "external_url": external_url,
    }
    return await _api_request("POST", "/shops/", json_body=body)


@mcp.tool()
async def update_shop(
    shop_id: str,
    name: str,
    description: str,
    vat_standard: float = 21.0,
    vat_lower_1: float = 9.0,
    vat_lower_2: float = 0.0,
    vat_lower_3: float = 0.0,
    vat_special: float = 0.0,
    vat_zero: float = 0.0,
    internal_url: Optional[str] = None,
    external_url: Optional[str] = None,
) -> str:
    """Update an existing shop. Requires admin authentication."""
    body = {
        "name": name,
        "description": description,
        "vat_standard": vat_standard,
        "vat_lower_1": vat_lower_1,
        "vat_lower_2": vat_lower_2,
        "vat_lower_3": vat_lower_3,
        "vat_special": vat_special,
        "vat_zero": vat_zero,
        "internal_url": internal_url,
        "external_url": external_url,
    }
    return await _api_request("PUT", f"/shops/{shop_id}", json_body=body)


@mcp.tool()
async def delete_shop(shop_id: str) -> str:
    """Delete a shop by its UUID. Requires admin authentication. This is irreversible."""
    return await _api_request("DELETE", f"/shops/{shop_id}")


# =============================================================================
# PRODUCT TOOLS
# =============================================================================


@mcp.tool()
async def list_products(shop_id: str, skip: int = 0, limit: int = 20) -> str:
    """List products for a shop. Returns product IDs, names, prices, and category info."""
    return await _api_request("GET", f"/shops/{shop_id}/products/", params={"skip": skip, "limit": limit})


@mcp.tool()
async def get_product(shop_id: str, product_id: str) -> str:
    """Get detailed product information including translations, prices, and images."""
    return await _api_request("GET", f"/shops/{shop_id}/products/{product_id}")


@mcp.tool()
async def create_product(
    shop_id: str,
    category_id: str,
    main_name: str,
    main_description: str,
    main_description_short: str,
    price: Optional[float] = None,
    tax_category: str = "vat_standard",
    max_one: bool = False,
    shippable: bool = False,
    featured: bool = False,
    new_product: bool = False,
    digital: Optional[str] = None,
    discounted_price: Optional[float] = None,
    stock: int = 1,
    order_number: Optional[int] = None,
    alt1_name: Optional[str] = None,
    alt1_description: Optional[str] = None,
    alt1_description_short: Optional[str] = None,
    alt2_name: Optional[str] = None,
    alt2_description: Optional[str] = None,
    alt2_description_short: Optional[str] = None,
) -> str:
    """Create a new product in a shop. Requires a category_id and translation fields (main_name, main_description, main_description_short). Optionally provide alt1_*/alt2_* for multi-language support."""
    body = {
        "shop_id": shop_id,
        "category_id": category_id,
        "price": price,
        "tax_category": tax_category,
        "max_one": max_one,
        "shippable": shippable,
        "featured": featured,
        "new_product": new_product,
        "digital": digital,
        "discounted_price": discounted_price,
        "stock": stock,
        "order_number": order_number,
        "translation": {
            "main_name": main_name,
            "main_description": main_description,
            "main_description_short": main_description_short,
            "alt1_name": alt1_name,
            "alt1_description": alt1_description,
            "alt1_description_short": alt1_description_short,
            "alt2_name": alt2_name,
            "alt2_description": alt2_description,
            "alt2_description_short": alt2_description_short,
        },
    }
    return await _api_request("POST", f"/shops/{shop_id}/products/", json_body=body)


@mcp.tool()
async def update_product(
    shop_id: str,
    product_id: str,
    category_id: str,
    main_name: str,
    main_description: str,
    main_description_short: str,
    price: Optional[float] = None,
    tax_category: str = "vat_standard",
    max_one: bool = False,
    shippable: bool = False,
    featured: bool = False,
    new_product: bool = False,
    digital: Optional[str] = None,
    discounted_price: Optional[float] = None,
    stock: int = 1,
    order_number: Optional[int] = None,
    alt1_name: Optional[str] = None,
    alt1_description: Optional[str] = None,
    alt1_description_short: Optional[str] = None,
    alt2_name: Optional[str] = None,
    alt2_description: Optional[str] = None,
    alt2_description_short: Optional[str] = None,
) -> str:
    """Update an existing product. All main translation fields are required."""
    body = {
        "shop_id": shop_id,
        "category_id": category_id,
        "price": price,
        "tax_category": tax_category,
        "max_one": max_one,
        "shippable": shippable,
        "featured": featured,
        "new_product": new_product,
        "digital": digital,
        "discounted_price": discounted_price,
        "stock": stock,
        "order_number": order_number,
        "translation": {
            "main_name": main_name,
            "main_description": main_description,
            "main_description_short": main_description_short,
            "alt1_name": alt1_name,
            "alt1_description": alt1_description,
            "alt1_description_short": alt1_description_short,
            "alt2_name": alt2_name,
            "alt2_description": alt2_description,
            "alt2_description_short": alt2_description_short,
        },
    }
    return await _api_request("PUT", f"/shops/{shop_id}/products/{product_id}", json_body=body)


@mcp.tool()
async def delete_product(shop_id: str, product_id: str) -> str:
    """Delete a product from a shop. This is irreversible."""
    return await _api_request("DELETE", f"/shops/{shop_id}/products/{product_id}")


# =============================================================================
# CATEGORY TOOLS
# =============================================================================


@mcp.tool()
async def list_categories(shop_id: str, skip: int = 0, limit: int = 20) -> str:
    """List categories for a shop. Categories organize products."""
    return await _api_request("GET", f"/shops/{shop_id}/categories/", params={"skip": skip, "limit": limit})


@mcp.tool()
async def get_category(shop_id: str, category_id: str) -> str:
    """Get detailed information about a specific category."""
    return await _api_request("GET", f"/shops/{shop_id}/categories/{category_id}")


@mcp.tool()
async def create_category(
    shop_id: str,
    main_name: str,
    main_description: str,
    color: str = "#000000",
    icon: Optional[str] = None,
    order_number: Optional[int] = None,
    alt1_name: Optional[str] = None,
    alt1_description: Optional[str] = None,
    alt2_name: Optional[str] = None,
    alt2_description: Optional[str] = None,
) -> str:
    """Create a new category in a shop. Provide main_name and main_description at minimum."""
    body = {
        "shop_id": shop_id,
        "color": color,
        "icon": icon,
        "order_number": order_number,
        "translation": {
            "main_name": main_name,
            "main_description": main_description,
            "alt1_name": alt1_name,
            "alt1_description": alt1_description,
            "alt2_name": alt2_name,
            "alt2_description": alt2_description,
        },
    }
    return await _api_request("POST", f"/shops/{shop_id}/categories/", json_body=body)


@mcp.tool()
async def delete_category(shop_id: str, category_id: str) -> str:
    """Delete a category from a shop. This is irreversible."""
    return await _api_request("DELETE", f"/shops/{shop_id}/categories/{category_id}")


# =============================================================================
# TAG TOOLS
# =============================================================================


@mcp.tool()
async def list_tags(shop_id: str, skip: int = 0, limit: int = 20) -> str:
    """List tags for a shop. Tags can be attached to products for filtering."""
    return await _api_request("GET", f"/shops/{shop_id}/tags/", params={"skip": skip, "limit": limit})


@mcp.tool()
async def create_tag(
    shop_id: str,
    name: str,
    main_name: str,
    alt1_name: Optional[str] = None,
    alt2_name: Optional[str] = None,
) -> str:
    """Create a new tag in a shop. Tags are used to label and filter products."""
    body = {
        "shop_id": shop_id,
        "name": name,
        "translation": {
            "main_name": main_name,
            "alt1_name": alt1_name,
            "alt2_name": alt2_name,
        },
    }
    return await _api_request("POST", f"/shops/{shop_id}/tags/", json_body=body)


@mcp.tool()
async def delete_tag(shop_id: str, tag_id: str) -> str:
    """Delete a tag from a shop. This is irreversible."""
    return await _api_request("DELETE", f"/shops/{shop_id}/tags/{tag_id}")


# =============================================================================
# ATTRIBUTE TOOLS
# =============================================================================


@mcp.tool()
async def list_attributes(shop_id: str, skip: int = 0, limit: int = 20) -> str:
    """List attributes for a shop. Attributes define product characteristics (e.g. size, color)."""
    return await _api_request("GET", f"/shops/{shop_id}/attributes/", params={"skip": skip, "limit": limit})


@mcp.tool()
async def list_attributes_with_options(shop_id: str, skip: int = 0, limit: int = 20) -> str:
    """List attributes with their options for a shop. Shows each attribute and its available option values."""
    return await _api_request(
        "GET", f"/shops/{shop_id}/attributes/with-options", params={"skip": skip, "limit": limit}
    )


@mcp.tool()
async def create_attribute(shop_id: str, name: str, unit: Optional[str] = None) -> str:
    """Create a new attribute for a shop (e.g. 'Size', 'Color'). Optionally specify a unit (e.g. 'ml', 'cm')."""
    body = {"name": name, "unit": unit}
    return await _api_request("POST", f"/shops/{shop_id}/attributes/", json_body=body)


@mcp.tool()
async def delete_attribute(shop_id: str, attribute_id: str) -> str:
    """Delete an attribute from a shop. This is irreversible."""
    return await _api_request("DELETE", f"/shops/{shop_id}/attributes/{attribute_id}")


# =============================================================================
# ATTRIBUTE OPTION TOOLS
# =============================================================================


@mcp.tool()
async def list_attribute_options(shop_id: str, attribute_id: str, skip: int = 0, limit: int = 20) -> str:
    """List options for a specific attribute (e.g. for a 'Size' attribute: 'S', 'M', 'L')."""
    return await _api_request(
        "GET", f"/shops/{shop_id}/attributes/{attribute_id}/options/", params={"skip": skip, "limit": limit}
    )


@mcp.tool()
async def create_attribute_option(shop_id: str, attribute_id: str, value_key: str) -> str:
    """Create a new option for an attribute. The value_key is the option value (e.g. 'Red', 'XL')."""
    body = {"value_key": value_key}
    return await _api_request("POST", f"/shops/{shop_id}/attributes/{attribute_id}/options/", json_body=body)


@mcp.tool()
async def delete_attribute_option(shop_id: str, attribute_id: str, option_id: str) -> str:
    """Delete an attribute option. This is irreversible."""
    return await _api_request("DELETE", f"/shops/{shop_id}/attributes/{attribute_id}/options/{option_id}")


# =============================================================================
# ORDER TOOLS
# =============================================================================


@mcp.tool()
async def list_orders(skip: int = 0, limit: int = 20) -> str:
    """List all orders across all shops. Requires admin authentication."""
    return await _api_request("GET", "/orders/", params={"skip": skip, "limit": limit})


@mcp.tool()
async def get_order(order_id: str) -> str:
    """Get detailed information about a specific order by its UUID."""
    return await _api_request("GET", f"/orders/{order_id}")


@mcp.tool()
async def create_order(
    shop_id: str,
    order_info: list[dict],
    account_id: Optional[str] = None,
    account_name: Optional[str] = None,
    total: Optional[float] = None,
    notes: Optional[str] = None,
    status: Optional[str] = None,
    customer_order_id: Optional[int] = None,
) -> str:
    """Create a new order. order_info is a list of items, each with: description, price, product_id, product_name, quantity. Provide either account_id (existing account) or account_name (creates new)."""
    body: dict[str, Any] = {
        "shop_id": shop_id,
        "order_info": order_info,
    }
    if account_id is not None:
        body["account_id"] = account_id
    if account_name is not None:
        body["account_name"] = account_name
    if total is not None:
        body["total"] = total
    if notes is not None:
        body["notes"] = notes
    if status is not None:
        body["status"] = status
    if customer_order_id is not None:
        body["customer_order_id"] = customer_order_id
    return await _api_request("POST", "/orders/", json_body=body)


# =============================================================================
# Entry point
# =============================================================================

if __name__ == "__main__":
    mcp.run()
