#!/usr/bin/env python3
"""
Test script for validating JSON-RPC 2.0 compliance of the MCP server

Usage:
    python3 test_jsonrpc_mcp.py [--server=<server_command>]

Example:
    python3 test_jsonrpc_mcp.py --server="docker run -i --rm mcp/simple-dependmap"
"""

import sys
import json
import argparse
import subprocess
import threading

def test_initialize(server_process):
    """Test the initialize request"""
    print("\n--- Testing initialize request ---")
    
    # Send initialize request
    request = {
        "jsonrpc": "2.0",
        "id": "initialize-test",
        "method": "initialize"
    }
    
    print(f"Sending: {json.dumps(request)}")
    server_process.stdin.write(json.dumps(request) + "\n")
    server_process.stdin.flush()
    
    # Read response
    response_line = server_process.stdout.readline().strip()
    print(f"Received: {response_line}")
    
    # Validate response
    try:
        response = json.loads(response_line)
        
        # Check for required fields
        assert "jsonrpc" in response, "Missing 'jsonrpc' field"
        assert response["jsonrpc"] == "2.0", "jsonrpc field should be '2.0'"
        assert "id" in response, "Missing 'id' field"
        assert response["id"] == "initialize-test", "id does not match request"
        assert "result" in response, "Missing 'result' field"
        
        # Check for serverInfo
        result = response["result"]
        assert "serverInfo" in result, "Missing 'serverInfo' in result"
        assert "name" in result["serverInfo"], "Missing 'name' in serverInfo"
        
        # Check for capabilities
        assert "capabilities" in result, "Missing 'capabilities' in result"
        assert "functions" in result["capabilities"], "Missing 'functions' in capabilities"
        
        print("✅ Initialize test passed")
        return True
    except (json.JSONDecodeError, AssertionError) as e:
        print(f"❌ Initialize test failed: {str(e)}")
        return False

def test_function_call(server_process):
    """Test a function call"""
    print("\n--- Testing function call ---")
    
    # Send function call request
    request = {
        "jsonrpc": "2.0",
        "id": "function-test",
        "method": "mcp/invokeFunction",
        "params": {
            "function": "list_projects",
            "parameters": {}
        }
    }
    
    print(f"Sending: {json.dumps(request)}")
    server_process.stdin.write(json.dumps(request) + "\n")
    server_process.stdin.flush()
    
    # Read response
    response_line = server_process.stdout.readline().strip()
    print(f"Received: {response_line}")
    
    # Validate response
    try:
        response = json.loads(response_line)
        
        # Check for required fields
        assert "jsonrpc" in response, "Missing 'jsonrpc' field"
        assert response["jsonrpc"] == "2.0", "jsonrpc field should be '2.0'"
        assert "id" in response, "Missing 'id' field"
        assert response["id"] == "function-test", "id does not match request"
        assert "result" in response, "Missing 'result' field"
        
        print("✅ Function call test passed")
        return True
    except (json.JSONDecodeError, AssertionError) as e:
        print(f"❌ Function call test failed: {str(e)}")
        return False

def test_error_handling(server_process):
    """Test error handling"""
    print("\n--- Testing error handling ---")
    
    # Send invalid method request
    request = {
        "jsonrpc": "2.0",
        "id": "error-test",
        "method": "invalid_method"
    }
    
    print(f"Sending: {json.dumps(request)}")
    server_process.stdin.write(json.dumps(request) + "\n")
    server_process.stdin.flush()
    
    # Read response
    response_line = server_process.stdout.readline().strip()
    print(f"Received: {response_line}")
    
    # Validate response
    try:
        response = json.loads(response_line)
        
        # Check for required fields
        assert "jsonrpc" in response, "Missing 'jsonrpc' field"
        assert response["jsonrpc"] == "2.0", "jsonrpc field should be '2.0'"
        assert "id" in response, "Missing 'id' field"
        assert response["id"] == "error-test", "id does not match request"
        assert "error" in response, "Missing 'error' field"
        
        # Check error object
        error = response["error"]
        assert "code" in error, "Missing 'code' in error"
        assert "message" in error, "Missing 'message' in error"
        
        print("✅ Error handling test passed")
        return True
    except (json.JSONDecodeError, AssertionError) as e:
        print(f"❌ Error handling test failed: {str(e)}")
        return False

def test_invalid_json(server_process):
    """Test sending invalid JSON"""
    print("\n--- Testing invalid JSON ---")
    
    # Send invalid JSON
    invalid_json = '{"jsonrpc": "2.0", "id": "invalid-json", "method": "initialize", }'
    
    print(f"Sending invalid JSON: {invalid_json}")
    server_process.stdin.write(invalid_json + "\n")
    server_process.stdin.flush()
    
    # Read response
    response_line = server_process.stdout.readline().strip()
    print(f"Received: {response_line}")
    
    # Validate response
    try:
        response = json.loads(response_line)
        
        # Check for required fields
        assert "jsonrpc" in response, "Missing 'jsonrpc' field"
        assert response["jsonrpc"] == "2.0", "jsonrpc field should be '2.0'"
        assert "error" in response, "Missing 'error' field"
        
        # Check error object
        error = response["error"]
        assert "code" in error, "Missing 'code' in error"
        assert error["code"] == -32700, "Error code should be -32700 for parse error"
        assert "message" in error, "Missing 'message' in error"
        
        print("✅ Invalid JSON test passed")
        return True
    except (json.JSONDecodeError, AssertionError) as e:
        print(f"❌ Invalid JSON test failed: {str(e)}")
        return False

def run_tests(server_command):
    """Run all tests against the specified server"""
    print(f"Testing JSON-RPC 2.0 compliance of: {server_command}")
    
    try:
        # Start the server process
        server_process = subprocess.Popen(
            server_command,
            shell=True,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1
        )
        
        # Create a thread to read stderr and log it
        def log_stderr():
            for line in server_process.stderr:
                print(f"[SERVER] {line.strip()}")
        
        stderr_thread = threading.Thread(target=log_stderr, daemon=True)
        stderr_thread.start()
        
        # Run the tests
        tests = [
            ("Initialize", test_initialize),
            ("Function Call", test_function_call),
            ("Error Handling", test_error_handling),
            ("Invalid JSON", test_invalid_json)
        ]
        
        results = []
        for name, test_func in tests:
            try:
                result = test_func(server_process)
                results.append((name, result))
            except Exception as e:
                print(f"Exception during test {name}: {str(e)}")
                results.append((name, False))
        
        # Print summary
        print("\n=== Test Summary ===")
        all_passed = True
        for name, result in results:
            status = "✅ PASSED" if result else "❌ FAILED"
            print(f"{name}: {status}")
            all_passed = all_passed and result
        
        if all_passed:
            print("\n🎉 All tests passed! The server is JSON-RPC 2.0 compliant.")
        else:
            print("\n❌ Some tests failed. The server is not fully JSON-RPC 2.0 compliant.")
        
        # Terminate the server
        server_process.terminate()
        server_process.wait(timeout=5)
        
    except Exception as e:
        print(f"Error running tests: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Test JSON-RPC 2.0 compliance of MCP server")
    parser.add_argument("--server", default="docker run -i --rm mcp/simple-dependmap",
                        help="Command to run the server (default: 'docker run -i --rm mcp/simple-dependmap')")
    args = parser.parse_args()
    
    run_tests(args.server) 