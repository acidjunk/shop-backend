# Copyright 2026 René Dohmen <acidjunk@gmail.com>
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
"""Tests for the MCP (Model Context Protocol) server integration.

These tests verify that:

1. The agent-tagged shop CRUD routes carry ``AgentTag.EXPOSED`` and have
   stable ``operation_id`` values that map 1:1 to the MCP tool names.
2. ``FastMCP.from_fastapi`` introspects the FastAPI app's routes, derives
   input schemas from their pydantic models, and produces exactly the tools
   we expect via ``RouteMap`` tag-based filtering.

Pattern adapted from ``workfloworchestrator/orchestrator-core`` PR #1620.
"""

from __future__ import annotations

import asyncio
from uuid import UUID

import pytest
from fastapi import FastAPI

from server.agent_tags import AgentTag

# All tool names must match the ``operation_id`` on each tagged route.
EXPECTED_TOOL_NAMES = {
    # products
    "list_products",
    "get_product",
    "create_product",
    "update_product",
    "delete_product",
    # categories
    "list_categories",
    "get_category",
    "create_category",
    "update_category",
    "delete_category",
    # tags
    "list_tags",
    "get_tag",
    "create_tag",
    "update_tag",
    "delete_tag",
    # attributes
    "list_attributes",
    "get_attribute",
    "create_attribute",
    "update_attribute",
    "delete_attribute",
    # revisions / trash
    "list_shop_revisions",
    "get_revision",
    "list_product_revisions",
    "get_product_revision",
    "restore_product_revision",
    "restore_product",
    "restore_category",
    "restore_category_revision",
    "restore_tag_revision",
    "restore_tag",
    "restore_attribute_revision",
    "restore_attribute",
    # shops
    "list_my_shops",
    # orders (read-only)
    "list_pending_orders",
    "list_complete_orders",
    "get_order",
}

# Hand-written tools added by ``register_ui_tools`` — deliberately NOT in
# EXPECTED_TOOL_NAMES, which is also asserted against the FastAPI route table.
EXPECTED_CUSTOM_TOOL_NAMES = {"orders_table_ui"}


def _agent_tagged_routes(app: FastAPI) -> dict[str, str]:
    """Return ``{operation_id: path}`` for every route tagged ``AgentTag.EXPOSED``."""
    out: dict[str, str] = {}
    for route in app.routes:
        tags = getattr(route, "tags", None) or []
        if AgentTag.EXPOSED.value in tags or AgentTag.EXPOSED in tags:
            op_id = getattr(route, "operation_id", None)
            path = getattr(route, "path", "")
            assert op_id, f"agent-exposed route {path!r} is missing operation_id"
            out[op_id] = path
    return out


def test_all_expected_routes_carry_agent_tag(fastapi_app: FastAPI) -> None:
    """Every expected MCP tool name has a route tagged ``AgentTag.EXPOSED``."""
    found = _agent_tagged_routes(fastapi_app)
    assert (
        set(found) == EXPECTED_TOOL_NAMES
    ), f"missing: {EXPECTED_TOOL_NAMES - set(found)}, extra: {set(found) - EXPECTED_TOOL_NAMES}"


def test_fastmcp_introspects_all_expected_tools(fastapi_app: FastAPI) -> None:
    """``FastMCP.from_fastapi`` produces exactly the expected tools from the tagged routes."""
    pytest.importorskip("fastmcp")
    from fastmcp import FastMCP
    from fastmcp.server.openapi import MCPType, RouteMap

    from server.mcp.server import mount_mcp  # noqa: F401 — sanity import

    mcp = FastMCP.from_fastapi(
        app=fastapi_app,
        name="shopvirge-mcp-test",
        route_maps=[
            RouteMap(tags={AgentTag.EXPOSED.value}, mcp_type=MCPType.TOOL),
            RouteMap(mcp_type=MCPType.EXCLUDE),
        ],
    )

    tools = asyncio.run(mcp.get_tools())
    tool_names = set(tools.keys())
    assert (
        tool_names == EXPECTED_TOOL_NAMES
    ), f"missing: {EXPECTED_TOOL_NAMES - tool_names}, extra: {tool_names - EXPECTED_TOOL_NAMES}"


def test_update_product_tool_has_no_required_body_fields(fastapi_app: FastAPI) -> None:
    """The update_product tool must not force the LLM to send the full product.

    Required image_1..image_6 fields made the model emit `"image_6": null` for
    empty slots, which triggered malformed streamed tool JSON under Anthropic's
    fine-grained-tool-streaming beta. Only the path params may be required.
    """
    pytest.importorskip("fastmcp")
    from fastmcp import FastMCP
    from fastmcp.server.openapi import MCPType, RouteMap

    mcp = FastMCP.from_fastapi(
        app=fastapi_app,
        name="shopvirge-mcp-test",
        route_maps=[
            RouteMap(tags={AgentTag.EXPOSED.value}, mcp_type=MCPType.TOOL),
            RouteMap(mcp_type=MCPType.EXCLUDE),
        ],
    )

    tools = asyncio.run(mcp.get_tools())
    schema = tools["update_product"].parameters
    required = set(schema.get("required", []))
    assert not any(r.startswith("image_") for r in required), f"image fields still required: {required}"
    assert "translation" not in required, f"translation still required: {required}"


def test_update_category_tool_has_no_required_body_fields(fastapi_app: FastAPI) -> None:
    """The update_category tool must not force the LLM to send the full category.

    Same failure mode as update_product: required main_image/alt1_image/alt2_image
    fields made the model emit `"alt2_image": null` for empty slots, which triggered
    malformed streamed tool JSON under Anthropic's fine-grained-tool-streaming beta.
    Only the path params may be required.
    """
    pytest.importorskip("fastmcp")
    from fastmcp import FastMCP
    from fastmcp.server.openapi import MCPType, RouteMap

    mcp = FastMCP.from_fastapi(
        app=fastapi_app,
        name="shopvirge-mcp-test",
        route_maps=[
            RouteMap(tags={AgentTag.EXPOSED.value}, mcp_type=MCPType.TOOL),
            RouteMap(mcp_type=MCPType.EXCLUDE),
        ],
    )

    tools = asyncio.run(mcp.get_tools())
    schema = tools["update_category"].parameters
    required = set(schema.get("required", []))
    assert not any(r.endswith("_image") for r in required), f"image fields still required: {required}"
    assert "translation" not in required, f"translation still required: {required}"


def _mcp_with_ui_tools(fastapi_app: FastAPI):
    from fastmcp import FastMCP
    from fastmcp.server.openapi import MCPType, RouteMap

    from server.mcp.ui_tools import register_ui_tools

    mcp = FastMCP.from_fastapi(
        app=fastapi_app,
        name="shopvirge-mcp-test",
        route_maps=[
            RouteMap(tags={AgentTag.EXPOSED.value}, mcp_type=MCPType.TOOL),
            RouteMap(mcp_type=MCPType.EXCLUDE),
        ],
    )
    register_ui_tools(mcp, fastapi_app)
    return mcp


def test_register_ui_tools_adds_custom_tools(fastapi_app: FastAPI) -> None:
    """``register_ui_tools`` adds the hand-written tools on top of the route-derived ones."""
    pytest.importorskip("fastmcp")

    tools = asyncio.run(_mcp_with_ui_tools(fastapi_app).get_tools())
    expected = EXPECTED_TOOL_NAMES | EXPECTED_CUSTOM_TOOL_NAMES
    assert set(tools) == expected, f"missing: {expected - set(tools)}, extra: {set(tools) - expected}"


def test_orders_table_ui_returns_a_ui_resource(fastapi_app: FastAPI, shop, pending_order) -> None:
    """The tool returns exactly one ``ui://`` text/html resource containing the order.

    That URI scheme + mimeType combination is the exact contract LibreChat's
    ``formatToolContent`` keys on to render an iframe instead of raw text.
    Called through a fastmcp ``Client`` so the real tool-call path (and the
    tool's in-process HTTP call back into the app) is exercised.
    """
    pytest.importorskip("fastmcp")
    from fastmcp import Client
    from mcp.types import EmbeddedResource

    mcp = _mcp_with_ui_tools(fastapi_app)

    async def call():
        async with Client(mcp) as client:
            return await client.call_tool("orders_table_ui", {"shop_id": str(shop), "status": "pending"})

    result = asyncio.run(call())

    resources = [block for block in result.content if isinstance(block, EmbeddedResource)]
    assert len(resources) == 1, f"expected exactly one embedded resource, got {result.content}"

    resource = resources[0].resource
    assert str(resource.uri).startswith("ui://"), resource.uri
    assert resource.mimeType == "text/html"
    assert str(pending_order) in resource.text, "rendered table does not reference the pending order"
    assert "postMessage" in resource.text and "get_order" in resource.text


def test_orders_table_ui_escapes_order_data(fastapi_app: FastAPI) -> None:
    """Order data is user-controlled and lands in a scripted iframe — it must be escaped."""
    from server.mcp.ui_tools import _orders_table_html

    rendered = _orders_table_html(
        UUID("00000000-0000-0000-0000-000000000001"),
        "pending",
        [{"id": "00000000-0000-0000-0000-000000000002", "account_name": "<script>alert(1)</script>"}],
    )
    assert "<script>alert(1)</script>" not in rendered
    assert "&lt;script&gt;alert(1)&lt;/script&gt;" in rendered
    assert "color-scheme: dark" in rendered
    assert "background: #111827" in rendered


def test_mount_mcp_is_importable() -> None:
    """The mount_mcp helper imports cleanly (catches dotted-path drift in fastmcp)."""
    pytest.importorskip("fastmcp")
    from server.mcp import mount_mcp

    assert callable(mount_mcp)
