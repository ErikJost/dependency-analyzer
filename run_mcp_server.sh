#!/bin/bash
# Run the MCP server and redirect stderr to a log file
# This ensures that the stdout stream contains only JSON-RPC responses

# Create log directory if it doesn't exist
mkdir -p /tmp/mcp_logs

# Run the container with stderr redirected to a log file
docker run -i --rm mcp/simple-dependmap 2>/tmp/mcp_logs/mcp_server.log 