import json
from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest

mcp_available = pytest.importorskip("mcp", reason="mcp not installed")
from mcp_server import _api_request


@pytest.mark.asyncio
async def test_api_request_get():
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = [{"id": "abc", "name": "Shop"}]

    with patch("mcp_server.httpx.AsyncClient") as mock_client_cls:
        mock_client = AsyncMock()
        mock_client.request.return_value = mock_response
        mock_client_cls.return_value.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client_cls.return_value.__aexit__ = AsyncMock(return_value=False)

        result = await _api_request("GET", "/shops/")

    data = json.loads(result)
    assert data == [{"id": "abc", "name": "Shop"}]


@pytest.mark.asyncio
async def test_api_request_post_with_body():
    mock_response = MagicMock()
    mock_response.status_code = 201
    mock_response.json.return_value = {"id": "new-123", "name": "New Shop"}

    with patch("mcp_server.httpx.AsyncClient") as mock_client_cls:
        mock_client = AsyncMock()
        mock_client.request.return_value = mock_response
        mock_client_cls.return_value.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client_cls.return_value.__aexit__ = AsyncMock(return_value=False)

        result = await _api_request("POST", "/shops/", json_body={"name": "New Shop"})

    data = json.loads(result)
    assert data["name"] == "New Shop"
    mock_client.request.assert_called_once()
    call_kwargs = mock_client.request.call_args
    assert call_kwargs.kwargs["json"] == {"name": "New Shop"}


@pytest.mark.asyncio
async def test_api_request_delete_204():
    mock_response = MagicMock()
    mock_response.status_code = 204

    with patch("mcp_server.httpx.AsyncClient") as mock_client_cls:
        mock_client = AsyncMock()
        mock_client.request.return_value = mock_response
        mock_client_cls.return_value.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client_cls.return_value.__aexit__ = AsyncMock(return_value=False)

        result = await _api_request("DELETE", "/shops/abc-123")

    data = json.loads(result)
    assert data["status"] == "deleted"


@pytest.mark.asyncio
async def test_api_request_error_response():
    mock_response = MagicMock()
    mock_response.status_code = 404
    mock_response.json.return_value = {"detail": "Not found"}

    with patch("mcp_server.httpx.AsyncClient") as mock_client_cls:
        mock_client = AsyncMock()
        mock_client.request.return_value = mock_response
        mock_client_cls.return_value.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client_cls.return_value.__aexit__ = AsyncMock(return_value=False)

        result = await _api_request("GET", "/shops/nonexistent")

    data = json.loads(result)
    assert data["error"] is True
    assert data["status_code"] == 404


@pytest.mark.asyncio
async def test_api_request_connection_error():
    with patch("mcp_server.httpx.AsyncClient") as mock_client_cls:
        mock_client = AsyncMock()
        mock_client.request.side_effect = httpx.ConnectError("Connection refused")
        mock_client_cls.return_value.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client_cls.return_value.__aexit__ = AsyncMock(return_value=False)

        result = await _api_request("GET", "/shops/")

    data = json.loads(result)
    assert "error" in data
    assert "Cannot connect" in data["error"]


@pytest.mark.asyncio
async def test_api_request_timeout():
    with patch("mcp_server.httpx.AsyncClient") as mock_client_cls:
        mock_client = AsyncMock()
        mock_client.request.side_effect = httpx.TimeoutException("timed out")
        mock_client_cls.return_value.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client_cls.return_value.__aexit__ = AsyncMock(return_value=False)

        result = await _api_request("GET", "/shops/")

    data = json.loads(result)
    assert "error" in data
    assert "timed out" in data["error"]


@pytest.mark.asyncio
async def test_api_request_strips_none_params():
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = []

    with patch("mcp_server.httpx.AsyncClient") as mock_client_cls:
        mock_client = AsyncMock()
        mock_client.request.return_value = mock_response
        mock_client_cls.return_value.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client_cls.return_value.__aexit__ = AsyncMock(return_value=False)

        await _api_request("GET", "/shops/", params={"skip": 0, "limit": 20, "filter": None})

    call_kwargs = mock_client.request.call_args
    assert call_kwargs.kwargs["params"] == {"skip": 0, "limit": 20}


@pytest.mark.asyncio
async def test_api_request_auth_header():
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = []

    with patch("mcp_server.httpx.AsyncClient") as mock_client_cls, patch("mcp_server.API_TOKEN", "test-token"):
        mock_client = AsyncMock()
        mock_client.request.return_value = mock_response
        mock_client_cls.return_value.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client_cls.return_value.__aexit__ = AsyncMock(return_value=False)

        await _api_request("GET", "/shops/")

    call_kwargs = mock_client.request.call_args
    assert call_kwargs.kwargs["headers"]["Authorization"] == "Bearer test-token"
