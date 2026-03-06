"""
CLI for the ShopVirge Backend API.

Provides command-line access to shops, products, categories, tags,
attributes, and orders.

Usage:
    # Start the API server first:
    PYTHONPATH=. uvicorn server.main:app --reload --port 8080

    # Then use the CLI:
    python cli.py shops list
    python cli.py shops get <shop-id>
    python cli.py products list <shop-id>
    python cli.py orders list

Environment variables:
    SHOP_API_BASE_URL  - Base URL of the running API (default: http://localhost:8080)
    SHOP_API_TOKEN     - Optional JWT token for authenticated endpoints
"""

from __future__ import annotations

import json
import os
import sys
from typing import Optional, Union

import httpx
import typer

API_BASE_URL = os.environ.get("SHOP_API_BASE_URL", "http://localhost:8080")
API_TOKEN = os.environ.get("SHOP_API_TOKEN", "")

app = typer.Typer(help="ShopVirge Backend CLI")
shops_app = typer.Typer(help="Manage shops")
products_app = typer.Typer(help="Manage products")
categories_app = typer.Typer(help="Manage categories")
tags_app = typer.Typer(help="Manage tags")
attributes_app = typer.Typer(help="Manage attributes")
orders_app = typer.Typer(help="Manage orders")
health_app = typer.Typer(help="Health checks")

app.add_typer(shops_app, name="shops")
app.add_typer(products_app, name="products")
app.add_typer(categories_app, name="categories")
app.add_typer(tags_app, name="tags")
app.add_typer(attributes_app, name="attributes")
app.add_typer(orders_app, name="orders")
app.add_typer(health_app, name="health")


# --- HTTP helper ---


def _headers() -> dict:
    headers = {}
    if API_TOKEN:
        headers["Authorization"] = f"Bearer {API_TOKEN}"
    return headers


def _api(method: str, path: str, params: Optional[dict] = None, json_body: Optional[dict] = None):
    """Make an HTTP request to the ShopVirge API and return parsed JSON."""
    url = f"{API_BASE_URL}{path}"
    if params:
        params = {k: v for k, v in params.items() if v is not None}

    try:
        response = httpx.request(method, url, params=params, json=json_body, headers=_headers(), timeout=30.0)
    except httpx.ConnectError:
        typer.echo(f"Error: Cannot connect to API at {API_BASE_URL}. Is the server running?", err=True)
        raise typer.Exit(1)
    except httpx.TimeoutException:
        typer.echo(f"Error: Request timed out: {method} {url}", err=True)
        raise typer.Exit(1)

    if response.status_code == 204:
        return {"status": "deleted"}

    try:
        data = response.json()
    except Exception:
        data = response.text

    if response.status_code >= 400:
        typer.echo(f"Error {response.status_code}: {json.dumps(data, indent=2, default=str)}", err=True)
        raise typer.Exit(1)

    return data


def _print(data):
    """Pretty-print JSON data."""
    typer.echo(json.dumps(data, indent=2, default=str))


# =============================================================================
# HEALTH
# =============================================================================


@health_app.command("check")
def health_check():
    """Check if the API is running."""
    _print(_api("GET", "/health/"))


# =============================================================================
# SHOPS
# =============================================================================


@shops_app.command("list")
def shops_list(
    skip: int = typer.Option(0, help="Number of records to skip"),
    limit: int = typer.Option(20, help="Max records to return"),
):
    """List all shops."""
    _print(_api("GET", "/shops/", params={"skip": skip, "limit": limit}))


@shops_app.command("get")
def shops_get(shop_id: str = typer.Argument(..., help="Shop UUID")):
    """Get details of a specific shop."""
    _print(_api("GET", f"/shops/{shop_id}"))


@shops_app.command("create")
def shops_create(
    name: str = typer.Option(..., help="Shop name"),
    description: str = typer.Option(..., help="Shop description"),
    vat_standard: float = typer.Option(21.0, help="Standard VAT rate"),
    vat_lower_1: float = typer.Option(9.0, help="Lower VAT rate 1"),
    vat_lower_2: float = typer.Option(0.0, help="Lower VAT rate 2"),
    vat_lower_3: float = typer.Option(0.0, help="Lower VAT rate 3"),
    vat_special: float = typer.Option(0.0, help="Special VAT rate"),
    vat_zero: float = typer.Option(0.0, help="Zero VAT rate"),
):
    """Create a new shop."""
    body = {
        "name": name,
        "description": description,
        "vat_standard": vat_standard,
        "vat_lower_1": vat_lower_1,
        "vat_lower_2": vat_lower_2,
        "vat_lower_3": vat_lower_3,
        "vat_special": vat_special,
        "vat_zero": vat_zero,
    }
    _print(_api("POST", "/shops/", json_body=body))


@shops_app.command("update")
def shops_update(
    shop_id: str = typer.Argument(..., help="Shop UUID"),
    name: str = typer.Option(..., help="Shop name"),
    description: str = typer.Option(..., help="Shop description"),
    vat_standard: float = typer.Option(21.0, help="Standard VAT rate"),
    vat_lower_1: float = typer.Option(9.0, help="Lower VAT rate 1"),
    vat_lower_2: float = typer.Option(0.0, help="Lower VAT rate 2"),
    vat_lower_3: float = typer.Option(0.0, help="Lower VAT rate 3"),
    vat_special: float = typer.Option(0.0, help="Special VAT rate"),
    vat_zero: float = typer.Option(0.0, help="Zero VAT rate"),
):
    """Update an existing shop."""
    body = {
        "name": name,
        "description": description,
        "vat_standard": vat_standard,
        "vat_lower_1": vat_lower_1,
        "vat_lower_2": vat_lower_2,
        "vat_lower_3": vat_lower_3,
        "vat_special": vat_special,
        "vat_zero": vat_zero,
    }
    _print(_api("PUT", f"/shops/{shop_id}", json_body=body))


@shops_app.command("delete")
def shops_delete(shop_id: str = typer.Argument(..., help="Shop UUID")):
    """Delete a shop."""
    _print(_api("DELETE", f"/shops/{shop_id}"))


# =============================================================================
# PRODUCTS
# =============================================================================


@products_app.command("list")
def products_list(
    shop_id: str = typer.Argument(..., help="Shop UUID"),
    skip: int = typer.Option(0, help="Number of records to skip"),
    limit: int = typer.Option(20, help="Max records to return"),
):
    """List products for a shop."""
    _print(_api("GET", f"/shops/{shop_id}/products/", params={"skip": skip, "limit": limit}))


@products_app.command("get")
def products_get(
    shop_id: str = typer.Argument(..., help="Shop UUID"),
    product_id: str = typer.Argument(..., help="Product UUID"),
):
    """Get details of a specific product."""
    _print(_api("GET", f"/shops/{shop_id}/products/{product_id}"))


@products_app.command("create")
def products_create(
    shop_id: str = typer.Argument(..., help="Shop UUID"),
    category_id: str = typer.Option(..., help="Category UUID"),
    main_name: str = typer.Option(..., help="Product name (main language)"),
    main_description: str = typer.Option(..., help="Product description (main language)"),
    main_description_short: str = typer.Option(..., help="Short description (main language)"),
    price: Optional[float] = typer.Option(None, help="Product price"),
    tax_category: str = typer.Option("vat_standard", help="Tax category"),
    stock: int = typer.Option(1, help="Stock count"),
    featured: bool = typer.Option(False, help="Mark as featured"),
    shippable: bool = typer.Option(False, help="Product is shippable"),
):
    """Create a new product in a shop."""
    body = {
        "shop_id": shop_id,
        "category_id": category_id,
        "price": price,
        "tax_category": tax_category,
        "stock": stock,
        "featured": featured,
        "shippable": shippable,
        "max_one": False,
        "new_product": False,
        "translation": {
            "main_name": main_name,
            "main_description": main_description,
            "main_description_short": main_description_short,
        },
    }
    _print(_api("POST", f"/shops/{shop_id}/products/", json_body=body))


@products_app.command("delete")
def products_delete(
    shop_id: str = typer.Argument(..., help="Shop UUID"),
    product_id: str = typer.Argument(..., help="Product UUID"),
):
    """Delete a product from a shop."""
    _print(_api("DELETE", f"/shops/{shop_id}/products/{product_id}"))


# =============================================================================
# CATEGORIES
# =============================================================================


@categories_app.command("list")
def categories_list(
    shop_id: str = typer.Argument(..., help="Shop UUID"),
    skip: int = typer.Option(0, help="Number of records to skip"),
    limit: int = typer.Option(20, help="Max records to return"),
):
    """List categories for a shop."""
    _print(_api("GET", f"/shops/{shop_id}/categories/", params={"skip": skip, "limit": limit}))


@categories_app.command("get")
def categories_get(
    shop_id: str = typer.Argument(..., help="Shop UUID"),
    category_id: str = typer.Argument(..., help="Category UUID"),
):
    """Get details of a specific category."""
    _print(_api("GET", f"/shops/{shop_id}/categories/{category_id}"))


@categories_app.command("create")
def categories_create(
    shop_id: str = typer.Argument(..., help="Shop UUID"),
    main_name: str = typer.Option(..., help="Category name (main language)"),
    main_description: str = typer.Option(..., help="Category description (main language)"),
    color: str = typer.Option("#000000", help="Category color (hex)"),
    order_number: Optional[int] = typer.Option(None, help="Display order"),
):
    """Create a new category in a shop."""
    body = {
        "shop_id": shop_id,
        "color": color,
        "order_number": order_number,
        "translation": {
            "main_name": main_name,
            "main_description": main_description,
        },
    }
    _print(_api("POST", f"/shops/{shop_id}/categories/", json_body=body))


@categories_app.command("delete")
def categories_delete(
    shop_id: str = typer.Argument(..., help="Shop UUID"),
    category_id: str = typer.Argument(..., help="Category UUID"),
):
    """Delete a category from a shop."""
    _print(_api("DELETE", f"/shops/{shop_id}/categories/{category_id}"))


# =============================================================================
# TAGS
# =============================================================================


@tags_app.command("list")
def tags_list(
    shop_id: str = typer.Argument(..., help="Shop UUID"),
    skip: int = typer.Option(0, help="Number of records to skip"),
    limit: int = typer.Option(20, help="Max records to return"),
):
    """List tags for a shop."""
    _print(_api("GET", f"/shops/{shop_id}/tags/", params={"skip": skip, "limit": limit}))


@tags_app.command("create")
def tags_create(
    shop_id: str = typer.Argument(..., help="Shop UUID"),
    name: str = typer.Option(..., help="Tag name (internal)"),
    main_name: str = typer.Option(..., help="Tag display name (main language)"),
):
    """Create a new tag in a shop."""
    body = {
        "shop_id": shop_id,
        "name": name,
        "translation": {"main_name": main_name},
    }
    _print(_api("POST", f"/shops/{shop_id}/tags/", json_body=body))


@tags_app.command("delete")
def tags_delete(
    shop_id: str = typer.Argument(..., help="Shop UUID"),
    tag_id: str = typer.Argument(..., help="Tag UUID"),
):
    """Delete a tag from a shop."""
    _print(_api("DELETE", f"/shops/{shop_id}/tags/{tag_id}"))


# =============================================================================
# ATTRIBUTES
# =============================================================================


@attributes_app.command("list")
def attributes_list(
    shop_id: str = typer.Argument(..., help="Shop UUID"),
    skip: int = typer.Option(0, help="Number of records to skip"),
    limit: int = typer.Option(20, help="Max records to return"),
):
    """List attributes for a shop."""
    _print(_api("GET", f"/shops/{shop_id}/attributes/", params={"skip": skip, "limit": limit}))


@attributes_app.command("list-with-options")
def attributes_list_with_options(
    shop_id: str = typer.Argument(..., help="Shop UUID"),
    skip: int = typer.Option(0, help="Number of records to skip"),
    limit: int = typer.Option(20, help="Max records to return"),
):
    """List attributes with their options for a shop."""
    _print(_api("GET", f"/shops/{shop_id}/attributes/with-options", params={"skip": skip, "limit": limit}))


@attributes_app.command("create")
def attributes_create(
    shop_id: str = typer.Argument(..., help="Shop UUID"),
    name: str = typer.Option(..., help="Attribute name (e.g. 'Size', 'Color')"),
    unit: Optional[str] = typer.Option(None, help="Unit (e.g. 'ml', 'cm')"),
):
    """Create a new attribute for a shop."""
    body = {"name": name, "unit": unit}
    _print(_api("POST", f"/shops/{shop_id}/attributes/", json_body=body))


@attributes_app.command("delete")
def attributes_delete(
    shop_id: str = typer.Argument(..., help="Shop UUID"),
    attribute_id: str = typer.Argument(..., help="Attribute UUID"),
):
    """Delete an attribute from a shop."""
    _print(_api("DELETE", f"/shops/{shop_id}/attributes/{attribute_id}"))


@attributes_app.command("add-option")
def attributes_add_option(
    shop_id: str = typer.Argument(..., help="Shop UUID"),
    attribute_id: str = typer.Argument(..., help="Attribute UUID"),
    value: str = typer.Option(..., help="Option value (e.g. 'Red', 'XL')"),
):
    """Add an option to an attribute."""
    body = {"value_key": value}
    _print(_api("POST", f"/shops/{shop_id}/attributes/{attribute_id}/options/", json_body=body))


@attributes_app.command("list-options")
def attributes_list_options(
    shop_id: str = typer.Argument(..., help="Shop UUID"),
    attribute_id: str = typer.Argument(..., help="Attribute UUID"),
    skip: int = typer.Option(0, help="Number of records to skip"),
    limit: int = typer.Option(20, help="Max records to return"),
):
    """List options for a specific attribute."""
    _print(_api("GET", f"/shops/{shop_id}/attributes/{attribute_id}/options/", params={"skip": skip, "limit": limit}))


@attributes_app.command("delete-option")
def attributes_delete_option(
    shop_id: str = typer.Argument(..., help="Shop UUID"),
    attribute_id: str = typer.Argument(..., help="Attribute UUID"),
    option_id: str = typer.Argument(..., help="Option UUID"),
):
    """Delete an attribute option."""
    _print(_api("DELETE", f"/shops/{shop_id}/attributes/{attribute_id}/options/{option_id}"))


# =============================================================================
# ORDERS
# =============================================================================


@orders_app.command("list")
def orders_list(
    skip: int = typer.Option(0, help="Number of records to skip"),
    limit: int = typer.Option(20, help="Max records to return"),
):
    """List all orders."""
    _print(_api("GET", "/orders/", params={"skip": skip, "limit": limit}))


@orders_app.command("get")
def orders_get(order_id: str = typer.Argument(..., help="Order UUID")):
    """Get details of a specific order."""
    _print(_api("GET", f"/orders/{order_id}"))


if __name__ == "__main__":
    app()
