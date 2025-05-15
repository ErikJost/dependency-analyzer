#!/bin/sh

# Ensure /data directory exists
mkdir -p /data

# Start static web server in background, serving /data
python3 -m http.server ${PORT:-8000} --directory /data &

# Start MCP server (foreground)
exec python sdk_minimal_server.py 