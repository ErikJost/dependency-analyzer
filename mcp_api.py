#!/usr/bin/env python3
"""
MCP API for Dependency Analyzer

This module implements the Model Context Protocol (MCP) API for the dependency analyzer,
allowing AI agents to interact with the code dependency data.
"""

import os
import json
import subprocess
from urllib.parse import unquote
from typing import Dict, List, Any, Optional, Union

# Constants for project and analysis directories
PROJECTS_DIR = os.environ.get("PROJECTS_DIR", os.path.join(os.getcwd(), "projects"))
ANALYSIS_DIR = os.environ.get("ANALYSIS_DIR", os.path.join(os.getcwd(), "analysis"))

# Ensure directories exist
os.makedirs(PROJECTS_DIR, exist_ok=True)
os.makedirs(ANALYSIS_DIR, exist_ok=True)

class MCPApi:
    """
    Main class implementing the MCP API for dependency analysis
    """
    
    def __init__(self):
        """Initialize the MCP API handler"""
        self.projects = self._load_projects()
    
    def _load_projects(self) -> Dict[str, Dict[str, Any]]:
        """Load existing projects from the projects directory"""
        projects = {}
        # Check each subdirectory in the projects directory
        for item in os.listdir(PROJECTS_DIR):
            project_dir = os.path.join(PROJECTS_DIR, item)
            if os.path.isdir(project_dir):
                # Check for project metadata
                metadata_path = os.path.join(project_dir, ".project-metadata.json")
                if os.path.exists(metadata_path):
                    try:
                        with open(metadata_path, 'r') as f:
                            metadata = json.load(f)
                            projects[item] = metadata
                    except Exception as e:
                        print(f"Error loading project metadata for {item}: {e}")
                else:
                    # Create basic metadata if doesn't exist
                    projects[item] = {
                        "id": item,
                        "name": item,
                        "path": project_dir,
                        "created_at": None
                    }
        return projects

    def _save_project_metadata(self, project_id: str, metadata: Dict[str, Any]) -> None:
        """Save project metadata to the project directory"""
        project_dir = os.path.join(PROJECTS_DIR, project_id)
        os.makedirs(project_dir, exist_ok=True)
        
        metadata_path = os.path.join(project_dir, ".project-metadata.json")
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)

    def _get_analysis_path(self, project_id: str) -> str:
        """Get the path to the analysis results for a project"""
        return os.path.join(ANALYSIS_DIR, project_id)

    # MCP Tool: list_projects
    def list_projects(self) -> Dict[str, Any]:
        """List all available projects"""
        return {
            "status": "success",
            "data": {
                "projects": list(self.projects.values())
            },
            "metadata": {
                "count": len(self.projects)
            }
        }

    # MCP Tool: add_project
    def add_project(self, name: str, source: str, branch: Optional[str] = None) -> Dict[str, Any]:
        """Add a new project for analysis"""
        project_id = name.lower().replace(" ", "-")
        
        # Check if project already exists
        if project_id in self.projects:
            return {
                "status": "error",
                "error": {
                    "code": "project_exists",
                    "message": f"Project '{name}' already exists",
                    "details": {"project_id": project_id}
                }
            }
        
        # Create project directory
        project_dir = os.path.join(PROJECTS_DIR, project_id)
        os.makedirs(project_dir, exist_ok=True)
        
        # If source is a git URL, clone the repository
        if source.startswith("http://") or source.startswith("https://") or source.startswith("git@"):
            try:
                cmd = ["git", "clone", source]
                if branch:
                    cmd.extend(["--branch", branch])
                cmd.append(project_dir)
                
                subprocess.run(cmd, check=True, capture_output=True)
            except subprocess.CalledProcessError as e:
                return {
                    "status": "error",
                    "error": {
                        "code": "git_clone_failed",
                        "message": "Failed to clone repository",
                        "details": {
                            "error": str(e),
                            "stdout": e.stdout.decode() if e.stdout else "",
                            "stderr": e.stderr.decode() if e.stderr else ""
                        }
                    }
                }
        # If source is a local path, copy the contents
        elif os.path.exists(source):
            try:
                # Use rsync or similar for copying
                subprocess.run(["rsync", "-av", f"{source}/", project_dir], check=True, capture_output=True)
            except subprocess.CalledProcessError as e:
                return {
                    "status": "error",
                    "error": {
                        "code": "copy_failed",
                        "message": "Failed to copy project files",
                        "details": {
                            "error": str(e),
                            "stdout": e.stdout.decode() if e.stdout else "",
                            "stderr": e.stderr.decode() if e.stderr else ""
                        }
                    }
                }
        else:
            return {
                "status": "error",
                "error": {
                    "code": "invalid_source",
                    "message": "Source is not a valid URL or path",
                    "details": {"source": source}
                }
            }
        
        # Create metadata
        import datetime
        metadata = {
            "id": project_id,
            "name": name,
            "source": source,
            "branch": branch,
            "path": project_dir,
            "created_at": datetime.datetime.now().isoformat()
        }
        
        # Save metadata
        self._save_project_metadata(project_id, metadata)
        
        # Update projects dictionary
        self.projects[project_id] = metadata
        
        return {
            "status": "success",
            "data": {
                "project": metadata
            }
        }

    # MCP Tool: analyze_dependencies
    def analyze_dependencies(self, project_id: str, options: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Analyze dependencies for a project"""
        if project_id not in self.projects:
            return {
                "status": "error",
                "error": {
                    "code": "project_not_found",
                    "message": f"Project '{project_id}' not found",
                    "details": {"project_id": project_id}
                }
            }
        
        project = self.projects[project_id]
        project_dir = project["path"]
        
        # Create analysis directory
        analysis_dir = self._get_analysis_path(project_id)
        os.makedirs(analysis_dir, exist_ok=True)
        
        # Set default options
        if options is None:
            options = {}
        
        # Prepare command
        script_path = os.path.join(os.getcwd(), "scripts", "enhanced-dependency-analysis.cjs")
        cmd = ["node", script_path, f"--root-dir={project_dir}"]
        
        # Add options
        if "exclude" in options:
            excludes = options["exclude"]
            if isinstance(excludes, list):
                cmd.append(f"--exclude={','.join(excludes)}")
        
        # Run analysis
        try:
            result = subprocess.run(cmd, check=True, capture_output=True, text=True)
            
            # Parse output to determine if successful
            output_lines = result.stdout.split("\n")
            
            # Look for the generated dependency graph file
            dependency_graph_path = os.path.join(project_dir, "dependency-graph.json")
            if os.path.exists(dependency_graph_path):
                # Copy to analysis directory
                import shutil
                shutil.copy(dependency_graph_path, os.path.join(analysis_dir, "dependency-graph.json"))
            
            return {
                "status": "success",
                "data": {
                    "project_id": project_id,
                    "output": output_lines,
                    "analysis_path": analysis_dir
                },
                "metadata": {
                    "duration": None,  # Could calculate duration if needed
                    "timestamp": datetime.datetime.now().isoformat()
                }
            }
        
        except subprocess.CalledProcessError as e:
            return {
                "status": "error",
                "error": {
                    "code": "analysis_failed",
                    "message": "Dependency analysis failed",
                    "details": {
                        "project_id": project_id,
                        "error": str(e),
                        "stdout": e.stdout,
                        "stderr": e.stderr
                    }
                }
            }

    # MCP Tool: get_dependency_graph
    def get_dependency_graph(self, project_id: str, format: str = "json") -> Dict[str, Any]:
        """Retrieve the dependency graph for a project"""
        if project_id not in self.projects:
            return {
                "status": "error",
                "error": {
                    "code": "project_not_found",
                    "message": f"Project '{project_id}' not found",
                    "details": {"project_id": project_id}
                }
            }
        
        # Check if analysis has been run
        analysis_dir = self._get_analysis_path(project_id)
        graph_path = os.path.join(analysis_dir, "dependency-graph.json")
        
        if not os.path.exists(graph_path):
            return {
                "status": "error",
                "error": {
                    "code": "no_analysis",
                    "message": "No dependency analysis found for this project",
                    "details": {
                        "project_id": project_id,
                        "hint": "Run analyze_dependencies first"
                    }
                }
            }
        
        # Load the dependency graph
        try:
            with open(graph_path, 'r') as f:
                graph_data = json.load(f)
            
            # Format the output
            if format.lower() == "d3":
                # Convert to D3 format (nodes and links)
                d3_data = self._convert_to_d3(graph_data)
                return {
                    "status": "success",
                    "data": {
                        "graph": d3_data
                    }
                }
            else:
                # Return raw JSON
                return {
                    "status": "success",
                    "data": {
                        "graph": graph_data
                    }
                }
        
        except Exception as e:
            return {
                "status": "error",
                "error": {
                    "code": "graph_load_failed",
                    "message": "Failed to load dependency graph",
                    "details": {"error": str(e)}
                }
            }

    def _convert_to_d3(self, graph_data: Dict[str, Any]) -> Dict[str, Any]:
        """Convert dependency graph to D3 format (nodes and links)"""
        nodes = []
        links = []
        
        # Extract nodes and links
        for file_path, data in graph_data.items():
            # Add node
            node_id = len(nodes)
            nodes.append({
                "id": node_id,
                "name": file_path,
                "group": self._determine_group(file_path)
            })
            
            # Map file path to node ID
            path_to_id = {file_path: node_id}
            
            # Add links for imports
            for imported in data.get("imports", []):
                if imported not in path_to_id:
                    imported_id = len(nodes)
                    nodes.append({
                        "id": imported_id,
                        "name": imported,
                        "group": self._determine_group(imported)
                    })
                    path_to_id[imported] = imported_id
                
                links.append({
                    "source": node_id,
                    "target": path_to_id[imported],
                    "value": 1
                })
        
        return {
            "nodes": nodes,
            "links": links
        }

    def _determine_group(self, file_path: str) -> int:
        """Determine the group for a file based on its extension or directory"""
        if file_path.endswith('.ts') or file_path.endswith('.tsx'):
            return 1
        elif file_path.endswith('.js') or file_path.endswith('.jsx'):
            return 2
        elif file_path.endswith('.css') or file_path.endswith('.scss'):
            return 3
        elif '/components/' in file_path:
            return 4
        elif '/pages/' in file_path or '/views/' in file_path:
            return 5
        elif '/utils/' in file_path or '/helpers/' in file_path:
            return 6
        else:
            return 0

    # MCP Tool: find_orphaned_files
    def find_orphaned_files(self, project_id: str, exclude_patterns: Optional[List[str]] = None) -> Dict[str, Any]:
        """Find potentially orphaned files in a project"""
        if project_id not in self.projects:
            return {
                "status": "error",
                "error": {
                    "code": "project_not_found",
                    "message": f"Project '{project_id}' not found",
                    "details": {"project_id": project_id}
                }
            }
        
        # Check if analysis has been run
        analysis_dir = self._get_analysis_path(project_id)
        graph_path = os.path.join(analysis_dir, "dependency-graph.json")
        
        if not os.path.exists(graph_path):
            return {
                "status": "error",
                "error": {
                    "code": "no_analysis",
                    "message": "No dependency analysis found for this project",
                    "details": {
                        "project_id": project_id,
                        "hint": "Run analyze_dependencies first"
                    }
                }
            }
        
        try:
            # Load the dependency graph
            with open(graph_path, 'r') as f:
                graph_data = json.load(f)
            
            # Find files that are not imported anywhere
            all_files = set(graph_data.keys())
            imported_files = set()
            
            for file_path, data in graph_data.items():
                for imported in data.get("imports", []):
                    imported_files.add(imported)
            
            orphaned_files = all_files - imported_files
            
            # Filter by exclude patterns
            if exclude_patterns:
                import fnmatch
                filtered_orphaned = []
                for file in orphaned_files:
                    if not any(fnmatch.fnmatch(file, pattern) for pattern in exclude_patterns):
                        filtered_orphaned.append(file)
                orphaned_files = filtered_orphaned
            
            return {
                "status": "success",
                "data": {
                    "orphaned_files": list(orphaned_files)
                },
                "metadata": {
                    "count": len(orphaned_files),
                    "total_files": len(all_files)
                }
            }
        
        except Exception as e:
            return {
                "status": "error",
                "error": {
                    "code": "orphaned_analysis_failed",
                    "message": "Failed to analyze orphaned files",
                    "details": {"error": str(e)}
                }
            }

    # MCP Tool: check_circular_dependencies
    def check_circular_dependencies(self, project_id: str, module: Optional[str] = None) -> Dict[str, Any]:
        """Detect circular dependencies in a project"""
        if project_id not in self.projects:
            return {
                "status": "error",
                "error": {
                    "code": "project_not_found",
                    "message": f"Project '{project_id}' not found",
                    "details": {"project_id": project_id}
                }
            }
        
        # Check if analysis has been run
        analysis_dir = self._get_analysis_path(project_id)
        graph_path = os.path.join(analysis_dir, "dependency-graph.json")
        
        if not os.path.exists(graph_path):
            return {
                "status": "error",
                "error": {
                    "code": "no_analysis",
                    "message": "No dependency analysis found for this project",
                    "details": {
                        "project_id": project_id,
                        "hint": "Run analyze_dependencies first"
                    }
                }
            }
        
        try:
            # Load the dependency graph
            with open(graph_path, 'r') as f:
                graph_data = json.load(f)
            
            # Build a graph representation
            graph = {}
            for file_path, data in graph_data.items():
                graph[file_path] = data.get("imports", [])
            
            # Find circular dependencies
            circular = []
            
            def detect_cycles(start_node, current_path, visited, current_module):
                if module and current_module not in start_node:
                    return
                
                if start_node in current_path:
                    # Circular dependency found
                    cycle_start = current_path.index(start_node)
                    cycle = current_path[cycle_start:] + [start_node]
                    circular.append(cycle)
                    return
                
                if start_node in visited:
                    return
                
                visited.add(start_node)
                current_path.append(start_node)
                
                for neighbor in graph.get(start_node, []):
                    detect_cycles(neighbor, current_path.copy(), visited, current_module)
            
            # Start DFS from each node
            for node in graph:
                if module and module not in node:
                    continue
                detect_cycles(node, [], set(), module)
            
            # Remove duplicates (cycles that are the same but start from different nodes)
            unique_circular = []
            seen_cycles = set()
            
            for cycle in circular:
                # Sort cycle to normalize for comparison
                sorted_cycle = tuple(sorted(cycle))
                if sorted_cycle not in seen_cycles:
                    seen_cycles.add(sorted_cycle)
                    unique_circular.append(cycle)
            
            return {
                "status": "success",
                "data": {
                    "circular_dependencies": unique_circular
                },
                "metadata": {
                    "count": len(unique_circular),
                    "module_filter": module
                }
            }
        
        except Exception as e:
            return {
                "status": "error",
                "error": {
                    "code": "circular_analysis_failed",
                    "message": "Failed to analyze circular dependencies",
                    "details": {"error": str(e)}
                }
            }

    # MCP Resource handlers
    def handle_resource(self, resource_uri: str) -> Dict[str, Any]:
        """Handle resource URI requests"""
        try:
            # Parse the URI
            # Format examples:
            # project://{project_id}/structure
            # project://{project_id}/dependencies
            # project://{project_id}/file/{path}/dependencies
            # project://{project_id}/component/{component_name}/dependencies
            
            if resource_uri.startswith("project://"):
                # Remove the schema
                path = resource_uri[len("project://"):]
                
                # Split the path
                parts = path.split("/")
                
                if len(parts) < 2:
                    return {
                        "status": "error",
                        "error": {
                            "code": "invalid_resource_uri",
                            "message": "Invalid resource URI format",
                            "details": {"uri": resource_uri}
                        }
                    }
                
                project_id = parts[0]
                
                # Check if project exists
                if project_id not in self.projects:
                    return {
                        "status": "error",
                        "error": {
                            "code": "project_not_found",
                            "message": f"Project '{project_id}' not found",
                            "details": {"project_id": project_id}
                        }
                    }
                
                # Handle different resource types
                resource_type = parts[1]
                
                if resource_type == "structure":
                    # Return project structure
                    return self._get_project_structure(project_id)
                
                elif resource_type == "dependencies":
                    # Return dependency graph
                    return self.get_dependency_graph(project_id)
                
                elif resource_type == "file" and len(parts) >= 4 and parts[-1] == "dependencies":
                    # Parse file path
                    file_path = "/".join(parts[2:-1])
                    file_path = unquote(file_path)
                    return self._get_file_dependencies(project_id, file_path)
                
                elif resource_type == "component" and len(parts) >= 4 and parts[-1] == "dependencies":
                    # Parse component name
                    component_name = parts[2]
                    return self._get_component_dependencies(project_id, component_name)
            
            return {
                "status": "error",
                "error": {
                    "code": "unsupported_resource",
                    "message": "Unsupported resource URI",
                    "details": {"uri": resource_uri}
                }
            }
        
        except Exception as e:
            return {
                "status": "error",
                "error": {
                    "code": "resource_handler_error",
                    "message": "Error handling resource URI",
                    "details": {"error": str(e), "uri": resource_uri}
                }
            }

    def _get_project_structure(self, project_id: str) -> Dict[str, Any]:
        """Get the structure of a project"""
        project = self.projects[project_id]
        project_dir = project["path"]
        
        # Build a tree structure
        def build_tree(base_path: str, rel_path: str = ""):
            result = {"type": "directory", "name": os.path.basename(rel_path) or project_id, "children": []}
            
            full_path = os.path.join(base_path, rel_path)
            
            try:
                for item in sorted(os.listdir(full_path)):
                    item_rel_path = os.path.join(rel_path, item)
                    item_full_path = os.path.join(base_path, item_rel_path)
                    
                    # Skip hidden files and directories
                    if item.startswith("."):
                        continue
                    
                    # Skip node_modules and similar
                    if item in ["node_modules", "dist", "build", ".git"]:
                        continue
                    
                    if os.path.isdir(item_full_path):
                        # Recursively build tree for subdirectories
                        result["children"].append(build_tree(base_path, item_rel_path))
                    else:
                        # Add file
                        result["children"].append({
                            "type": "file",
                            "name": item,
                            "path": item_rel_path,
                            "extension": os.path.splitext(item)[1][1:] or None
                        })
            except Exception as e:
                print(f"Error building tree for {full_path}: {e}")
            
            return result
        
        tree = build_tree(project_dir)
        
        return {
            "status": "success",
            "data": {
                "structure": tree
            }
        }

    def _get_file_dependencies(self, project_id: str, file_path: str) -> Dict[str, Any]:
        """Get dependencies for a specific file"""
        # Check if analysis has been run
        analysis_dir = self._get_analysis_path(project_id)
        graph_path = os.path.join(analysis_dir, "dependency-graph.json")
        
        if not os.path.exists(graph_path):
            return {
                "status": "error",
                "error": {
                    "code": "no_analysis",
                    "message": "No dependency analysis found for this project",
                    "details": {
                        "project_id": project_id,
                        "hint": "Run analyze_dependencies first"
                    }
                }
            }
        
        try:
            # Load the dependency graph
            with open(graph_path, 'r') as f:
                graph_data = json.load(f)
            
            # Normalize the file path
            normalized_path = file_path
            if normalized_path.startswith("/"):
                normalized_path = normalized_path[1:]
            
            # Look for the file
            file_data = None
            matching_files = []
            
            # Check for exact match
            if normalized_path in graph_data:
                file_data = graph_data[normalized_path]
            else:
                # Try to find partial matches
                for path in graph_data:
                    if path.endswith(normalized_path):
                        matching_files.append(path)
            
            if file_data:
                # Get reverse dependencies (files that import this file)
                imported_by = []
                for other_path, other_data in graph_data.items():
                    if normalized_path in other_data.get("imports", []):
                        imported_by.append(other_path)
                
                return {
                    "status": "success",
                    "data": {
                        "file": normalized_path,
                        "imports": file_data.get("imports", []),
                        "imported_by": imported_by
                    }
                }
            elif matching_files:
                return {
                    "status": "success",
                    "data": {
                        "matching_files": matching_files,
                        "message": "Multiple files match this path. Please specify a more precise path."
                    }
                }
            else:
                return {
                    "status": "error",
                    "error": {
                        "code": "file_not_found",
                        "message": "File not found in dependency graph",
                        "details": {"file_path": file_path}
                    }
                }
        
        except Exception as e:
            return {
                "status": "error",
                "error": {
                    "code": "file_dependencies_failed",
                    "message": "Failed to get file dependencies",
                    "details": {"error": str(e)}
                }
            }

    def _get_component_dependencies(self, project_id: str, component_name: str) -> Dict[str, Any]:
        """Get dependencies for a specific component"""
        # Similar to file dependencies, but looks for files matching the component name
        # Check if analysis has been run
        analysis_dir = self._get_analysis_path(project_id)
        graph_path = os.path.join(analysis_dir, "dependency-graph.json")
        
        if not os.path.exists(graph_path):
            return {
                "status": "error",
                "error": {
                    "code": "no_analysis",
                    "message": "No dependency analysis found for this project",
                    "details": {
                        "project_id": project_id,
                        "hint": "Run analyze_dependencies first"
                    }
                }
            }
        
        try:
            # Load the dependency graph
            with open(graph_path, 'r') as f:
                graph_data = json.load(f)
            
            # Find files that might represent this component
            matching_files = []
            for path in graph_data:
                filename = os.path.basename(path)
                name_without_ext = os.path.splitext(filename)[0]
                
                if name_without_ext == component_name:
                    matching_files.append(path)
            
            if not matching_files:
                return {
                    "status": "error",
                    "error": {
                        "code": "component_not_found",
                        "message": "Component not found in dependency graph",
                        "details": {"component_name": component_name}
                    }
                }
            
            # Get dependencies for all matching files
            component_data = []
            for file_path in matching_files:
                file_data = graph_data[file_path]
                
                # Get reverse dependencies
                imported_by = []
                for other_path, other_data in graph_data.items():
                    if file_path in other_data.get("imports", []):
                        imported_by.append(other_path)
                
                component_data.append({
                    "file": file_path,
                    "imports": file_data.get("imports", []),
                    "imported_by": imported_by
                })
            
            return {
                "status": "success",
                "data": {
                    "component": component_name,
                    "files": component_data
                }
            }
        
        except Exception as e:
            return {
                "status": "error",
                "error": {
                    "code": "component_dependencies_failed",
                    "message": "Failed to get component dependencies",
                    "details": {"error": str(e)}
                }
            }

# Create a singleton instance
mcp_api = MCPApi()

# Function to handle MCP API requests
def handle_mcp_request(tool_name: str, params: Dict[str, Any]) -> Dict[str, Any]:
    """Handle an MCP API request"""
    # Validate parameters
    from validation import validate_tool_parameters, format_validation_error
    is_valid, error_details = validate_tool_parameters(tool_name, params)
    
    if not is_valid:
        return {
            "status": "error",
            "error": error_details
        }

    # Map tool names to methods
    tool_handlers = {
        "list_projects": lambda: mcp_api.list_projects(),
        "add_project": lambda: mcp_api.add_project(
            name=params.get("name"),
            source=params.get("source"),
            branch=params.get("branch")
        ),
        "analyze_dependencies": lambda: mcp_api.analyze_dependencies(
            project_id=params.get("project_id"),
            options=params.get("options")
        ),
        "get_dependency_graph": lambda: mcp_api.get_dependency_graph(
            project_id=params.get("project_id"),
            format=params.get("format", "json")
        ),
        "find_orphaned_files": lambda: mcp_api.find_orphaned_files(
            project_id=params.get("project_id"),
            exclude_patterns=params.get("exclude_patterns")
        ),
        "check_circular_dependencies": lambda: mcp_api.check_circular_dependencies(
            project_id=params.get("project_id"),
            module=params.get("module")
        )
    }
    
    handler = tool_handlers.get(tool_name)
    if handler:
        return handler()
    else:
        return {
            "status": "error",
            "error": {
                "code": "unknown_tool",
                "message": f"Unknown tool: {tool_name}",
                "details": {"available_tools": list(tool_handlers.keys())}
            }
        }

def handle_mcp_resource(resource_uri: str) -> Dict[str, Any]:
    """Handle an MCP resource request"""
    # Validate resource URI
    from validation import validate_resource_uri
    is_valid, error_details = validate_resource_uri(resource_uri)
    
    if not is_valid:
        return {
            "status": "error",
            "error": error_details
        }
    
    return mcp_api.handle_resource(resource_uri) 