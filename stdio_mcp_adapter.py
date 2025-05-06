#!/usr/bin/env python3
"""
MCP Adapter for Dependency Analyzer

This script acts as an adapter between Cursor (expecting JSON-RPC 2.0) and 
the dependency analyzer MCP server (using a different format).

Usage:
    python3 stdio_mcp_adapter.py
"""

import json
import sys
import subprocess
import uuid
import threading
import os

# Docker command to run the dependency analyzer
DOCKER_CMD = [
    "docker", "run", "-i", "--rm",
    "-v", f"{os.getcwd()}:/external_projects", 
    "-e", f"HOST_PROJECT_DIR={os.getcwd()}",
    "mcp/dependmap"
]

# Start the Docker process
docker_process = subprocess.Popen(
    DOCKER_CMD, 
    stdin=subprocess.PIPE, 
    stdout=subprocess.PIPE, 
    stderr=subprocess.PIPE,
    text=True
)

# Create a lock for writing to Docker
docker_write_lock = threading.Lock()

def send_to_docker(data):
    """Send data to the Docker process"""
    with docker_write_lock:
        print(f"Sending to Docker: {data}", file=sys.stderr)
        docker_process.stdin.write(json.dumps(data) + "\n")
        docker_process.stdin.flush()

def read_from_docker():
    """Read a line from the Docker process"""
    line = docker_process.stdout.readline()
    if not line:
        print("Docker process closed stdout", file=sys.stderr)
        return None
    return line.strip()

def cursor_to_mcp(cursor_data):
    """Convert Cursor's JSON-RPC 2.0 request to MCP format"""
    if "method" not in cursor_data:
        print(f"Invalid Cursor request: {cursor_data}", file=sys.stderr)
        return None
    
    method = cursor_data["method"]
    
    # Handle special methods
    if method == "initialize":
        # Return a simple handshake request in MCP format
        return {
            "handshake": True,
            "version": "1.0",
            "request_id": cursor_data.get("id", str(uuid.uuid4()))
        }
    
    if method == "mcp/listOfferings":
        # Get offerings using the handshake capabilities
        return {
            "handshake": True,
            "version": "1.0",
            "request_id": cursor_data.get("id", str(uuid.uuid4()))
        }
    
    if method == "mcp/invokeFunction":
        # Extract tool details from params
        params = cursor_data.get("params", {})
        tool = params.get("function", "")
        tool_params = params.get("parameters", {})
        
        return {
            "type": "tool_call",
            "tool": tool,
            "parameters": tool_params,
            "request_id": cursor_data.get("id", str(uuid.uuid4()))
        }
    
    # Default fallback
    return {
        "type": "generic_call",
        "method": method,
        "parameters": cursor_data.get("params", {}),
        "request_id": cursor_data.get("id", str(uuid.uuid4()))
    }

def mcp_to_jsonrpc(mcp_data, request_id=None):
    """Convert MCP response to JSON-RPC 2.0 format for Cursor"""
    if "status" not in mcp_data and "data" not in mcp_data and "handshake" not in mcp_data.get("data", {}):
        print(f"Invalid MCP response: {mcp_data}", file=sys.stderr)
        return None
    
    # Use the request_id from the argument if available, otherwise from the MCP data
    id_value = request_id or mcp_data.get("request_id", str(uuid.uuid4()))
    
    # Handle handshake response
    if "data" in mcp_data and "handshake" in mcp_data["data"]:
        capabilities = mcp_data["data"].get("capabilities", {})
        tools = []
        
        # Convert tools to function objects
        for tool_name in capabilities.get("tools", []):
            tools.append({
                "name": tool_name,
                "description": f"Dependency analyzer tool: {tool_name}",
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            })
        
        return {
            "jsonrpc": "2.0",
            "id": id_value,
            "result": {
                "functions": tools,
                "resources": [],
                "resourceTemplates": []
            }
        }
    
    # Handle error responses
    if mcp_data.get("status") == "error":
        error_data = mcp_data.get("error", {})
        return {
            "jsonrpc": "2.0",
            "id": id_value,
            "error": {
                "code": -32000,  # Generic server error
                "message": error_data.get("message", "Unknown error"),
                "data": error_data
            }
        }
    
    # Handle normal responses
    return {
        "jsonrpc": "2.0",
        "id": id_value,
        "result": mcp_data.get("data", {})
    }

def handle_cursor_input():
    """Main loop to handle input from Cursor"""
    while True:
        try:
            line = sys.stdin.readline()
            if not line:
                print("End of stdin stream, exiting", file=sys.stderr)
                break
            
            # Parse cursor input
            cursor_data = json.loads(line)
            print(f"Received from Cursor: {cursor_data}", file=sys.stderr)
            
            # Remember the ID for the response
            request_id = cursor_data.get("id")
            
            # Convert and send to Docker
            mcp_request = cursor_to_mcp(cursor_data)
            if mcp_request:
                send_to_docker(mcp_request)
                
                # Read response from Docker
                response_line = read_from_docker()
                if response_line:
                    try:
                        mcp_response = json.loads(response_line)
                        # Convert to JSON-RPC and send to Cursor
                        jsonrpc_response = mcp_to_jsonrpc(mcp_response, request_id)
                        if jsonrpc_response:
                            print(json.dumps(jsonrpc_response))
                            sys.stdout.flush()
                    except json.JSONDecodeError:
                        print(f"Failed to parse Docker response: {response_line}", file=sys.stderr)
                        # Send error to Cursor
                        error_response = {
                            "jsonrpc": "2.0",
                            "id": request_id,
                            "error": {
                                "code": -32000,
                                "message": "Failed to parse response from dependency analyzer"
                            }
                        }
                        print(json.dumps(error_response))
                        sys.stdout.flush()
            
        except json.JSONDecodeError:
            print(f"Failed to parse Cursor input: {line}", file=sys.stderr)
        except Exception as e:
            print(f"Error handling Cursor input: {str(e)}", file=sys.stderr)

# Start the main loop
if __name__ == "__main__":
    try:
        # Send error output to a log file
        sys.stderr = open("adapter_log.txt", "w")
        print("MCP Adapter starting", file=sys.stderr)
        
        # Run the main loop
        handle_cursor_input()
    finally:
        # Clean up
        print("MCP Adapter shutting down", file=sys.stderr)
        docker_process.terminate()
        sys.stderr.close() 