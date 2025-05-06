#!/usr/bin/env python3
"""
Test script for MCP server interaction
"""
import subprocess
import json
import time

def test_mcp_server():
    # Start the Docker container
    print("Starting MCP server container...")
    process = subprocess.Popen(
        ["docker", "run", "-i", "--rm", "mcp/simple-dependmap"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    # Wait a moment for the server to start
    time.sleep(1)
    
    # Send an initialize request
    print("Sending initialize request...")
    initialize_request = {
        "jsonrpc": "2.0",
        "id": "init123",
        "method": "initialize"
    }
    
    process.stdin.write(json.dumps(initialize_request) + "\n")
    process.stdin.flush()
    
    # Read the response
    response_line = process.stdout.readline()
    print(f"Response received: {response_line[:100]}...")
    
    try:
        response = json.loads(response_line)
        if "result" in response and "serverInfo" in response["result"]:
            print("✅ Initialize response looks correct")
        else:
            print("❌ Initialize response format issue")
    except json.JSONDecodeError:
        print("❌ Could not parse response as JSON")
    
    # Send a function invocation request
    print("\nSending function invocation request...")
    function_request = {
        "jsonrpc": "2.0",
        "id": "func123",
        "method": "mcp/invokeFunction",
        "params": {
            "function": "list_projects",
            "parameters": {}
        }
    }
    
    process.stdin.write(json.dumps(function_request) + "\n")
    process.stdin.flush()
    
    # Read the response
    response_line = process.stdout.readline()
    print(f"Response received: {response_line[:100]}...")
    
    try:
        response = json.loads(response_line)
        if "result" in response and "function" in response["result"]:
            print("✅ Function response looks correct")
        else:
            print("❌ Function response format issue")
    except json.JSONDecodeError:
        print("❌ Could not parse response as JSON")
    
    # Terminate the process
    print("\nTerminating server...")
    process.terminate()
    process.wait(timeout=5)
    
    # Check stderr output
    stderr_output = process.stderr.read()
    print(f"\nServer logs (first 300 chars):\n{stderr_output[:300]}")
    
    return True

if __name__ == "__main__":
    test_mcp_server() 