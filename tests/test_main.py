"""Tests for the main module."""

import os
import pytest
from unittest.mock import patch, MagicMock
from prometheus_mcp_server.main import setup_environment, run_server

def test_setup_environment_success():
    """Test successful environment setup."""
    # Setup
    os.environ["PROMETHEUS_URL"] = "http://test:9090"

    # Execute with mocked print function
    with patch("builtins.print") as mock_print:
        result = setup_environment()

    # Verify
    assert result is True
    mock_print.assert_any_call("Prometheus configuration:")
    mock_print.assert_any_call("  Server URL: http://test:9090")

    # Clean up
    del os.environ["PROMETHEUS_URL"]

def test_setup_environment_missing_url():
    """Test environment setup with missing URL."""
    # Setup - ensure URL is not in environment
    if "PROMETHEUS_URL" in os.environ:
        del os.environ["PROMETHEUS_URL"]

    # Execute with mocked print function
    with patch("builtins.print") as mock_print:
        result = setup_environment()

    # Verify
    assert result is False
    mock_print.assert_any_call("ERROR: PROMETHEUS_URL environment variable is not set")

def test_setup_environment_with_auth():
    """Test environment setup with authentication."""
    # Setup
    os.environ["PROMETHEUS_URL"] = "http://test:9090"
    os.environ["PROMETHEUS_USERNAME"] = "user"
    os.environ["PROMETHEUS_PASSWORD"] = "pass"

    # Execute with mocked print function
    with patch("builtins.print") as mock_print:
        result = setup_environment()

    # Verify
    assert result is True
    mock_print.assert_any_call("Authentication: Using basic auth")

    # Clean up
    del os.environ["PROMETHEUS_URL"]
    del os.environ["PROMETHEUS_USERNAME"]
    del os.environ["PROMETHEUS_PASSWORD"]

@patch("prometheus_mcp_server.main.setup_environment")
@patch("prometheus_mcp_server.main.mcp.run")
@patch("prometheus_mcp_server.main.sys.exit")
def test_run_server_success(mock_exit, mock_run, mock_setup):
    """Test successful server run."""
    # Setup
    mock_setup.return_value = True

    # Execute
    run_server()

    # Verify
    mock_setup.assert_called_once()
    mock_run.assert_called_once_with(transport="stdio")
    mock_exit.assert_not_called()

@patch("prometheus_mcp_server.main.setup_environment")
@patch("prometheus_mcp_server.main.mcp.run")
@patch("prometheus_mcp_server.main.sys.exit")
def test_run_server_setup_failure(mock_exit, mock_run, mock_setup):
    """Test server run with setup failure."""
    # Setup
    mock_setup.return_value = False

    # Execute
    run_server()

    # Verify
    mock_setup.assert_called_once()
    mock_run.assert_not_called()
    mock_exit.assert_called_once_with(1)
