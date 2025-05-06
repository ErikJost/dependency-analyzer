#!/usr/bin/env python3
"""
Error handling utilities for MCP API.

This module provides standard error handling for the MCP API,
with consistent error codes, messages, and formatting.
"""

import json
import traceback
import uuid
from typing import Dict, Any, Optional
from datetime import datetime

# Import structured logging
from structured_logging import get_logger, create_correlation_id

# Configure logger
logger = get_logger("mcp_error_handler")

# Standard error codes and their descriptions
ERROR_CODES = {
    # General errors
    "server_error": "An unexpected server error occurred",
    "not_found": "The requested resource was not found",
    "invalid_request": "The request was invalid",
    "validation_error": "The request parameters failed validation",
    
    # Authentication and authorization errors
    "unauthorized": "Authentication is required to access this resource",
    "forbidden": "You do not have permission to access this resource",
    
    # Tool-specific errors
    "unknown_tool": "The requested tool is not available",
    "tool_execution_failed": "The tool execution failed",
    
    # Resource-specific errors
    "invalid_resource_uri": "The resource URI format is invalid",
    "resource_not_found": "The requested resource was not found",
    "resource_access_failed": "Failed to access the resource",
    
    # Project-specific errors
    "project_not_found": "The requested project was not found",
    "project_exists": "A project with this name already exists",
    "invalid_source": "The source is not a valid URL or path",
    "git_clone_failed": "Failed to clone the Git repository",
    "copy_failed": "Failed to copy the project files",
    
    # Analysis-specific errors
    "analysis_failed": "Dependency analysis failed",
    "no_analysis": "No dependency analysis found for this project",
    "graph_load_failed": "Failed to load the dependency graph",
    "orphaned_analysis_failed": "Failed to analyze orphaned files",
    "circular_analysis_failed": "Failed to analyze circular dependencies",
    
    # Protocol-specific errors
    "invalid_json": "Invalid JSON received",
    "missing_tool": "Tool name is required",
    "missing_resource": "Resource URI is required",
    "handshake_failed": "Failed to complete protocol handshake"
}

def create_error_response(code: str, message: Optional[str] = None, details: Optional[Dict[str, Any]] = None, 
                          request_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Create a standardized error response.
    
    Args:
        code: The error code (should be one from ERROR_CODES)
        message: Optional custom error message (if None, the standard message for the code is used)
        details: Optional dictionary with additional error details
        request_id: Optional request ID to include in the response
        
    Returns:
        A formatted error response dictionary
    """
    # Generate a correlation ID for this error
    correlation_id = details.get("correlation_id") if details else create_correlation_id()
    
    # Use the standard message if none provided
    if message is None:
        message = ERROR_CODES.get(code, "Unknown error")
    
    # Create the error object
    error_obj = {
        "code": code,
        "message": message,
        "error_id": str(uuid.uuid4())
    }
    
    if details:
        error_obj["details"] = details
    
    # Create the response
    response = {
        "status": "error",
        "error": error_obj,
        "timestamp": datetime.now().isoformat(),
        "correlation_id": correlation_id
    }
    
    if request_id:
        response["request_id"] = request_id
    
    # Log the error with structured data
    error_logger = logger.with_correlation_id(correlation_id)
    error_logger.error(
        f"Error [{code}]: {message}",
        error_code=code,
        error_id=error_obj["error_id"],
        request_id=request_id,
        details=details
    )
    
    return response

def handle_exception(e: Exception, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Handle an exception and create a standardized error response.
    
    Args:
        e: The exception to handle
        context: Optional dictionary with additional context about the request
        
    Returns:
        A formatted error response dictionary
    """
    # Generate a unique ID for this error
    error_id = str(uuid.uuid4())
    
    # Extract correlation ID from context if available
    correlation_id = context.get("correlation_id") if context else create_correlation_id()
    
    # Get the exception traceback
    tb = traceback.format_exc()
    
    # Get request ID from context if available
    request_id = context.get("request_id") if context else None
    
    # Log the error with structured data
    error_logger = logger.with_correlation_id(correlation_id)
    error_logger.error(
        f"Unhandled exception: {str(e)}",
        error_id=error_id,
        exception_type=type(e).__name__,
        traceback=tb,
        request_id=request_id,
        context=context
    )
    
    # Create the error response
    return create_error_response(
        code="server_error",
        message=f"An unexpected error occurred: {str(e)}",
        details={
            "error_id": error_id,
            "type": type(e).__name__,
            "correlation_id": correlation_id
        },
        request_id=request_id
    )

def get_http_status_for_error(code: str) -> int:
    """
    Map an error code to an appropriate HTTP status code.
    
    Args:
        code: The error code
        
    Returns:
        An HTTP status code
    """
    # Map error codes to HTTP status codes
    status_map = {
        # 400 Bad Request
        "invalid_request": 400,
        "validation_error": 400,
        "invalid_json": 400,
        "missing_tool": 400,
        "missing_resource": 400,
        "invalid_resource_uri": 400,
        
        # 401 Unauthorized
        "unauthorized": 401,
        
        # 403 Forbidden
        "forbidden": 403,
        
        # 404 Not Found
        "not_found": 404,
        "unknown_tool": 404,
        "resource_not_found": 404,
        "project_not_found": 404,
        
        # 409 Conflict
        "project_exists": 409,
        
        # 500 Internal Server Error (default)
        "server_error": 500,
        "tool_execution_failed": 500,
        "resource_access_failed": 500,
        "analysis_failed": 500,
        "graph_load_failed": 500,
        "orphaned_analysis_failed": 500,
        "circular_analysis_failed": 500,
        "git_clone_failed": 500,
        "copy_failed": 500,
        
        # 503 Service Unavailable
        "no_analysis": 503,
        "handshake_failed": 503
    }
    
    return status_map.get(code, 500)  # Default to 500 Internal Server Error 