from unittest.mock import MagicMock, patch

import httpx
import pytest
from typer.testing import CliRunner

from cli import app

runner = CliRunner()


def test_cli_help():
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "ShopVirge Backend CLI" in result.output


def test_cli_shops_help():
    result = runner.invoke(app, ["shops", "--help"])
    assert result.exit_code == 0
    assert "list" in result.output
    assert "get" in result.output
    assert "create" in result.output
    assert "delete" in result.output


def test_cli_products_help():
    result = runner.invoke(app, ["products", "--help"])
    assert result.exit_code == 0
    assert "list" in result.output
    assert "get" in result.output
    assert "create" in result.output
    assert "delete" in result.output


def test_cli_categories_help():
    result = runner.invoke(app, ["categories", "--help"])
    assert result.exit_code == 0
    assert "list" in result.output
    assert "create" in result.output


def test_cli_tags_help():
    result = runner.invoke(app, ["tags", "--help"])
    assert result.exit_code == 0
    assert "list" in result.output
    assert "create" in result.output


def test_cli_attributes_help():
    result = runner.invoke(app, ["attributes", "--help"])
    assert result.exit_code == 0
    assert "list" in result.output
    assert "create" in result.output
    assert "add-option" in result.output
    assert "list-options" in result.output


def test_cli_orders_help():
    result = runner.invoke(app, ["orders", "--help"])
    assert result.exit_code == 0
    assert "list" in result.output
    assert "get" in result.output


@patch("cli.httpx.request")
def test_cli_shops_list(mock_request):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = [{"id": "abc-123", "name": "Test Shop"}]
    mock_request.return_value = mock_response

    result = runner.invoke(app, ["shops", "list"])
    assert result.exit_code == 0
    assert "Test Shop" in result.output
    assert "abc-123" in result.output
    mock_request.assert_called_once()


@patch("cli.httpx.request")
def test_cli_shops_get(mock_request):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"id": "abc-123", "name": "Test Shop", "description": "A test shop"}
    mock_request.return_value = mock_response

    result = runner.invoke(app, ["shops", "get", "abc-123"])
    assert result.exit_code == 0
    assert "Test Shop" in result.output


@patch("cli.httpx.request")
def test_cli_shops_create(mock_request):
    mock_response = MagicMock()
    mock_response.status_code = 201
    mock_response.json.return_value = {"id": "new-123", "name": "New Shop"}
    mock_request.return_value = mock_response

    result = runner.invoke(app, ["shops", "create", "--name", "New Shop", "--description", "Desc"])
    assert result.exit_code == 0
    assert "New Shop" in result.output


@patch("cli.httpx.request")
def test_cli_shops_delete(mock_request):
    mock_response = MagicMock()
    mock_response.status_code = 204
    mock_request.return_value = mock_response

    result = runner.invoke(app, ["shops", "delete", "abc-123"])
    assert result.exit_code == 0
    assert "deleted" in result.output


@patch("cli.httpx.request")
def test_cli_products_list(mock_request):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = [{"id": "prod-1", "name": "Widget"}]
    mock_request.return_value = mock_response

    result = runner.invoke(app, ["products", "list", "shop-123"])
    assert result.exit_code == 0
    assert "Widget" in result.output


@patch("cli.httpx.request")
def test_cli_orders_list(mock_request):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = [{"id": "order-1", "total": 42.0}]
    mock_request.return_value = mock_response

    result = runner.invoke(app, ["orders", "list"])
    assert result.exit_code == 0
    assert "order-1" in result.output


@patch("cli.httpx.request")
def test_cli_health_check(mock_request):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"status": "ok"}
    mock_request.return_value = mock_response

    result = runner.invoke(app, ["health", "check"])
    assert result.exit_code == 0
    assert "ok" in result.output


@patch("cli.httpx.request")
def test_cli_api_error(mock_request):
    mock_response = MagicMock()
    mock_response.status_code = 404
    mock_response.json.return_value = {"detail": "Not found"}
    mock_request.return_value = mock_response

    result = runner.invoke(app, ["shops", "get", "nonexistent"])
    assert result.exit_code == 1


@patch("cli.httpx.request", side_effect=httpx.ConnectError("Connection refused"))
def test_cli_connection_error(mock_request):
    result = runner.invoke(app, ["shops", "list"])
    assert result.exit_code == 1
    assert "Cannot connect" in result.output


@patch("cli.httpx.request", side_effect=httpx.TimeoutException("timed out"))
def test_cli_timeout_error(mock_request):
    result = runner.invoke(app, ["shops", "list"])
    assert result.exit_code == 1
    assert "timed out" in result.output


@patch("cli.httpx.request")
def test_cli_auth_header(mock_request):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = []
    mock_request.return_value = mock_response

    with patch("cli.API_TOKEN", "my-secret-token"):
        runner.invoke(app, ["shops", "list"])

    call_kwargs = mock_request.call_args
    assert call_kwargs.kwargs["headers"]["Authorization"] == "Bearer my-secret-token"


@patch("cli.httpx.request")
def test_cli_no_auth_header_when_no_token(mock_request):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = []
    mock_request.return_value = mock_response

    with patch("cli.API_TOKEN", ""):
        runner.invoke(app, ["shops", "list"])

    call_kwargs = mock_request.call_args
    assert "Authorization" not in call_kwargs.kwargs["headers"]
