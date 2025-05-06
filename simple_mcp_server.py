#!/usr/bin/env python3
"""
Simple MCP Server for Dependency Analysis using FastMCP
"""
import os
import sys
import json
import uuid
import time
import traceback

# Create a basic MCP server that responds to JSON-RPC 2.0 format
class SimpleMCPServer:
    def __init__(self, name="Dependency Analyzer"):
        self.name = name
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
    
    def handle_message(self, message):
        # Parse the message
        try:
            data = json.loads(message)
            
            # Handle initialization
            if data.get("method") == "initialize" or data.get("method") == "mcp/listOfferings":
                return self._create_offerings_response(data.get("id", "null"))
            
            # Handle tool invocations
            elif data.get("method") == "mcp/invokeFunction":
                function_name = data.get("params", {}).get("function", "")
                parameters = data.get("params", {}).get("parameters", {})
                return self._handle_tool_call(data.get("id", "null"), function_name, parameters)
            
            # Unknown method
            else:
                return self._create_error_response(
                    data.get("id", "null"),
                    -32601,
                    f"Method {data.get('method')} not found"
                )
                
        except json.JSONDecodeError:
            return self._create_error_response("null", -32700, "Parse error")
        except Exception as e:
            self.log(f"Exception in handle_message: {str(e)}")
            self.log(traceback.format_exc())
            return self._create_error_response("null", -32603, f"Internal error: {str(e)}")
    
    def _create_offerings_response(self, id_value):
        """Create a JSON-RPC 2.0 response with tool offerings"""
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
        
        return {
            "jsonrpc": "2.0",
            "id": id_value,
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
    
    def _handle_tool_call(self, id_value, function_name, parameters):
        """Handle a tool call"""
        # For this simple example, just echo back the function name and parameters
        if function_name in self.tools:
            return {
                "jsonrpc": "2.0",
                "id": id_value,
                "result": {
                    "message": f"Called function {function_name} with parameters {parameters}",
                    "function": function_name,
                    "parameters": parameters
                }
            }
        else:
            return self._create_error_response(
                id_value,
                -32601,
                f"Function {function_name} not found"
            )
    
    def _create_error_response(self, id_value, code, message, data=None):
        """Create a JSON-RPC 2.0 error response"""
        error = {
            "code": code,
            "message": message
        }
        
        if data:
            error["data"] = data
            
        return {
            "jsonrpc": "2.0",
            "id": id_value,
            "error": error
        }

    def log(self, message):
        """Log a message to stderr and flush immediately"""
        print(message, file=sys.stderr)
        sys.stderr.flush()
    
    def run(self):
        """Run the server, processing lines from stdin"""
        self.log("Simple MCP Server starting - waiting for requests")
        self.log(f"Server PID: {os.getpid()}")
        self.log(f"Environment: {os.environ}")
        
        # For Cursor debugging - explicitly flush stdout
        sys.stdout.flush()
        
        # Track active status
        self.active = True
        
        while self.active:
            try:
                # Wait for input on stdin
                line = ""
                
                # Use raw stdin reading to avoid potential issues
                if not sys.stdin.isatty():
                    line = sys.stdin.readline()
                    if not line:
                        self.log("End of input stream detected, but staying alive")
                        # Sleep a bit to avoid CPU spinning
                        time.sleep(0.5)
                        continue
                else:
                    self.log("stdin is a terminal, waiting for input...")
                    time.sleep(1)
                    continue
                
                # Process if we have input
                if line.strip():
                    self.log(f"Received: {line.strip()[:200]}")
                    
                    # Process the message
                    response = self.handle_message(line.strip())
                    
                    # Send the response and ensure it's flushed
                    json_response = json.dumps(response)
                    self.log(f"Sending response for ID: {response.get('id')}")
                    self.log(f"Response content (first 200 chars): {json_response[:200]}")
                    
                    # Write to stdout and flush
                    print(json_response, flush=True)
                    sys.stdout.flush()
                
            except KeyboardInterrupt:
                self.log("Keyboard interrupt received, exiting")
                self.active = False
                break
            except Exception as e:
                self.log(f"Error in server loop: {str(e)}")
                self.log(traceback.format_exc())
                # Don't exit, try to recover
                time.sleep(1)

if __name__ == "__main__":
    server = SimpleMCPServer()
    server.run() 