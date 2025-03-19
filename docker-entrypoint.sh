#!/bin/bash
set -e

# Activate virtual environment
source /app/.venv/bin/activate

# Run the MCP server
python -m prometheus_mcp_server.main

# Keep the script running
exec "$@"
