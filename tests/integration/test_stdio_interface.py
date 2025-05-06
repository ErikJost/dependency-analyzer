#!/usr/bin/env python3
"""
Integration tests for stdio_mcp interface.

This module tests the MCP protocol handler using stdin/stdout streams.
"""

import io
import json
import sys
import pytest
from unittest.mock import patch, MagicMock

# Import the stdio handler - adjust import as needed
import stdio_mcp

class TestStdioInterface:
    """Tests for the stdio MCP interface"""

    @patch('sys.stdin')
    @patch('sys.stdout', new_callable=io.StringIO)
    def test_mcp_handshake(self, mock_stdout, mock_stdin):
        """Test the MCP handshake protocol"""
        # Prepare mock input (stdin)
        handshake_request = json.dumps({
            "jsonrpc": "2.0",
            "method": "mcp.handshake",
            "params": {
                "version": "0.1.0",
                "capabilities": ["tools"]
            },
            "id": "handshake-1"
        }) + "\n"
        
        mock_stdin.readline.return_value = handshake_request
        
        # Create a mock handler to capture the output without actually running the message loop
        with patch.object(stdio_mcp, 'handle_message', return_value=None) as mock_handler:
            # Mock the message loop to run only once
            with patch.object(stdio_mcp, 'message_loop', side_effect=lambda: mock_handler(json.loads(handshake_request))):
                # Run the stdio handler
                stdio_mcp.main()
                
                # Check that the handler was called with the handshake request
                mock_handler.assert_called_once()
                
                # Get the stdout content and parse it as JSON
                response_str = mock_stdout.getvalue().strip()
                response = json.loads(response_str)
                
                # Verify the response structure
                assert response["jsonrpc"] == "2.0"
                assert response["id"] == "handshake-1"
                assert "result" in response
                assert "version" in response["result"]
                assert "capabilities" in response["result"]
                assert "tools" in response["result"]["capabilities"]

    @patch('sys.stdin')
    @patch('sys.stdout', new_callable=io.StringIO)
    def test_tool_request(self, mock_stdout, mock_stdin):
        """Test a basic tool request and response"""
        # Prepare mock input (stdin)
        tool_request = json.dumps({
            "jsonrpc": "2.0",
            "method": "mcp.execute_tool",
            "params": {
                "tool": "list_projects",
                "parameters": {}
            },
            "id": "tool-1"
        }) + "\n"
        
        mock_stdin.readline.return_value = tool_request
        
        # Mock the list_projects function
        mock_result = {
            "status": "success",
            "projects": [
                {
                    "id": "test-project",
                    "name": "Test Project",
                    "source": "https://github.com/user/test-project.git"
                }
            ]
        }
        
        # Mock the execute_tool function
        with patch.object(stdio_mcp, 'execute_tool', return_value=mock_result) as mock_execute:
            # Mock the message loop to run only once
            with patch.object(stdio_mcp, 'message_loop', side_effect=lambda: stdio_mcp.handle_message(json.loads(tool_request))):
                # Run the stdio handler
                stdio_mcp.main()
                
                # Check that execute_tool was called with correct arguments
                mock_execute.assert_called_once_with("list_projects", {})
                
                # Get the stdout content and parse it as JSON
                response_str = mock_stdout.getvalue().strip()
                response = json.loads(response_str)
                
                # Verify the response structure
                assert response["jsonrpc"] == "2.0"
                assert response["id"] == "tool-1"
                assert "result" in response
                assert response["result"]["status"] == "success"
                assert "projects" in response["result"]
                assert len(response["result"]["projects"]) == 1
                assert response["result"]["projects"][0]["id"] == "test-project"

    @patch('sys.stdin')
    @patch('sys.stdout', new_callable=io.StringIO)
    def test_invalid_json(self, mock_stdout, mock_stdin):
        """Test handling of invalid JSON input"""
        # Prepare invalid JSON input
        invalid_json = "{ this is not valid JSON }\n"
        
        mock_stdin.readline.return_value = invalid_json
        
        # Mock the message loop to run only once and handle the error
        with patch.object(stdio_mcp, 'message_loop', side_effect=lambda: stdio_mcp.handle_raw_message(invalid_json)):
            # Run the stdio handler
            stdio_mcp.main()
            
            # Get the stdout content and parse it as JSON
            response_str = mock_stdout.getvalue().strip()
            response = json.loads(response_str)
            
            # Verify error response structure
            assert response["jsonrpc"] == "2.0"
            assert "error" in response
            assert response["error"]["code"] == -32700  # Parse error code
            assert "id" in response  # Should be null for parse errors
            assert response["id"] is None

    @patch('sys.stdin')
    @patch('sys.stdout', new_callable=io.StringIO)
    def test_invalid_request(self, mock_stdout, mock_stdin):
        """Test handling of invalid request structure"""
        # Prepare request with missing required fields
        invalid_request = json.dumps({
            # Missing jsonrpc and method fields
            "params": {},
            "id": "invalid-1"
        }) + "\n"
        
        mock_stdin.readline.return_value = invalid_request
        
        # Mock the message loop to run only once
        with patch.object(stdio_mcp, 'message_loop', side_effect=lambda: stdio_mcp.handle_message(json.loads(invalid_request))):
            # Run the stdio handler
            stdio_mcp.main()
            
            # Get the stdout content and parse it as JSON
            response_str = mock_stdout.getvalue().strip()
            response = json.loads(response_str)
            
            # Verify error response structure
            assert response["jsonrpc"] == "2.0"
            assert "error" in response
            assert response["error"]["code"] == -32600  # Invalid request error code
            assert "id" in response
            assert response["id"] == "invalid-1"

    @patch('sys.stdin')
    @patch('sys.stdout', new_callable=io.StringIO)
    def test_method_not_found(self, mock_stdout, mock_stdin):
        """Test handling of unknown method"""
        # Prepare request with unknown method
        unknown_method = json.dumps({
            "jsonrpc": "2.0",
            "method": "unknown.method",
            "params": {},
            "id": "unknown-1"
        }) + "\n"
        
        mock_stdin.readline.return_value = unknown_method
        
        # Mock the message loop to run only once
        with patch.object(stdio_mcp, 'message_loop', side_effect=lambda: stdio_mcp.handle_message(json.loads(unknown_method))):
            # Run the stdio handler
            stdio_mcp.main()
            
            # Get the stdout content and parse it as JSON
            response_str = mock_stdout.getvalue().strip()
            response = json.loads(response_str)
            
            # Verify error response structure
            assert response["jsonrpc"] == "2.0"
            assert "error" in response
            assert response["error"]["code"] == -32601  # Method not found error code
            assert "id" in response
            assert response["id"] == "unknown-1" 