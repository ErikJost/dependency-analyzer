#!/usr/bin/env python3
"""
Request validation utilities for MCP API.

This module provides functions to validate incoming requests against JSON schemas.
"""

import json
from typing import Dict, Any, Tuple, Optional, List

# Use jsonschema for validation
try:
    import jsonschema
    from jsonschema import ValidationError
    JSONSCHEMA_AVAILABLE = True
except ImportError:
    # Fallback if jsonschema isn't installed
    JSONSCHEMA_AVAILABLE = False

# Import schema definitions
from schemas import get_schema_for_tool

def validate_tool_parameters(tool_name: str, params: Dict[str, Any]) -> Tuple[bool, Optional[Dict[str, Any]]]:
    """
    Validate parameters for a tool against its JSON schema.
    
    Args:
        tool_name: The name of the tool to validate parameters for
        params: The parameters to validate
        
    Returns:
        Tuple containing (is_valid, error_details)
        - is_valid: Boolean indicating if the parameters are valid
        - error_details: None if validation passed, or a dict with error details if failed
    """
    # Get the schema for this tool
    schema = get_schema_for_tool(tool_name)
    
    # If no schema exists for this tool, consider it valid
    if schema is None:
        return True, None
    
    # If jsonschema isn't available, return valid but log a warning
    if not JSONSCHEMA_AVAILABLE:
        import logging
        logging.warning("jsonschema package not available, skipping validation")
        return True, None
    
    try:
        # Validate the parameters against the schema
        jsonschema.validate(instance=params, schema=schema)
        return True, None
    
    except ValidationError as e:
        # Build a detailed error message from the validation error
        path = '.'.join(str(p) for p in e.path) if e.path else None
        error_details = {
            "message": e.message,
            "path": path,
            "schema_path": '.'.join(str(p) for p in e.schema_path) if e.schema_path else None,
            "instance": e.instance
        }
        
        return False, {
            "code": "validation_error",
            "message": f"Invalid parameters for tool '{tool_name}'",
            "details": error_details
        }
    
    except Exception as e:
        # Catch any other validation-related exceptions
        return False, {
            "code": "validation_error",
            "message": f"Error validating parameters for tool '{tool_name}'",
            "details": {"error": str(e)}
        }

def format_validation_error(error: Dict[str, Any]) -> str:
    """Format a validation error into a human-readable message."""
    message = error.get("message", "Unknown validation error")
    
    if "details" in error:
        details = error["details"]
        
        if "path" in details and details["path"]:
            message += f" at '{details['path']}'"
            
        if "message" in details:
            message += f": {details['message']}"
    
    return message

def validate_resource_uri(resource_uri: str) -> Tuple[bool, Optional[Dict[str, Any]]]:
    """
    Validate a resource URI against supported patterns.
    
    Args:
        resource_uri: The resource URI to validate
        
    Returns:
        Tuple containing (is_valid, error_details)
    """
    # Define supported URI patterns
    supported_patterns = [
        "project://",  # Project resources
    ]
    
    # Check if the URI matches any supported pattern
    if not any(resource_uri.startswith(pattern) for pattern in supported_patterns):
        return False, {
            "code": "invalid_resource_uri",
            "message": "Unsupported resource URI format",
            "details": {
                "uri": resource_uri,
                "supported_patterns": supported_patterns
            }
        }
    
    # Additional validation for project URIs
    if resource_uri.startswith("project://"):
        # Format examples:
        # project://{project_id}/structure
        # project://{project_id}/dependencies
        # project://{project_id}/file/{path}/dependencies
        # project://{project_id}/component/{component_name}/dependencies
        
        # Parse the URI
        path = resource_uri[len("project://"):]
        parts = path.split("/")
        
        if len(parts) < 2:
            return False, {
                "code": "invalid_resource_uri",
                "message": "Invalid project resource URI format",
                "details": {
                    "uri": resource_uri,
                    "error": "Missing project ID or resource type"
                }
            }
        
        project_id = parts[0]
        if not project_id:
            return False, {
                "code": "invalid_resource_uri",
                "message": "Invalid project resource URI format",
                "details": {
                    "uri": resource_uri,
                    "error": "Empty project ID"
                }
            }
        
        resource_type = parts[1]
        valid_resource_types = ["structure", "dependencies", "file", "component"]
        
        if resource_type not in valid_resource_types:
            return False, {
                "code": "invalid_resource_uri",
                "message": "Invalid resource type in URI",
                "details": {
                    "uri": resource_uri,
                    "resource_type": resource_type,
                    "valid_types": valid_resource_types
                }
            }
        
        # Additional validation for file and component resources
        if resource_type == "file" and (len(parts) < 4 or parts[-1] != "dependencies"):
            return False, {
                "code": "invalid_resource_uri",
                "message": "Invalid file resource URI format",
                "details": {
                    "uri": resource_uri,
                    "expected_format": "project://{project_id}/file/{path}/dependencies"
                }
            }
        
        elif resource_type == "component" and (len(parts) < 4 or parts[-1] != "dependencies"):
            return False, {
                "code": "invalid_resource_uri",
                "message": "Invalid component resource URI format",
                "details": {
                    "uri": resource_uri,
                    "expected_format": "project://{project_id}/component/{component_name}/dependencies"
                }
            }
    
    # If all validation passes
    return True, None 