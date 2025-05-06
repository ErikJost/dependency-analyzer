#!/usr/bin/env python3
"""
Test script to see how the dependency analyzer responds to JSON-RPC 2.0 initialization
"""
import subprocess
import json
import time

# The exact format Cursor uses for initialization
INITIALIZE_MESSAGE = {
    "jsonrpc": "2.0",
    "id": "init123",
    "method": "initialize",
    "params": {}
}

LIST_OFFERINGS_MESSAGE = {
    "jsonrpc": "2.0",
    "id": "list456",
    "method": "mcp/listOfferings",
    "params": {}
}

def main():
    # Start the Docker container
    process = subprocess.Popen(
        ["docker", "run", "-i", "--rm", "mcp/dependmap"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    # Send initialize message
    print("Sending initialize message...")
    process.stdin.write(json.dumps(INITIALIZE_MESSAGE) + "\n")
    process.stdin.flush()
    
    # Wait for response
    initialize_response = process.stdout.readline().strip()
    print("\nResponse to initialize:")
    try:
        pretty_response = json.dumps(json.loads(initialize_response), indent=2)
        print(pretty_response)
    except:
        print(initialize_response)
    
    # Send listOfferings message
    print("\nSending listOfferings message...")
    process.stdin.write(json.dumps(LIST_OFFERINGS_MESSAGE) + "\n")
    process.stdin.flush()
    
    # Wait for response
    list_response = process.stdout.readline().strip()
    print("\nResponse to listOfferings:")
    try:
        pretty_response = json.dumps(json.loads(list_response), indent=2)
        print(pretty_response)
    except:
        print(list_response)
    
    # Close the process
    process.stdin.close()
    process.terminate()
    process.wait(timeout=5)

if __name__ == "__main__":
    main() 