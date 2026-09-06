# Copyright 2026 René Dohmen <acidjunk@gmail.com>
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
"""Per-endpoint metadata for LLM agent exposure.

Add these as FastAPI route ``tags=[...]`` to mark endpoints for downstream
consumers. Each tag is a short kebab-case string that lands unchanged in the
OpenAPI spec, so any tool reading the spec can filter/branch on it.

Also holds the agent-surface guards used by routes that accept a destructive
``force`` flag -- see ``deny_agent_purge``.
"""

from enum import Enum

from fastapi import HTTPException, Request


class AgentTag(str, Enum):
    """Per-endpoint metadata for LLM agent exposure."""

    EXPOSED = "agent-exposed"
    """Gate: if absent, the endpoint is not exposed to any LLM agent surface."""

    LARGE = "agent-large"
    """Signal: may return many records; agent should narrow before calling."""


# --- Agent-surface guards ---------------------------------------------------
#
# ``server/mcp/server.py`` stamps this header onto every in-process request it
# makes on an LLM's behalf, from an httpx request event hook — i.e. after header
# merging, so an MCP client cannot unset it by forwarding its own value. An
# ordinary REST caller can of course set it themselves, but that only ever makes
# them *more* restricted, so trusting it in the deny direction is safe.
AGENT_SURFACE_HEADER = "x-agent-surface"
AGENT_SURFACE_MCP = "mcp"


def is_agent_request(request: Request) -> bool:
    """True when this request was made by an LLM agent through the MCP surface."""
    return request.headers.get(AGENT_SURFACE_HEADER) == AGENT_SURFACE_MCP


def deny_agent_purge(request: Request, entity: str) -> None:
    """Reject ``force=true`` hard purges coming from an LLM agent.

    Purging is irreversible: it drops the row outright, so neither ``restore_*``
    nor the revision history can bring the entity back. Agents get the reversible
    trash path only; a human purges from the web UI or a direct REST call.

    The MCP tool schema also hides the ``force`` parameter (see
    ``server/mcp/server.py``) so the model never learns it exists — but fastmcp
    forwards unknown arguments through to the route regardless, so that alone is
    not enforcement. This is.
    """
    if is_agent_request(request):
        raise HTTPException(
            status_code=403,
            detail=(
                f"Purging a {entity} is irreversible and not available to agents. "
                "Omit force to move it to the trash instead."
            ),
        )
