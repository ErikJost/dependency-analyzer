#!/usr/bin/env python3
"""
JSON-RPC 2.0 compliant stdio MCP Server for Dependency Analysis

This module implements a stdio-based server following strict JSON-RPC 2.0 format
for compatibility with Cursor's Model Context Protocol (MCP) integration.

Usage:
    python3 stdio_mcp_jsonrpc.py
"""

import os
import sys
import json
import uuid
import traceback
import threading
from typing import Dict, Any, Optional

class JSONRPC2Server:
    """
    JSON-RPC 2.0 server implementation for Cursor integration via stdio
    """
    
    def __init__(self, name="Dependency Analyzer"):
        self.name = name
        self.active = True
        self.operations = {}
        
        # Available tools - these will be offered to Cursor
        self.tools = [
            "list_projects",
            "add_project",
            "analyze_dependencies",
            "get_dependency_graph",
            "find_orphaned_files",
            "check_circular_dependencies",
            "get_operation_status",
            "cancel_operation",
            "list_operations"
        ]
        
        # Print debug info to stderr
        self._log(f"JSON-RPC 2.0 Server starting - PID: {os.getpid()}")
    
    def _log(self, message: str):
        """Log a message to stderr"""
        print(message, file=sys.stderr)
        sys.stderr.flush()
    
    def handle_initialize(self, request_id: str) -> Dict[str, Any]:
        """
        Handle an initialize or listOfferings request
        
        This creates the response with available tools in the format Cursor expects.
        """
        # Build the functions list for the initialize response
        functions = []
        for tool_name in self.tools:
            functions.append({
                "name": tool_name,
                "description": f"Dependency analyzer tool: {tool_name}",
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            })
        
        # Create a standard JSON-RPC 2.0 response
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "protocolVersion": "0.1.0",
                "serverInfo": {
                    "name": self.name,
                    "version": "1.0.0"
                },
                "capabilities": {
                    "functions": functions,
                    "resources": {},
                    "resourceTemplates": []
                }
            }
        }
    
    def handle_function_call(self, request_id: str, function_name: str, 
                            parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle a function call request
        
        This dispatches to the appropriate tool function or returns an error.
        """
        # Check if the function exists
        if function_name not in self.tools:
            return self.create_error_response(
                request_id, 
                -32601, 
                f"Function not found: {function_name}"
            )
        
        # For now, just echo back a simple response - you would implement actual functionality here
        # Each real tool would be implemented as a separate method
        
        # Example implementation for list_projects
        if function_name == "list_projects":
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "projects": [
                        {"id": "project1", "name": "Sample Project"}
                    ]
                }
            }
        
        # For other functions, return a placeholder
        # In a real implementation, you would dispatch to actual tool functions
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "function": function_name,
                "status": "success",
                "message": f"Function {function_name} called with parameters {parameters}"
            }
        }
    
    def create_error_response(self, request_id: str, code: int, message: str, 
                             data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Create a JSON-RPC 2.0 error response
        """
        error = {
            "code": code,
            "message": message
        }
        
        if data:
            error["data"] = data
            
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "error": error
        }
    
    def process_message(self, message: str) -> Optional[Dict[str, Any]]:
        """
        Process a raw message and return a response
        """
        try:
            # Parse the message as JSON
            request = json.loads(message)
            
            # Ensure this is a valid JSON-RPC 2.0 request
            if "jsonrpc" not in request or request["jsonrpc"] != "2.0":
                return self.create_error_response(
                    request.get("id", "null"), 
                    -32600, 
                    "Invalid Request: Not a valid JSON-RPC 2.0 request"
                )
            
            # Get the request ID
            request_id = request.get("id", "null")
            
            # Handle initialization request
            if request.get("method") == "initialize" or request.get("method") == "mcp/listOfferings":
                self._log(f"Received initialize request: ID {request_id}")
                return self.handle_initialize(request_id)
            
            # Handle function invocation
            elif request.get("method") == "mcp/invokeFunction":
                params = request.get("params", {})
                function_name = params.get("function", "")
                parameters = params.get("parameters", {})
                
                self._log(f"Received function call: {function_name}, ID {request_id}")
                return self.handle_function_call(request_id, function_name, parameters)
            
            # Unknown method
            else:
                return self.create_error_response(
                    request_id,
                    -32601,
                    f"Method not found: {request.get('method')}"
                )
                
        except json.JSONDecodeError:
            # Invalid JSON
            return self.create_error_response("null", -32700, "Parse error: Invalid JSON")
        except Exception as e:
            # Unexpected error
            self._log(f"Error processing message: {str(e)}")
            self._log(traceback.format_exc())
            return self.create_error_response("null", -32603, f"Internal error: {str(e)}")
    
    def run(self):
        """
        Run the server, processing lines from stdin
        """
        self._log("JSON-RPC 2.0 MCP Server ready - waiting for requests")
        
        # Explicitly flush stdout to ensure Cursor can see that we're ready
        sys.stdout.flush()
        
        while self.active:
            try:
                # Read a line from stdin
                line = sys.stdin.readline()
                
                # Check for end of stream
                if not line:
                    self._log("End of input stream detected, exiting")
                    self.active = False
                    break
                
                # Process the message if not empty
                if line.strip():
                    self._log(f"Processing message: {line.strip()[:100]}...")
                    
                    # Process the message and get a response
                    response = self.process_message(line.strip())
                    
                    # Send the response if we have one
                    if response:
                        # Convert to JSON and send
                        json_response = json.dumps(response)
                        self._log(f"Sending response: {json_response[:100]}...")
                        
                        # Write to stdout and flush
                        print(json_response, flush=True)
                        sys.stdout.flush()
            
            except KeyboardInterrupt:
                self._log("Keyboard interrupt received, exiting")
                self.active = False
                break
            
            except Exception as e:
                self._log(f"Unexpected error in main loop: {str(e)}")
                self._log(traceback.format_exc())
                
                # Try to send an error response if possible
                try:
                    error_response = self.create_error_response(
                        "null", 
                        -32603, 
                        f"Internal server error: {str(e)}"
                    )
                    print(json.dumps(error_response), flush=True)
                except:
                    # If we can't even send an error response, just log
                    self._log("Failed to send error response")

def main():
    """Main entry point for the stdio JSON-RPC 2.0 MCP server"""
    server = JSONRPC2Server()
    server.run()

if __name__ == "__main__":
    main() 