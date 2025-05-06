#!/usr/bin/env python3
"""
JSON Schema definitions for MCP API validation.

This module provides JSON Schemas for validating MCP API request parameters.
"""

import json
from typing import Dict, Any, Optional

# JSON Schema for list_projects (no parameters required)
LIST_PROJECTS_SCHEMA = {
    "type": "object",
    "properties": {},
    "additionalProperties": False
}

# JSON Schema for add_project
ADD_PROJECT_SCHEMA = {
    "type": "object",
    "required": ["name", "source"],
    "properties": {
        "name": {
            "type": "string",
            "minLength": 1,
            "description": "Project name"
        },
        "source": {
            "type": "string",
            "minLength": 1,
            "description": "Project source (Git URL or local path)"
        },
        "branch": {
            "type": "string",
            "description": "Git branch to checkout (optional)"
        }
    },
    "additionalProperties": False
}

# JSON Schema for analyze_dependencies
ANALYZE_DEPENDENCIES_SCHEMA = {
    "type": "object",
    "required": ["project_id"],
    "properties": {
        "project_id": {
            "type": "string",
            "minLength": 1,
            "description": "Project identifier"
        },
        "options": {
            "type": "object",
            "properties": {
                "exclude": {
                    "type": "array",
                    "items": {
                        "type": "string"
                    },
                    "description": "Patterns to exclude from analysis"
                }
            },
            "additionalProperties": False
        },
        "streaming": {
            "type": "boolean",
            "default": False,
            "description": "Whether to use streaming mode for long-running analysis"
        }
    },
    "additionalProperties": False
}

# JSON Schema for get_dependency_graph
GET_DEPENDENCY_GRAPH_SCHEMA = {
    "type": "object",
    "required": ["project_id"],
    "properties": {
        "project_id": {
            "type": "string",
            "minLength": 1,
            "description": "Project identifier"
        },
        "format": {
            "type": "string",
            "enum": ["json", "d3"],
            "default": "json",
            "description": "Output format for the dependency graph"
        }
    },
    "additionalProperties": False
}

# JSON Schema for find_orphaned_files
FIND_ORPHANED_FILES_SCHEMA = {
    "type": "object",
    "required": ["project_id"],
    "properties": {
        "project_id": {
            "type": "string",
            "minLength": 1,
            "description": "Project identifier"
        },
        "exclude_patterns": {
            "type": "array",
            "items": {
                "type": "string"
            },
            "description": "Patterns to exclude from orphaned files list"
        }
    },
    "additionalProperties": False
}

# JSON Schema for check_circular_dependencies
CHECK_CIRCULAR_DEPENDENCIES_SCHEMA = {
    "type": "object",
    "required": ["project_id"],
    "properties": {
        "project_id": {
            "type": "string",
            "minLength": 1,
            "description": "Project identifier"
        },
        "module": {
            "type": ["string", "null"],
            "description": "Optional module name to filter circular dependencies"
        }
    },
    "additionalProperties": False
}

# JSON Schema for get_operation_status
GET_OPERATION_STATUS_SCHEMA = {
    "type": "object",
    "required": ["operation_id"],
    "properties": {
        "operation_id": {
            "type": "string",
            "minLength": 1,
            "description": "Operation identifier"
        }
    },
    "additionalProperties": False
}

# JSON Schema for cancel_operation
CANCEL_OPERATION_SCHEMA = {
    "type": "object",
    "required": ["operation_id"],
    "properties": {
        "operation_id": {
            "type": "string",
            "minLength": 1,
            "description": "Operation identifier"
        }
    },
    "additionalProperties": False
}

# JSON Schema for list_operations
LIST_OPERATIONS_SCHEMA = {
    "type": "object",
    "properties": {},
    "additionalProperties": False
}

# Map of tool names to their schemas
TOOL_SCHEMAS = {
    "list_projects": LIST_PROJECTS_SCHEMA,
    "add_project": ADD_PROJECT_SCHEMA,
    "analyze_dependencies": ANALYZE_DEPENDENCIES_SCHEMA,
    "get_dependency_graph": GET_DEPENDENCY_GRAPH_SCHEMA,
    "find_orphaned_files": FIND_ORPHANED_FILES_SCHEMA,
    "check_circular_dependencies": CHECK_CIRCULAR_DEPENDENCIES_SCHEMA,
    "get_operation_status": GET_OPERATION_STATUS_SCHEMA,
    "cancel_operation": CANCEL_OPERATION_SCHEMA,
    "list_operations": LIST_OPERATIONS_SCHEMA
}

def get_schema_for_tool(tool_name: str) -> Optional[Dict[str, Any]]:
    """Get the JSON Schema for a specific tool."""
    return TOOL_SCHEMAS.get(tool_name) 