#!/usr/bin/env python3
"""
MCP Protocol Compatibility Endpoints

This module implements the required endpoints for full MCP protocol compatibility,
allowing Cursor and other MCP clients to discover tools and capabilities.
"""

import json

# Define tool schemas
TOOL_SCHEMAS = {
    "list_projects": {
        "name": "list_projects",
        "description": "List all available projects for dependency analysis",
        "parameters": {
            "type": "object",
            "properties": {},
            "required": []
        },
        "returns": {
            "type": "object",
            "properties": {
                "projects": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "id": {"type": "string"},
                            "name": {"type": "string"},
                            "path": {"type": "string"}
                        }
                    }
                }
            }
        }
    },
    "add_project": {
        "name": "add_project",
        "description": "Add a new project for dependency analysis",
        "parameters": {
            "type": "object",
            "properties": {
                "name": {
                    "type": "string",
                    "description": "Name of the project"
                },
                "source": {
                    "type": "string",
                    "description": "Git repository URL or local directory path"
                },
                "branch": {
                    "type": "string",
                    "description": "Branch to clone (for git repositories)"
                }
            },
            "required": ["name", "source"]
        },
        "returns": {
            "type": "object",
            "properties": {
                "project": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "string"},
                        "name": {"type": "string"},
                        "path": {"type": "string"}
                    }
                }
            }
        }
    },
    "analyze_dependencies": {
        "name": "analyze_dependencies",
        "description": "Analyze dependencies for a project",
        "parameters": {
            "type": "object",
            "properties": {
                "project_id": {
                    "type": "string",
                    "description": "ID of the project to analyze"
                },
                "options": {
                    "type": "object",
                    "description": "Analysis options",
                    "properties": {
                        "exclude": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Patterns to exclude from analysis"
                        }
                    }
                }
            },
            "required": ["project_id"]
        },
        "returns": {
            "type": "object",
            "properties": {
                "project_id": {"type": "string"},
                "analysis_path": {"type": "string"}
            }
        }
    },
    "get_dependency_graph": {
        "name": "get_dependency_graph",
        "description": "Get the dependency graph for a project",
        "parameters": {
            "type": "object",
            "properties": {
                "project_id": {
                    "type": "string",
                    "description": "ID of the project"
                },
                "format": {
                    "type": "string",
                    "description": "Output format (json or d3)",
                    "enum": ["json", "d3"]
                }
            },
            "required": ["project_id"]
        },
        "returns": {
            "type": "object",
            "properties": {
                "graph": {"type": "object"}
            }
        }
    },
    "find_orphaned_files": {
        "name": "find_orphaned_files",
        "description": "Find files not referenced by any other files",
        "parameters": {
            "type": "object",
            "properties": {
                "project_id": {
                    "type": "string",
                    "description": "ID of the project"
                },
                "exclude_patterns": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Patterns to exclude from orphaned file search"
                }
            },
            "required": ["project_id"]
        },
        "returns": {
            "type": "object",
            "properties": {
                "orphaned_files": {
                    "type": "array",
                    "items": {"type": "string"}
                }
            }
        }
    },
    "check_circular_dependencies": {
        "name": "check_circular_dependencies",
        "description": "Check for circular dependencies in a project",
        "parameters": {
            "type": "object",
            "properties": {
                "project_id": {
                    "type": "string",
                    "description": "ID of the project"
                },
                "module": {
                    "type": "string",
                    "description": "Specific module to check (optional)"
                }
            },
            "required": ["project_id"]
        },
        "returns": {
            "type": "object",
            "properties": {
                "circular_dependencies": {
                    "type": "array",
                    "items": {
                        "type": "array",
                        "items": {"type": "string"}
                    }
                }
            }
        }
    }
}

def get_tools_list():
    """Return a list of tools with their schemas"""
    return {
        "status": "success",
        "data": {
            "tools": list(TOOL_SCHEMAS.values())
        },
        "metadata": {
            "count": len(TOOL_SCHEMAS)
        }
    }

def get_capabilities():
    """Return server capabilities in MCP format"""
    return {
        "status": "success",
        "data": {
            "name": "Dependency Analyzer MCP Server",
            "version": "1.0.0",
            "description": "MCP server for analyzing code dependencies",
            "capabilities": {
                "protocols": ["mcp/1.0"],
                "interfaces": ["http", "stdio"],
                "features": {
                    "streaming": True,
                    "async_operations": True,
                    "authentication": False,
                    "batch_requests": False
                },
                "tools": list(TOOL_SCHEMAS.keys()),
                "resources": [
                    "project://{project_id}/structure",
                    "project://{project_id}/dependencies",
                    "project://{project_id}/file/{path}/dependencies",
                    "project://{project_id}/component/{component_name}/dependencies"
                ]
            }
        }
    } 