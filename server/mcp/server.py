# Copyright 2026 René Dohmen <acidjunk@gmail.com>
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
"""MCP (Model Context Protocol) server exposing shop-backend operations as tools.

Mounted into the FastAPI app at ``/mcp`` when ``MCP_ENABLED=True`` (see
``server/main.py``).

Tools are **auto-generated from the FastAPI app's routes** via ``fastmcp``'s
``FastMCP.from_fastapi(app=...)``. Every REST operation tagged
``AgentTag.EXPOSED`` becomes an MCP tool with a typed parameter schema
derived from the route's pydantic models, plus the route's docstring as the
tool description.

Auth: ``from_fastapi`` invokes routes via in-process ``httpx`` over
``ASGITransport``, which goes through the FastAPI middleware + dependency
chain so the existing ``Depends(auth_required_any)`` on each route fires
normally when the LLM calls the corresponding MCP tool. fastmcp's
``OpenAPITool.run`` auto-forwards the incoming MCP request's headers into
that inner httpx call, and as of 2.14.x its default exclude list does NOT
strip ``authorization`` or ``x-api-key`` — so either credential reaches the
underlying route's auth dependency without extra plumbing here.

Transport: streamable HTTP.

Pattern adapted from ``workfloworchestrator/orchestrator-core`` PR #1620.
"""

from typing import TYPE_CHECKING, Any

from fastapi import FastAPI

from server.agent_tags import AGENT_SURFACE_HEADER, AGENT_SURFACE_MCP, AgentTag

if TYPE_CHECKING:
    import httpx
    from fastmcp import FastMCP
    from starlette.applications import Starlette

MCP_MOUNT_PATH = "/mcp"

PURGE_TOOLS = frozenset(
    {
        "delete_product",
        "delete_tag",
        "delete_attribute",
        "delete_attribute_option",
    }
)

_FORCE_PARAM = "force"


def _hide_purge_flag(route: Any, component: Any) -> None:
    """Drop ``force`` from the input schema of the purge tools."""
    if component.name not in PURGE_TOOLS:
        return

    schema = component.parameters
    properties = schema.get("properties") or {}
    if properties.pop(_FORCE_PARAM, None) is None:
        raise RuntimeError(f"MCP tool {component.name!r} has no {_FORCE_PARAM!r} parameter to hide")

    required = schema.get("required")
    if required:
        schema["required"] = [name for name in required if name != _FORCE_PARAM]


async def _stamp_agent_surface(request: "httpx.Request") -> None:
    """Mark every in-process call fastmcp makes as coming from the agent surface.

    Runs as an httpx request event hook, i.e. on the fully-built request after
    client defaults and the MCP caller's forwarded headers have been merged — so
    an MCP client cannot suppress the marker by forwarding its own value.
    Routes read it via ``server.agent_tags.is_agent_request``.
    """
    request.headers[AGENT_SURFACE_HEADER] = AGENT_SURFACE_MCP


def build_mcp(app: FastAPI) -> "FastMCP":
    """Build the FastMCP server for ``app`` without mounting it.

    Split out from ``mount_mcp`` so tests can assert on the generated tool
    schemas using the exact same configuration that runs in production.
    """
    from fastmcp import FastMCP
    from fastmcp.server.openapi import MCPType, RouteMap

    return FastMCP.from_fastapi(
        app=app,
        name="shopvirge-mcp",
        route_maps=[
            RouteMap(tags={AgentTag.EXPOSED.value}, mcp_type=MCPType.TOOL),
            RouteMap(mcp_type=MCPType.EXCLUDE),
        ],
        mcp_component_fn=_hide_purge_flag,
        httpx_client_kwargs={"event_hooks": {"request": [_stamp_agent_surface]}},
    )


def mount_mcp(app: FastAPI) -> "Starlette":
    """Auto-generate MCP tools from ``app``'s routes, mount at ``/mcp``, return the sub-app.

    Only routes tagged with ``AgentTag.EXPOSED`` are surfaced; all other
    routes are excluded (otherwise fastmcp's default would expose every
    route in the app as a tool).

    The returned sub-app carries its own ASGI lifespan that the parent must
    enter — Starlette does not invoke a mounted sub-app's lifespan. Use
    ``mcp_app.router.lifespan_context(parent)`` from inside the parent's
    own lifespan context manager.
    """
    mcp = build_mcp(app)
    mcp_app = mcp.http_app(path="/", transport="http")
    app.mount(MCP_MOUNT_PATH, mcp_app)
    return mcp_app
