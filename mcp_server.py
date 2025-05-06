#!/usr/bin/env python3
"""
MCP Server for Dependency Analysis - Main Entry Point

This module serves as the unified entry point for the MCP server,
providing a JSON-RPC 2.0 compliant interface to Cursor.

Usage:
    python3 mcp_server.py [--mode=(http|stdio)] [--port=8000] [--config=config.yaml]

Note: For Cursor integration, use stdio mode only with JSON-RPC 2.0 format.
"""

import os
import sys
import json
import argparse
import signal
import traceback
from typing import Dict, Any, Optional

# Import the JSON-RPC server implementation
import simple_mcp_server  # JSON-RPC 2.0 stdio mode

def signal_handler(sig, frame):
    """Handle graceful shutdown on signals"""
    print(f"Received signal {sig}, shutting down...", file=sys.stderr)
    sys.exit(0)

def main():
    """Main entry point for the MCP server."""
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Start the dependency analyzer MCP server")
    parser.add_argument('--port', type=int, default=8000, 
                        help='Port to run the server on (HTTP mode only)')
    parser.add_argument('--mode', choices=['http', 'stdio'], default="stdio",
                        help='Mode to run the server in (use stdio for Cursor integration)')
    parser.add_argument('--config', help='Path to the configuration file')
    parser.add_argument('--no-browser', action='store_true', help='Don\'t open the browser automatically (HTTP mode only)')
    args = parser.parse_args()
    
    print(f"Starting MCP server in {args.mode} mode", file=sys.stderr)
    
    try:
        if args.mode == "stdio":
            # Start the simple JSON-RPC 2.0 stdio server
            print("Running stdio MCP server with JSON-RPC 2.0 protocol", file=sys.stderr)
            server = simple_mcp_server.SimpleMCPServer()
            server.run()
        else:  # HTTP mode
            print(f"HTTP mode is not recommended for Cursor integration", file=sys.stderr)
            print(f"For Cursor, please use: python mcp_server.py --mode=stdio", file=sys.stderr)
            # You could optionally import and run the HTTP server here if needed
    
    except Exception as e:
        print(f"Error starting MCP server: {str(e)}", file=sys.stderr)
        traceback.print_exc(file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main() 