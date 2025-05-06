#!/usr/bin/env python3
"""
MCP Server for Dependency Analysis - stdio Interface with JSON-RPC 2.0 compatibility

This module implements a stdio-based interface for the Model Context Protocol (MCP)
server, allowing direct interaction with AI agents through stdin/stdout streams.
Modified to be compatible with Cursor's JSON-RPC 2.0 expectations.

Usage:
    python3 stdio_mcp_updated.py
"""

import os
import sys
import json
import uuid
import traceback
import threading
import datetime
from typing import Dict, Any, Optional, List
import signal

# Import the MCP API module
from mcp_api import handle_mcp_request, handle_mcp_resource
from error_handler import create_error_response, handle_exception
from validation import validate_tool_parameters, validate_resource_uri
from structured_logging import get_logger, create_correlation_id
from streaming import streaming_manager, stream_over_stdio

# Configure logging to stderr to avoid interfering with the protocol on stdout
logger = get_logger("mcp_stdio", os.environ.get("LOG_LEVEL", "INFO"))

# Global state
active_requests = {}
streaming_operations = {}
is_shutting_down = False

def signal_handler(sig, frame):
    """Handle graceful shutdown on signals"""
    global is_shutting_down
    logger.info(f"Received signal {sig}, shutting down...")
    is_shutting_down = True
    # Finish processing any active requests before exiting
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

def read_message() -> Optional[Dict[str, Any]]:
    """Read a single message from stdin and parse as JSON-RPC 2.0 or MCP format"""
    try:
        line = sys.stdin.readline()
        if not line:
            logger.info("End of input stream detected, exiting")
            return None
        
        # Parse the JSON message
        message = json.loads(line.strip())
        
        # Check if this is JSON-RPC 2.0 format
        if "jsonrpc" in message and message.get("jsonrpc") == "2.0":
            # Convert to MCP format
            method = message.get("method", "")
            params = message.get("params", {})
            request_id = message.get("id", str(uuid.uuid4()))
            
            # Handle special methods
            if method == "initialize" or method == "mcp/listOfferings":
                return {
                    "handshake": True,
                    "version": "1.0",
                    "request_id": request_id,
                    "_jsonrpc_id": request_id  # Store original ID for response
                }
            elif method == "mcp/invokeFunction":
                tool = params.get("function", "")
                tool_params = params.get("parameters", {})
                return {
                    "type": "tool_call",
                    "tool": tool,
                    "parameters": tool_params,
                    "request_id": request_id,
                    "_jsonrpc_id": request_id  # Store original ID for response
                }
            else:
                # Generic method
                return {
                    "type": "generic_call",
                    "method": method,
                    "parameters": params,
                    "request_id": request_id,
                    "_jsonrpc_id": request_id  # Store original ID for response
                }
        
        # If not JSON-RPC, assume it's direct MCP format
        logger.debug("Received message", message_type=list(message.keys())[0] if message else None)
        return message
    except json.JSONDecodeError as e:
        logger.error("Failed to parse input as JSON", error=str(e), line=line[:100])
        send_error_response(None, "invalid_json", "Invalid JSON message received")
        return None
    except Exception as e:
        logger.error("Error reading message", error=str(e))
        return None

def send_response(request_id: Optional[str], response: Dict[str, Any]):
    """Send a response to stdout in JSON-RPC 2.0 format"""
    correlation_id = response.get("correlation_id", create_correlation_id())
    
    # Check if this was from a JSON-RPC request (has _jsonrpc_id)
    jsonrpc_id = response.pop("_jsonrpc_id", None) or request_id
    
    # Convert to JSON-RPC 2.0 format
    if "status" in response:
        if response["status"] == "success":
            jsonrpc_response = {
                "jsonrpc": "2.0",
                "id": jsonrpc_id,
                "result": response.get("data", {})
            }
        else:  # Error case
            error_data = response.get("error", {})
            jsonrpc_response = {
                "jsonrpc": "2.0",
                "id": jsonrpc_id,
                "error": {
                    "code": -32000,  # Generic server error
                    "message": error_data.get("message", "Unknown error"),
                    "data": error_data
                }
            }
    else:
        # Default case - treat as success
        jsonrpc_response = {
            "jsonrpc": "2.0",
            "id": jsonrpc_id,
            "result": response
        }
    
    # Special handling for handshake responses
    if "data" in response and "handshake" in response.get("data", {}):
        capabilities = response["data"].get("capabilities", {})
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
        
        jsonrpc_response = {
            "jsonrpc": "2.0",
            "id": jsonrpc_id,
            "result": {
                "functions": tools,
                "resources": [],
                "resourceTemplates": []
            }
        }
    
    # Log the response being sent
    logger.debug(
        "Sending response",
        response_type=jsonrpc_response.get("result") and "result" or "error",
        request_id=request_id,
        correlation_id=correlation_id
    )
    
    # Write the response to stdout as a single line
    print(json.dumps(jsonrpc_response), flush=True)

def send_error_response(request_id: Optional[str], error_code: str, error_message: str, details: Optional[Dict[str, Any]] = None):
    """Send an error response to stdout in JSON-RPC 2.0 format"""
    correlation_id = create_correlation_id()
    
    # Log the error
    logger.error(
        f"Error: {error_message}",
        error_code=error_code,
        request_id=request_id,
        correlation_id=correlation_id,
        details=details
    )
    
    # Create JSON-RPC 2.0 error response
    jsonrpc_response = {
        "jsonrpc": "2.0",
        "id": request_id or "null",
        "error": {
            "code": -32000,  # Generic server error
            "message": error_message,
            "data": {
                "code": error_code,
                "details": details,
                "correlation_id": correlation_id
            }
        }
    }
    
    # Write to stdout
    print(json.dumps(jsonrpc_response), flush=True)

def handle_streaming_tool_request(tool_name: str, params: Dict[str, Any], request_id: str, correlation_id: str):
    """Handle a streaming tool request that sends updates via stdio"""
    request_logger = logger.with_correlation_id(correlation_id)
    
    request_logger.info(
        f"Processing streaming tool request: {tool_name}",
        request_id=request_id,
        tool=tool_name,
        parameters=params
    )
    
    try:
        # Handle the tool request, which will start an asynchronous operation
        response = handle_mcp_request(tool_name, params)
        
        # Add JSON-RPC ID for response
        response["_jsonrpc_id"] = request_id
        
        # Send the initial response (with operation_id)
        send_response(request_id, response)
        
        # If the tool returned an operation_id for a streaming operation, start streaming updates
        if response.get("status") == "accepted" and "data" in response and "operation_id" in response["data"]:
            operation_id = response["data"]["operation_id"]
            
            # Register in active streaming operations
            streaming_operations[operation_id] = {
                "request_id": request_id,
                "correlation_id": correlation_id,
                "tool": tool_name
            }
            
            # Start a thread to stream updates
            operation = streaming_manager.get_operation(operation_id)
            if operation:
                threading.Thread(
                    target=stream_over_stdio,
                    args=(operation,),
                    daemon=True
                ).start()
                
                request_logger.info(
                    f"Started streaming updates for operation: {operation_id}",
                    operation_id=operation_id,
                    request_id=request_id
                )
    
    except Exception as e:
        request_logger.error(
            f"Error handling streaming tool request: {str(e)}",
            request_id=request_id,
            tool=tool_name,
            error=str(e),
            traceback=traceback.format_exc()
        )
        
        # Create error context for better debugging
        context = {
            "tool": tool_name,
            "request_id": request_id,
            "parameters": params,
            "correlation_id": correlation_id
        }
        
        # Use our standardized error handler
        error_response = handle_exception(e, context)
        error_response["correlation_id"] = correlation_id
        error_response["_jsonrpc_id"] = request_id
        send_response(request_id, error_response)

def handle_tool_request(message: Dict[str, Any]):
    """Handle an MCP tool request"""
    request_id = message.get("request_id", str(uuid.uuid4()))
    correlation_id = create_correlation_id()
    request_logger = logger.with_correlation_id(correlation_id)
    
    # Store the original JSON-RPC ID if present
    jsonrpc_id = message.pop("_jsonrpc_id", request_id)
    
    tool_name = message.get("tool")
    params = message.get("parameters", {})
    
    request_logger.info(
        f"Processing tool request: {tool_name}",
        request_id=request_id,
        tool=tool_name,
        parameters=params
    )
    
    if not tool_name:
        send_error_response(request_id, "missing_tool", "Tool name is required")
        return
    
    try:
        # Store the request in active requests
        active_requests[request_id] = {
            "tool": tool_name,
            "status": "processing",
            "started_at": datetime.datetime.now().isoformat(),
            "correlation_id": correlation_id
        }
        
        # Validate the tool parameters
        is_valid, error_details = validate_tool_parameters(tool_name, params)
        if not is_valid:
            request_logger.warning(
                "Invalid parameters for tool",
                tool=tool_name,
                error=error_details
            )
            
            send_error_response(
                jsonrpc_id,  # Use JSON-RPC ID for response
                error_details["code"], 
                error_details["message"],
                error_details.get("details")
            )
            return
        
        # Check if this is a streaming tool request (like analyze_dependencies with streaming=true)
        if tool_name == "analyze_dependencies" and params.get("streaming", False):
            # Handle in a separate thread to avoid blocking the main loop
            threading.Thread(
                target=handle_streaming_tool_request,
                args=(tool_name, params, jsonrpc_id, correlation_id),  # Use JSON-RPC ID
                daemon=True
            ).start()
            
            # Update the request status (the thread will handle the rest)
            active_requests[request_id]["status"] = "streaming"
            return
        
        # Handle regular (non-streaming) tool request
        response = handle_mcp_request(tool_name, params)
        
        # Update the request status
        active_requests[request_id]["status"] = "completed"
        active_requests[request_id]["completed_at"] = datetime.datetime.now().isoformat()
        
        # Add correlation ID to the response
        response["correlation_id"] = correlation_id
        
        # Add original JSON-RPC ID for response formatting
        response["_jsonrpc_id"] = jsonrpc_id
        
        # Send the response
        send_response(request_id, response)
        
        request_logger.info(
            f"Tool request completed: {tool_name}",
            request_id=request_id,
            tool=tool_name,
            status=response.get("status")
        )
        
    except Exception as e:
        request_logger.error(
            f"Error handling tool request: {str(e)}",
            request_id=request_id,
            tool=tool_name,
            error=str(e),
            traceback=traceback.format_exc()
        )
        
        # Create error context for better debugging
        context = {
            "tool": tool_name,
            "request_id": request_id,
            "parameters": params,
            "correlation_id": correlation_id
        }
        
        # Use our standardized error handler
        error_response = handle_exception(e, context)
        error_response["correlation_id"] = correlation_id
        error_response["_jsonrpc_id"] = jsonrpc_id
        send_response(request_id, error_response)
    finally:
        # Clean up the request from active requests
        if request_id in active_requests:
            del active_requests[request_id]

def handle_resource_request(message: Dict[str, Any]):
    """Handle an MCP resource request"""
    request_id = message.get("request_id", str(uuid.uuid4()))
    correlation_id = create_correlation_id()
    request_logger = logger.with_correlation_id(correlation_id)
    
    # Store the original JSON-RPC ID if present
    jsonrpc_id = message.pop("_jsonrpc_id", request_id)
    
    resource_uri = message.get("resource")
    
    request_logger.info(
        f"Processing resource request: {resource_uri}",
        request_id=request_id,
        resource_uri=resource_uri
    )
    
    if not resource_uri:
        send_error_response(jsonrpc_id, "missing_resource", "Resource URI is required")
        return
    
    try:
        # Store the request in active requests
        active_requests[request_id] = {
            "resource": resource_uri,
            "status": "processing",
            "started_at": datetime.datetime.now().isoformat(),
            "correlation_id": correlation_id
        }
        
        # Validate the resource URI
        is_valid, error_details = validate_resource_uri(resource_uri)
        if not is_valid:
            request_logger.warning(
                "Invalid resource URI",
                resource_uri=resource_uri,
                error=error_details
            )
            
            send_error_response(
                jsonrpc_id,
                error_details["code"], 
                error_details["message"],
                error_details.get("details")
            )
            return
        
        # Handle the resource request
        response = handle_mcp_resource(resource_uri)
        
        # Update the request status
        active_requests[request_id]["status"] = "completed"
        active_requests[request_id]["completed_at"] = datetime.datetime.now().isoformat()
        
        # Add correlation ID to the response
        response["correlation_id"] = correlation_id
        
        # Add original JSON-RPC ID for response formatting
        response["_jsonrpc_id"] = jsonrpc_id
        
        # Send the response
        send_response(request_id, response)
        
        request_logger.info(
            "Resource request completed",
            request_id=request_id,
            resource_uri=resource_uri,
            status=response.get("status")
        )
        
    except Exception as e:
        request_logger.error(
            f"Error handling resource request: {str(e)}",
            request_id=request_id,
            resource_uri=resource_uri,
            error=str(e),
            traceback=traceback.format_exc()
        )
        
        # Create error context for better debugging
        context = {
            "resource": resource_uri,
            "request_id": request_id,
            "correlation_id": correlation_id
        }
        
        # Use our standardized error handler
        error_response = handle_exception(e, context)
        error_response["correlation_id"] = correlation_id
        error_response["_jsonrpc_id"] = jsonrpc_id
        send_response(request_id, error_response)
    finally:
        # Clean up the request from active requests
        if request_id in active_requests:
            del active_requests[request_id]

def handle_handshake(message: Dict[str, Any]):
    """Handle MCP protocol handshake"""
    request_id = message.get("request_id", str(uuid.uuid4()))
    correlation_id = create_correlation_id()
    request_logger = logger.with_correlation_id(correlation_id)
    
    # Store the original JSON-RPC ID if present
    jsonrpc_id = message.pop("_jsonrpc_id", request_id)
    
    request_logger.info(
        "Processing handshake request",
        request_id=request_id,
        client_version=message.get("version", "unknown")
    )
    
    try:
        # Check protocol version compatibility
        client_version = message.get("version", "1.0")
        server_version = "1.0"  # Our current MCP version
        
        # For now, we only support version 1.0
        if client_version != server_version:
            request_logger.warning(
                "Protocol version mismatch",
                client_version=client_version,
                server_version=server_version
            )
        
        # Send capabilities, including streaming support
        capabilities = {
            "tools": [
                "list_projects",
                "add_project",
                "analyze_dependencies",
                "get_dependency_graph",
                "find_orphaned_files",
                "check_circular_dependencies",
                "get_operation_status",
                "cancel_operation",
                "list_operations"
            ],
            "resource_patterns": [
                "project://{project_id}/structure",
                "project://{project_id}/dependencies",
                "project://{project_id}/file/{path}/dependencies",
                "project://{project_id}/component/{component_name}/dependencies"
            ],
            "version": server_version,
            "extensions": ["streaming"],
            "features": {
                "streaming": True,
                "async_operations": True
            }
        }
        
        response = {
            "status": "success",
            "data": {
                "handshake": "accepted",
                "capabilities": capabilities
            },
            "correlation_id": correlation_id,
            "_jsonrpc_id": jsonrpc_id  # Include original JSON-RPC ID
        }
        
        send_response(request_id, response)
        
        request_logger.info(
            "Handshake completed successfully",
            request_id=request_id
        )
        
    except Exception as e:
        request_logger.error(
            f"Error handling handshake: {str(e)}",
            request_id=request_id,
            error=str(e),
            traceback=traceback.format_exc()
        )
        
        context = {
            "handshake_version": message.get("version"),
            "request_id": request_id,
            "correlation_id": correlation_id
        }
        error_response = handle_exception(e, context)
        error_response["correlation_id"] = correlation_id
        error_response["_jsonrpc_id"] = jsonrpc_id
        send_response(request_id, error_response)

def handle_status_request(message: Dict[str, Any]):
    """Handle status request for the MCP server"""
    request_id = message.get("request_id", str(uuid.uuid4()))
    correlation_id = create_correlation_id()
    request_logger = logger.with_correlation_id(correlation_id)
    
    # Store the original JSON-RPC ID if present
    jsonrpc_id = message.pop("_jsonrpc_id", request_id)
    
    request_logger.info(
        "Processing status request",
        request_id=request_id
    )
    
    try:
        # Get information about active requests
        active_request_count = len(active_requests)
        streaming_operation_count = len(streaming_operations)
        
        # Get server status information
        import psutil
        process = psutil.Process()
        memory_info = process.memory_info()
        
        status_info = {
            "active_requests": active_request_count,
            "streaming_operations": streaming_operation_count,
            "uptime": process.create_time(),
            "memory_usage": {
                "rss": memory_info.rss,
                "vms": memory_info.vms
            },
            "cpu_percent": process.cpu_percent(interval=0.1)
        }
        
        response = {
            "status": "success",
            "data": {
                "server_status": status_info
            },
            "correlation_id": correlation_id,
            "_jsonrpc_id": jsonrpc_id
        }
        
        send_response(request_id, response)
        
        request_logger.info(
            "Status request completed",
            request_id=request_id
        )
        
    except Exception as e:
        request_logger.error(
            f"Error handling status request: {str(e)}",
            request_id=request_id,
            error=str(e),
            traceback=traceback.format_exc()
        )
        
        context = {
            "request_type": "status",
            "request_id": request_id,
            "correlation_id": correlation_id
        }
        error_response = handle_exception(e, context)
        error_response["correlation_id"] = correlation_id
        error_response["_jsonrpc_id"] = jsonrpc_id
        send_response(request_id, error_response)

def handle_cancel_request(message: Dict[str, Any]):
    """Handle cancellation request for streaming operations"""
    request_id = message.get("request_id", str(uuid.uuid4()))
    correlation_id = create_correlation_id()
    request_logger = logger.with_correlation_id(correlation_id)
    
    # Store the original JSON-RPC ID if present
    jsonrpc_id = message.pop("_jsonrpc_id", request_id)
    
    operation_id = message.get("operation_id")
    
    request_logger.info(
        f"Processing cancel request for operation {operation_id}",
        request_id=request_id,
        operation_id=operation_id
    )
    
    if not operation_id:
        send_error_response(jsonrpc_id, "missing_operation_id", "Operation ID is required")
        return
    
    try:
        # Call the cancel operation tool
        response = handle_mcp_request("cancel_operation", {"operation_id": operation_id})
        
        # Add correlation ID to the response
        response["correlation_id"] = correlation_id
        response["_jsonrpc_id"] = jsonrpc_id
        
        # Send the response
        send_response(request_id, response)
        
        if response.get("status") == "success":
            # Clean up from streaming operations
            if operation_id in streaming_operations:
                del streaming_operations[operation_id]
            
            request_logger.info(
                f"Operation cancelled successfully: {operation_id}",
                request_id=request_id,
                operation_id=operation_id
            )
        else:
            request_logger.warning(
                f"Failed to cancel operation: {operation_id}",
                request_id=request_id,
                operation_id=operation_id,
                response=response
            )
        
    except Exception as e:
        request_logger.error(
            f"Error handling cancel request: {str(e)}",
            request_id=request_id,
            operation_id=operation_id,
            error=str(e),
            traceback=traceback.format_exc()
        )
        
        context = {
            "operation_id": operation_id,
            "request_id": request_id,
            "correlation_id": correlation_id
        }
        error_response = handle_exception(e, context)
        error_response["correlation_id"] = correlation_id
        error_response["_jsonrpc_id"] = jsonrpc_id
        send_response(request_id, error_response)

def main():
    """Main entry point for the stdio MCP server"""
    logger.info("Dependency Analyzer MCP Server (stdio interface) starting with JSON-RPC 2.0 support")
    
    # Process messages in a loop
    while not is_shutting_down:
        try:
            # Read a message from stdin
            message = read_message()
            
            # Exit if we've reached the end of the input stream
            if message is None:
                break
            
            # Determine the message type and handle accordingly
            if "tool" in message:
                handle_tool_request(message)
            elif "resource" in message:
                handle_resource_request(message)
            elif "handshake" in message:
                handle_handshake(message)
            elif "status" in message:
                handle_status_request(message)
            elif "cancel" in message and "operation_id" in message:
                handle_cancel_request(message)
            elif "method" in message:
                # Handle JSON-RPC style requests
                method = message.get("method", "")
                
                if method == "initialize" or method == "mcp/listOfferings":
                    handle_handshake({"handshake": True, "version": "1.0", "_jsonrpc_id": message.get("id")})
                elif method == "mcp/invokeFunction":
                    params = message.get("params", {})
                    function_name = params.get("function", "")
                    parameters = params.get("parameters", {})
                    
                    handle_tool_request({
                        "tool": function_name,
                        "parameters": parameters,
                        "request_id": str(uuid.uuid4()),
                        "_jsonrpc_id": message.get("id")
                    })
                else:
                    request_id = message.get("id", str(uuid.uuid4()))
                    send_error_response(
                        request_id,
                        "invalid_method",
                        f"Unrecognized method: {method}",
                        {"method": method}
                    )
            else:
                request_id = message.get("request_id", str(uuid.uuid4()))
                jsonrpc_id = message.get("id", request_id)
                correlation_id = create_correlation_id()
                
                logger.warning(
                    "Unrecognized message format",
                    request_id=request_id,
                    correlation_id=correlation_id,
                    message_keys=list(message.keys())
                )
                
                send_error_response(
                    jsonrpc_id,
                    "invalid_message",
                    "Unrecognized message format",
                    {"received_keys": list(message.keys())}
                )
        
        except Exception as e:
            logger.error(
                f"Unhandled exception in main loop: {str(e)}",
                error=str(e),
                traceback=traceback.format_exc()
            )
            
            # Try to extract a request ID if possible
            request_id = None
            if isinstance(message, dict):
                request_id = message.get("request_id") or message.get("id")
            
            # Send a generic error response
            correlation_id = create_correlation_id()
            
            # Send JSON-RPC 2.0 error response
            jsonrpc_response = {
                "jsonrpc": "2.0",
                "id": request_id or "null",
                "error": {
                    "code": -32000,  # Generic server error
                    "message": str(e),
                    "data": {
                        "location": "main_loop",
                        "correlation_id": correlation_id,
                        "traceback": traceback.format_exc()
                    }
                }
            }
            print(json.dumps(jsonrpc_response), flush=True)
    
    logger.info("Dependency Analyzer MCP Server shutting down")

if __name__ == "__main__":
    main() 