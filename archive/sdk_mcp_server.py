#!/usr/bin/env python3
"""
MCP server for Dependency Analysis using JSON-RPC 2.0 fallback implementation for Cursor compatibility.

Usage:
    python3 sdk_mcp_server.py
"""

import sys
import os
import json
import uuid
import traceback
from typing import Dict, Any, List, Optional

class FallbackMCPServer:
    def __init__(self, name="Dependency Analyzer"):
        self.name = name
        self.version = "1.0.0"
        self.active = True
        self.functions = [
            {
                "name": "list_projects",
                "description": "Lists all projects available for analysis",
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            }
        ]
        self.projects = {
            "project1": {
                "id": "project1",
                "name": "Sample Project 1",
                "path": "/path/to/sample1"
            },
            "project2": {
                "id": "project2",
                "name": "Sample Project 2",
                "path": "/path/to/sample2"
            }
        }
        self.analysis_results = {}
        print(f"Fallback MCP Server starting - Name: {name}, Version: {self.version}", file=sys.stderr)

    def _log(self, message):
        print(message, file=sys.stderr)
        sys.stderr.flush()

    def handle_initialize(self, request_id):
        self._log(f"Handling initialize request: {request_id}")
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "protocolVersion": "1.0.0",
                "serverInfo": {
                    "name": self.name,
                    "version": self.version
                },
                "capabilities": {
                    "functions": self.functions,
                    "resources": {},
                    "resourceTemplates": []
                }
            }
        }

    def handle_function_call(self, request_id, function_name, params):
        self._log(f"Handling function call: {function_name}, {params}")
        if function_name == "list_projects":
            return self.handle_list_projects(request_id)
        elif function_name == "add_project":
            return self.handle_add_project(request_id, params)
        elif function_name == "analyze_dependencies":
            return self.handle_analyze_dependencies(request_id, params)
        elif function_name == "get_dependency_graph":
            return self.handle_get_dependency_graph(request_id, params)
        elif function_name == "find_orphaned_files":
            return self.handle_find_orphaned_files(request_id, params)
        elif function_name == "check_circular_dependencies":
            return self.handle_check_circular_dependencies(request_id, params)
        else:
            return self.create_error_response(request_id, -32601, f"Method not found: {function_name}")

    def handle_list_projects(self, request_id):
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "projects": list(self.projects.values())
            }
        }

    def handle_add_project(self, request_id, params):
        path = params.get("path", "")
        name = params.get("name", f"Project-{uuid.uuid4().hex[:8]}")
        project_id = f"project-{uuid.uuid4().hex[:8]}"
        self.projects[project_id] = {
            "id": project_id,
            "name": name,
            "path": path
        }
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "project": self.projects[project_id]
            }
        }

    def handle_analyze_dependencies(self, request_id, params):
        project_id = params.get("project_id", "")
        if project_id not in self.projects:
            return self.create_error_response(request_id, -32000, f"Project not found: {project_id}")
        operation_id = f"op-{uuid.uuid4().hex}"
        self.analysis_results[project_id] = {
            "files_analyzed": 42,
            "dependencies_found": 156,
            "graph": {
                "nodes": [
                    {"id": "file1.js", "type": "JavaScript"},
                    {"id": "file2.js", "type": "JavaScript"},
                    {"id": "utils.js", "type": "JavaScript"}
                ],
                "edges": [
                    {"source": "file1.js", "target": "utils.js"},
                    {"source": "file2.js", "target": "utils.js"}
                ]
            }
        }
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "operation": {
                    "id": operation_id,
                    "status": "completed"
                },
                "result": self.analysis_results[project_id]
            }
        }

    def handle_get_dependency_graph(self, request_id, params):
        project_id = params.get("project_id", "")
        if project_id not in self.projects:
            return self.create_error_response(request_id, -32000, f"Project not found: {project_id}")
        if project_id not in self.analysis_results:
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "graph": {
                        "nodes": [],
                        "edges": []
                    }
                }
            }
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "graph": self.analysis_results[project_id]["graph"]
            }
        }

    def handle_find_orphaned_files(self, request_id, params):
        project_id = params.get("project_id", "")
        if project_id not in self.projects:
            return self.create_error_response(request_id, -32000, f"Project not found: {project_id}")
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "orphaned_files": [
                    {"path": "unused.js", "type": "JavaScript"},
                    {"path": "old_utils.js", "type": "JavaScript"}
                ]
            }
        }

    def handle_check_circular_dependencies(self, request_id, params):
        project_id = params.get("project_id", "")
        if project_id not in self.projects:
            return self.create_error_response(request_id, -32000, f"Project not found: {project_id}")
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "circular_dependencies": [
                    {
                        "cycle": ["moduleA.js", "moduleB.js", "moduleC.js", "moduleA.js"],
                        "severity": "high"
                    }
                ]
            }
        }

    def create_error_response(self, request_id, code, message, data=None):
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

    def process_message(self, message):
        try:
            request = json.loads(message)
            if "jsonrpc" not in request or request["jsonrpc"] != "2.0" or "method" not in request:
                return self.create_error_response(
                    request.get("id", "null"),
                    -32600,
                    "Invalid Request: Not a valid JSON-RPC 2.0 request"
                )
            method = request["method"]
            request_id = request.get("id", "null")
            if method == "initialize" or method == "mcp/listOfferings":
                return self.handle_initialize(request_id)
            elif method == "mcp/invokeFunction":
                params = request.get("params", {})
                function_name = params.get("function", "")
                function_params = params.get("parameters", {})
                return self.handle_function_call(request_id, function_name, function_params)
            else:
                return self.create_error_response(
                    request_id,
                    -32601,
                    f"Method not found: {method}"
                )
        except json.JSONDecodeError:
            return self.create_error_response("null", -32700, "Parse error: Invalid JSON")
        except Exception as e:
            self._log(f"Error processing message: {str(e)}")
            self._log(traceback.format_exc())
            return self.create_error_response("null", -32603, f"Internal error: {str(e)}")

    def run(self):
        self._log("MCP Server ready - waiting for requests")
        sys.stdout.flush()
        while self.active:
            try:
                line = sys.stdin.readline()
                if not line:
                    self._log("End of input stream detected, exiting")
                    self.active = False
                    break
                if line.strip():
                    self._log(f"Received message: {line.strip()[:100]}...")
                    response = self.process_message(line.strip())
                    json_response = json.dumps(response)
                    print(json_response, flush=True)
                    sys.stdout.flush()
            except KeyboardInterrupt:
                self._log("Keyboard interrupt received, exiting")
                self.active = False
                break
            except Exception as e:
                self._log(f"Unhandled exception in main loop: {str(e)}")
                self._log(traceback.format_exc())

def main():
    try:
        server = FallbackMCPServer()
        server.run()
    except Exception as e:
        print(f"Fatal error: {str(e)}", file=sys.stderr)
        traceback.print_exc(file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main() 