# Copyright 2026 René Dohmen <acidjunk@gmail.com>
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
"""Hand-written MCP tools that return mcp-ui (``ui://``) resources.

Unlike every other tool in this server (auto-generated from FastAPI routes by
``FastMCP.from_fastapi`` in ``server/mcp/server.py``), the tools here are
added directly to the ``FastMCP`` instance. They still authenticate and
shop-scope exactly like the auto-generated tools do: by re-invoking an
existing, already-authenticated FastAPI route in-process over
``httpx.ASGITransport`` and forwarding the incoming MCP request's headers.
This avoids hand-rolling auth/shop-scoping again, and avoids touching
``order_crud``/the DB session directly from a tool body (see the module
docstring in ``server/mcp/server.py`` for why that's fragile here).

The rendered HTML posts a ``postMessage`` back to the LibreChat host in the
shape ``@mcp-ui/client`` expects (see
https://github.com/idosal/mcp-ui/blob/main/docs/src/guide/mcp-apps.md and
``librechat-upstream/client/src/utils/index.ts::handleUIAction``):

    {"type": "tool", "payload": {"toolName": "get_order", "params": {...}}}

LibreChat does not call the tool directly from this message - it turns the
click into a new user turn instructing the model to call ``get_order``, so
that tool must already be an exposed MCP tool (see ``get_order`` in
``server/api/endpoints/shop_endpoints/orders.py``).
"""

import html
import json
from http import HTTPStatus
from typing import TYPE_CHECKING, Literal
from uuid import UUID

import httpx
from fastapi import FastAPI
from mcp.types import EmbeddedResource, TextContent, TextResourceContents

if TYPE_CHECKING:
    from fastmcp import FastMCP


def _orders_table_html(shop_id: UUID, status: str, orders: list[dict]) -> str:
    """Render a minimal, self-contained HTML table of orders.

    Escapes every interpolated field - this renders inside a scripted
    ``srcDoc`` iframe (sandboxed, no ``allow-same-origin``), and customer /
    account names are user-controlled data. Uses a single delegated click
    listener rather than inline ``onclick=`` attributes.
    """
    rows = []
    for order in orders:
        order_id = html.escape(str(order["id"]))
        rows.append(
            "<tr data-order-id=\"{order_id}\">"
            "<td>{customer_order_id}</td>"
            "<td>{status}</td>"
            "<td>{account_name}</td>"
            "<td>{total}</td>"
            "<td>{created_at}</td>"
            "</tr>".format(
                order_id=order_id,
                customer_order_id=html.escape(str(order.get("customer_order_id") or "")),
                status=html.escape(str(order.get("status") or "")),
                account_name=html.escape(str(order.get("account_name") or "")),
                total=html.escape(str(order.get("total") if order.get("total") is not None else "")),
                created_at=html.escape(str(order.get("created_at") or "")),
            )
        )

    return """<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8" />
<style>
  :root {{ color-scheme: dark; }}
  body {{ font-family: system-ui, sans-serif; font-size: 13px; margin: 8px; color: #e5e7eb; background: #111827; }}
  table {{ width: 100%; border-collapse: collapse; }}
  th, td {{ text-align: left; padding: 4px 8px; border-bottom: 1px solid #374151; }}
  th {{ color: #f9fafb; }}
  tr[data-order-id] {{ cursor: pointer; }}
  tr[data-order-id]:hover {{ background: #1f2937; }}
  caption {{ text-align: left; font-weight: 600; margin-bottom: 6px; color: #f9fafb; }}
</style>
</head>
<body>
<table>
  <caption>{caption}</caption>
  <thead>
    <tr><th>Order #</th><th>Status</th><th>Customer</th><th>Total</th><th>Created</th></tr>
  </thead>
  <tbody>
    {rows}
  </tbody>
</table>
<script>
  document.querySelector('tbody').addEventListener('click', function (event) {{
    var row = event.target.closest('tr[data-order-id]');
    if (!row) return;
    window.parent.postMessage({{
      type: 'tool',
      payload: {{
        toolName: 'get_order',
        params: {{ shop_id: {shop_id_js}, id: row.getAttribute('data-order-id') }}
      }}
    }}, '*');
  }});
</script>
</body>
</html>""".format(
        caption=html.escape(f"{status.capitalize()} orders"),
        rows="\n    ".join(rows) if rows else "<tr><td colspan=\"5\">No orders found</td></tr>",
        shop_id_js=json.dumps(str(shop_id)),
    )


def register_ui_tools(mcp: "FastMCP", app: FastAPI) -> None:
    """Add the mcp-ui prototype tool(s) to ``mcp`` before ``.http_app(...)`` is called."""
    from fastmcp.exceptions import ToolError
    from fastmcp.server.dependencies import get_http_headers
    from fastmcp.tools.tool import ToolResult

    @mcp.tool(
        name="orders_table_ui",
        description=(
            "Read-only. Renders a shop's orders as an interactive table (mcp-ui resource) "
            "instead of plain text - use this when the user wants to browse/click through "
            "orders rather than just read a list. Clicking a row calls `get_order` for that "
            "order's detail. Scoped to the shop in the path, same as `list_pending_orders` "
            "and `list_complete_orders`, which this wraps."
        ),
    )
    async def orders_table_ui(shop_id: UUID, status: Literal["pending", "complete"] = "pending") -> ToolResult:
        path = f"/orders/shop/{shop_id}/{status}"
        headers = get_http_headers()

        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(transport=transport, base_url="http://internal") as client:
            response = await client.get(path, headers=headers)

        if response.status_code != HTTPStatus.OK:
            # Surface the underlying route's own 401/403/404 as a readable tool
            # error rather than an httpx traceback the model has to guess at.
            raise ToolError(
                f"Could not read {status} orders for shop {shop_id} "
                f"(HTTP {response.status_code} from {path}): {response.text[:200]}"
            )
        orders = response.json()

        resource_html = _orders_table_html(shop_id, status, orders)
        resource_uri = f"ui://orders-table/{shop_id}-{status}"

        return ToolResult(
            content=[
                TextContent(
                    type="text",
                    text=(
                        f"Rendered {len(orders)} {status} order(s) for shop {shop_id} as an interactive "
                        "table. Reply with a one-line summary and the UI resource marker for this "
                        "resource so the table actually renders; do not repeat the order data as text."
                    ),
                ),
                EmbeddedResource(
                    type="resource",
                    resource=TextResourceContents(
                        uri=resource_uri,
                        mimeType="text/html",
                        text=resource_html,
                    ),
                ),
            ],
        )
