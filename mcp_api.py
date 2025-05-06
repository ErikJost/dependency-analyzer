#!/usr/bin/env python3
"""
MCP API for Dependency Analyzer

This module implements the Model Context Protocol (MCP) API for the dependency analyzer,
allowing AI agents to interact with the code dependency data.
"""

import os
import json
import subprocess
import time
import shutil
import re
from urllib.parse import unquote
from typing import Dict, List, Any, Optional, Union, Callable

# Import streaming support
from streaming import execute_streaming_operation, streaming_manager

# Constants for project and analysis directories
PROJECTS_DIR = os.environ.get("PROJECTS_DIR", os.path.join(os.getcwd(), "projects"))
ANALYSIS_DIR = os.environ.get("ANALYSIS_DIR", os.path.join(os.getcwd(), "analysis"))
HOST_MOUNT_POINT = os.environ.get("HOST_MOUNT_POINT", "/host")

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
        
        # Check each subdirectory in the projects directory for internal projects
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
                        "created_at": None,
                        "is_external": False
                    }
        
        # Load external projects from registry
        registry_path = os.path.join(ANALYSIS_DIR, "external_projects_registry.json")
        if os.path.exists(registry_path):
            try:
                with open(registry_path, 'r') as f:
                    external_projects = json.load(f)
                    # Add external projects to the projects dictionary
                    for project_id, metadata in external_projects.items():
                        # Verify that the external path still exists
                        if os.path.exists(metadata["path"]):
                            projects[project_id] = metadata
                        else:
                            print(f"Warning: External project path no longer exists: {metadata['path']}")
            except Exception as e:
                print(f"Error loading external projects registry: {e}")
        
        return projects

    def _save_project_metadata(self, project_id: str, metadata: Dict[str, Any]) -> None:
        """Save project metadata to the appropriate location"""
        is_external = metadata.get("is_external", False)
        
        if is_external:
            # For external projects, update the registry
            registry_path = os.path.join(ANALYSIS_DIR, "external_projects_registry.json")
            external_projects = {}
            
            # Load existing registry if it exists
            if os.path.exists(registry_path):
                try:
                    with open(registry_path, 'r') as f:
                        external_projects = json.load(f)
                except Exception as e:
                    print(f"Error loading external projects registry: {e}")
            
            # Update the registry with this project
            external_projects[project_id] = metadata
            
            # Save the updated registry
            with open(registry_path, 'w') as f:
                json.dump(external_projects, f, indent=2)
        else:
            # For internal projects, save metadata in the project directory
            project_dir = os.path.join(PROJECTS_DIR, project_id)
            os.makedirs(project_dir, exist_ok=True)
            
            metadata_path = os.path.join(project_dir, ".project-metadata.json")
            with open(metadata_path, 'w') as f:
                json.dump(metadata, f, indent=2)

    def _get_analysis_path(self, project_id: str) -> str:
        """Get the path to the analysis results for a project"""
        return os.path.join(ANALYSIS_DIR, project_id)
        
    def _convert_host_path_to_container_path(self, host_path: str) -> str:
        """
        Convert a host filesystem path to a container-accessible path
        
        This function maps paths from the host OS to their location in the container
        using the mounted directories.
        """
        # For paths that already exist in the container directly, return as-is
        if os.path.exists(host_path):
            return host_path
            
        # Check if HOST_MOUNT_POINT is available
        if not os.path.exists(HOST_MOUNT_POINT):
            raise ValueError(f"Host mount point {HOST_MOUNT_POINT} is not available")
            
        # Convert absolute paths from host to container paths
        # For example: /Users/name/projects -> /host/projects
        
        # Get the host's OS type (e.g., macOS paths vs. Linux paths)
        # Generally, we expect paths like these:
        # - macOS/Linux: /Users/name/path or /home/name/path
        # - Windows: C:\Users\name\path or /c/Users/name/path (in WSL/Git Bash)
        
        # Convert Windows-style paths if needed
        if re.match(r'^[A-Za-z]:\\', host_path):
            # Windows drive letter path (C:\path\to\dir)
            drive_letter = host_path[0].lower()
            path_segments = host_path[2:].replace('\\', '/').split('/')
            host_path = f"/{drive_letter}/{'/'.join(path_segments)}"
        
        # Get just the relative part after the mount
        if not HOST_MOUNT_POINT.endswith('/'):
            host_mount_with_slash = HOST_MOUNT_POINT + '/'
        else:
            host_mount_with_slash = HOST_MOUNT_POINT
            
        container_path = os.path.join(host_mount_with_slash, os.path.basename(host_path))
        
        # Check if the converted path exists
        if not os.path.exists(container_path):
            # If the direct mapping doesn't work, try looking for a partial match
            # This handles cases where the host path doesn't exactly match the container path
            for root, dirs, _ in os.walk(HOST_MOUNT_POINT):
                for dir_name in dirs:
                    if host_path.endswith(dir_name):
                        potential_path = os.path.join(root, dir_name)
                        if os.path.exists(potential_path):
                            return potential_path
            
            # If we can't find a matching path, use the default mapping
            # and let the caller handle any access issues
            return container_path
            
        return container_path

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
        
        # Determine if the source is a repository or a local path
        is_repository = source.startswith("http://") or source.startswith("https://") or source.startswith("git@")
        
        # Check if it's a local path
        host_path_exists = False
        original_source = source
        
        try:
            # For local paths, we need to convert host paths to container paths
            if not is_repository:
                # Try to convert the path and check if it exists
                try:
                    source = self._convert_host_path_to_container_path(source)
                    host_path_exists = os.path.exists(source) and os.path.isdir(source)
                except Exception as e:
                    return {
                        "status": "error",
                        "error": {
                            "code": "path_conversion_error",
                            "message": f"Failed to convert host path: {str(e)}",
                            "details": {"source": original_source}
                        }
                    }
        
            is_local_path = host_path_exists
            is_external = is_local_path
            
            if is_repository:
                # For repositories, clone into our projects directory
                project_dir = os.path.join(PROJECTS_DIR, project_id)
                os.makedirs(project_dir, exist_ok=True)
                
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
            elif is_local_path:
                # For local paths, simply register the external directory
                project_dir = source
                
                # Verify the directory is accessible
                if not os.access(project_dir, os.R_OK):
                    return {
                        "status": "error",
                        "error": {
                            "code": "directory_access_error",
                            "message": "Cannot access the specified directory",
                            "details": {"directory": project_dir, "original_path": original_source}
                        }
                    }
            else:
                return {
                    "status": "error",
                    "error": {
                        "code": "invalid_source",
                        "message": "Source is not a valid URL or path",
                        "details": {"source": original_source, "converted_path": source}
                    }
                }
            
            # Create analysis directory for the project
            analysis_dir = self._get_analysis_path(project_id)
            os.makedirs(analysis_dir, exist_ok=True)
            
            # Create metadata
            import datetime
            metadata = {
                "id": project_id,
                "name": name,
                "source": original_source,  # Store the original source for reference
                "container_path": project_dir,  # The path used inside the container
                "branch": branch,
                "path": project_dir,
                "is_external": is_external,
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
        except Exception as e:
            return {
                "status": "error",
                "error": {
                    "code": "add_project_failed",
                    "message": f"Failed to add project: {str(e)}",
                    "details": {"source": original_source}
                }
            }

    # MCP Tool: analyze_dependencies
    def analyze_dependencies(self, project_id: str, options: Optional[Dict[str, Any]] = None, use_streaming: bool = False) -> Dict[str, Any]:
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
        
        # If streaming is requested, use the streaming operation
        if use_streaming:
            # Start a streaming operation
            params = {
                "project_id": project_id,
                "options": options
            }
            
            operation = execute_streaming_operation(
                task_func=self._analyze_dependencies_task,
                params=params
            )
            
            # Return the operation details
            return {
                "status": "accepted",
                "data": {
                    "operation_id": operation.operation_id,
                    "status": operation.status,
                    "correlation_id": operation.correlation_id
                },
                "metadata": {
                    "streaming": True,
                    "started_at": operation.start_time
                }
            }
        
        # Non-streaming version
        project = self.projects[project_id]
        project_dir = project["path"]
        
        # Verify the directory exists and is accessible
        if not os.path.exists(project_dir):
            return {
                "status": "error",
                "error": {
                    "code": "directory_not_found",
                    "message": f"Project directory does not exist: {project_dir}",
                    "details": {"project_id": project_id, "path": project_dir}
                }
            }
        
        if not os.access(project_dir, os.R_OK):
            return {
                "status": "error",
                "error": {
                    "code": "directory_access_error",
                    "message": f"Cannot access project directory: {project_dir}",
                    "details": {"project_id": project_id, "path": project_dir}
                }
            }
        
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
            
            # Copy all generated analysis files to the analysis directory
            source_analysis_dir = os.path.join(project_dir, "docs", "dependency-analysis")
            if os.path.exists(source_analysis_dir):
                # Copy all files from the source analysis directory to the destination
                for filename in os.listdir(source_analysis_dir):
                    source_file = os.path.join(source_analysis_dir, filename)
                    if os.path.isfile(source_file):
                        shutil.copy2(source_file, os.path.join(analysis_dir, filename))
            
            import datetime
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
    
    def _analyze_dependencies_task(self, operation, project_id: str, options: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Task function for analyzing dependencies with progress updates"""
        project = self.projects[project_id]
        project_dir = project["path"]
        
        # Verify the directory exists and is accessible
        if not os.path.exists(project_dir):
            operation.add_message(f"Project directory does not exist: {project_dir}", "error")
            raise FileNotFoundError(f"Project directory does not exist: {project_dir}")
        
        if not os.access(project_dir, os.R_OK):
            operation.add_message(f"Cannot access project directory: {project_dir}", "error")
            raise PermissionError(f"Cannot access project directory: {project_dir}")
        
        # Create analysis directory
        analysis_dir = self._get_analysis_path(project_id)
        os.makedirs(analysis_dir, exist_ok=True)
        
        # Set default options
        if options is None:
            options = {}
        
        try:
            # Update progress
            operation.update_progress(0.1, "Preparing dependency analysis")
            
            # Count files to analyze (for progress estimation)
            file_count = 0
            for root, dirs, files in os.walk(project_dir):
                # Skip node_modules and other common excludes
                if any(exclude in root for exclude in ["node_modules", ".git", "dist", "build"]):
                    continue
                
                # Count relevant files
                file_count += sum(1 for f in files if f.endswith(('.js', '.jsx', '.ts', '.tsx')))
            
            operation.update_progress(0.2, f"Found {file_count} files to analyze")
            
            # Prepare command - note we're running analysis directly on the project directory
            script_path = os.path.join(os.getcwd(), "scripts", "enhanced-dependency-analysis.cjs")
            cmd = ["node", script_path, f"--root-dir={project_dir}"]
            
            # Add options
            if "exclude" in options:
                excludes = options["exclude"]
                if isinstance(excludes, list):
                    cmd.append(f"--exclude={','.join(excludes)}")
            
            # Run analysis in chunks to provide progress updates
            operation.update_progress(0.3, "Starting dependency analysis")
            
            # Start the process
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1  # Line buffered
            )
            
            stdout_lines = []
            stderr_lines = []
            
            # Track progress through output
            progress = 0.3
            progress_step = 0.5 / (file_count if file_count > 0 else 100)
            files_processed = 0
            
            # Process output
            while True:
                # Check for process completion
                if process.poll() is not None:
                    break
                
                # Read available stdout
                line = process.stdout.readline()
                if line:
                    stdout_lines.append(line.strip())
                    
                    # Parse the line to update progress
                    if "Analyzing file:" in line:
                        files_processed += 1
                        if files_processed % 10 == 0:  # Update every 10 files
                            progress = min(0.8, 0.3 + (files_processed * progress_step))
                            operation.update_progress(
                                progress, 
                                f"Analyzed {files_processed}/{file_count} files"
                            )
                
                # Read available stderr
                err_line = process.stderr.readline()
                if err_line:
                    stderr_lines.append(err_line.strip())
                    operation.add_message(f"Error: {err_line.strip()}", "error")
                
                # Avoid CPU spin
                time.sleep(0.1)
            
            # Get any remaining output
            remaining_stdout, remaining_stderr = process.communicate()
            if remaining_stdout:
                stdout_lines.extend(remaining_stdout.splitlines())
            if remaining_stderr:
                stderr_lines.extend(remaining_stderr.splitlines())
                for line in remaining_stderr.splitlines():
                    operation.add_message(f"Error: {line}", "error")
            
            # Check result
            if process.returncode != 0:
                raise subprocess.CalledProcessError(
                    process.returncode, cmd, 
                    output="\n".join(stdout_lines), 
                    stderr="\n".join(stderr_lines)
                )
            
            operation.update_progress(0.9, "Analysis complete, saving results")
            
            # Copy all generated analysis files to our central analysis directory
            source_analysis_dir = os.path.join(project_dir, "docs", "dependency-analysis")
            if os.path.exists(source_analysis_dir):
                # Copy all files from the source analysis directory to the destination
                for filename in os.listdir(source_analysis_dir):
                    source_file = os.path.join(source_analysis_dir, filename)
                    if os.path.isfile(source_file):
                        shutil.copy2(source_file, os.path.join(analysis_dir, filename))
                operation.add_message("Copied analysis files to central analysis directory", "info")
            
            import datetime
            # Return the final result
            result = {
                "project_id": project_id,
                "output": stdout_lines,
                "analysis_path": analysis_dir,
                "files_processed": files_processed,
                "total_files": file_count,
                "timestamp": datetime.datetime.now().isoformat()
            }
            
            operation.update_progress(1.0, "Dependency analysis completed successfully")
            return result
            
        except subprocess.CalledProcessError as e:
            operation.add_message(f"Analysis failed: {e}", "error")
            raise
        except Exception as e:
            operation.add_message(f"Unexpected error: {e}", "error")
            raise

    # MCP Tool: get_operation_status
    def get_operation_status(self, operation_id: str) -> Dict[str, Any]:
        """Get the status of a streaming operation"""
        operation = streaming_manager.get_operation(operation_id)
        
        if not operation:
            return {
                "status": "error",
                "error": {
                    "code": "operation_not_found",
                    "message": f"Operation '{operation_id}' not found",
                    "details": {"operation_id": operation_id}
                }
            }
        
        # Get the operation status
        status = operation.get_status()
        
        # Return as MCP response
        return {
            "status": "success",
            "data": status
        }
    
    # MCP Tool: cancel_operation
    def cancel_operation(self, operation_id: str) -> Dict[str, Any]:
        """Cancel a streaming operation"""
        result = streaming_manager.cancel_operation(operation_id)
        
        if result:
            return {
                "status": "success",
                "data": {
                    "operation_id": operation_id,
                    "cancelled": True
                }
            }
        else:
            return {
                "status": "error",
                "error": {
                    "code": "cancel_failed",
                    "message": f"Failed to cancel operation '{operation_id}'",
                    "details": {"operation_id": operation_id}
                }
            }
    
    # MCP Tool: list_operations
    def list_operations(self) -> Dict[str, Any]:
        """List all streaming operations"""
        operations = streaming_manager.get_all_operations()
        
        return {
            "status": "success",
            "data": {
                "operations": operations
            },
            "metadata": {
                "count": len(operations)
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

    # Create API instance
    api = mcp_api
    
    # Map tool names to methods
    tool_handlers = {
        "list_projects": lambda: api.list_projects(),
        "add_project": lambda: api.add_project(
            name=params.get("name"),
            source=params.get("source"),
            branch=params.get("branch")
        ),
        "analyze_dependencies": lambda: api.analyze_dependencies(
            project_id=params.get("project_id"),
            options=params.get("options"),
            use_streaming=params.get("streaming", False)
        ),
        "get_dependency_graph": lambda: api.get_dependency_graph(
            project_id=params.get("project_id"),
            format=params.get("format", "json")
        ),
        "find_orphaned_files": lambda: api.find_orphaned_files(
            project_id=params.get("project_id"),
            exclude_patterns=params.get("exclude_patterns")
        ),
        "check_circular_dependencies": lambda: api.check_circular_dependencies(
            project_id=params.get("project_id"),
            module=params.get("module")
        ),
        "get_operation_status": lambda: api.get_operation_status(
            operation_id=params.get("operation_id")
        ),
        "cancel_operation": lambda: api.cancel_operation(
            operation_id=params.get("operation_id")
        ),
        "list_operations": lambda: api.list_operations()
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