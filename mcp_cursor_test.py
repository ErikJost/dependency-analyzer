#!/usr/bin/env python3
"""
MCP Test Client for Cursor Integration

This script demonstrates how to use the Dependency Analyzer MCP API
from Cursor or any other client that supports MCP.
"""

import argparse
import json
import os
import requests
import sys
from typing import Dict, Any, Optional, List

# Default MCP server URL
MCP_SERVER_URL = "http://localhost:8000"

class MCPClient:
    """Simple client for interacting with the MCP server"""
    
    def __init__(self, server_url: str):
        """Initialize the client with the server URL"""
        self.server_url = server_url
        self.tools_endpoint = f"{server_url}/api/tools"
        self.resource_endpoint = f"{server_url}/api/resource"
        self.correlation_id = None

    def call_tool(self, tool_name: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Call an MCP tool with the given parameters"""
        url = f"{self.tools_endpoint}/{tool_name}"
        
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
        # Add correlation ID for request tracing if available
        if self.correlation_id:
            headers["X-Correlation-ID"] = self.correlation_id
        
        # Make the API request
        response = requests.post(url, json=params, headers=headers)
        
        # Save the correlation ID for subsequent requests
        if "X-Correlation-ID" in response.headers:
            self.correlation_id = response.headers["X-Correlation-ID"]
        
        # Return the parsed JSON response
        try:
            return response.json()
        except ValueError:
            return {
                "status": "error",
                "error": {
                    "code": "invalid_response",
                    "message": "Server returned an invalid response",
                    "details": {
                        "status_code": response.status_code,
                        "content": response.text
                    }
                }
            }
    
    def get_resource(self, resource_uri: str) -> Dict[str, Any]:
        """Get a resource from the MCP server"""
        url = f"{self.resource_endpoint}/{resource_uri}"
        
        headers = {
            "Accept": "application/json"
        }
        
        # Add correlation ID for request tracing if available
        if self.correlation_id:
            headers["X-Correlation-ID"] = self.correlation_id
        
        # Make the API request
        response = requests.get(url, headers=headers)
        
        # Save the correlation ID for subsequent requests
        if "X-Correlation-ID" in response.headers:
            self.correlation_id = response.headers["X-Correlation-ID"]
        
        # Return the parsed JSON response
        try:
            return response.json()
        except ValueError:
            return {
                "status": "error",
                "error": {
                    "code": "invalid_response",
                    "message": "Server returned an invalid response",
                    "details": {
                        "status_code": response.status_code,
                        "content": response.text
                    }
                }
            }

def print_json(data: Dict[str, Any]) -> None:
    """Print JSON data in a human-readable format"""
    print(json.dumps(data, indent=2))

def main():
    """Main function to run the MCP client test"""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Test the Dependency Analyzer MCP API")
    parser.add_argument("--server", default=MCP_SERVER_URL, help="MCP server URL")
    parser.add_argument("--project-dir", help="Project directory to analyze")
    parser.add_argument("--project-id", help="ID of an existing project to analyze")
    parser.add_argument("--list-projects", action="store_true", help="List all projects")
    parser.add_argument("--analyze", action="store_true", help="Analyze dependencies for the specified project")
    parser.add_argument("--graph", action="store_true", help="Get dependency graph for the specified project")
    parser.add_argument("--orphaned", action="store_true", help="Find orphaned files in the specified project")
    
    args = parser.parse_args()
    
    # Initialize the MCP client
    client = MCPClient(args.server)
    
    # List projects if requested
    if args.list_projects:
        print("Listing projects...")
        response = client.call_tool("list_projects", {})
        print_json(response)
        
        if response.get("status") == "success":
            projects = response.get("data", {}).get("projects", [])
            print(f"\nFound {len(projects)} projects:")
            for project in projects:
                print(f"  - {project['name']} (ID: {project['id']})")
    
    # Add a new project if requested
    if args.project_dir and not args.project_id:
        project_name = os.path.basename(args.project_dir)
        print(f"Adding project '{project_name}' from {args.project_dir}...")
        
        response = client.call_tool("add_project", {
            "name": project_name,
            "source": args.project_dir
        })
        print_json(response)
        
        if response.get("status") == "success":
            project = response.get("data", {}).get("project", {})
            project_id = project.get("id")
            print(f"\nAdded project '{project_name}' with ID: {project_id}")
            
            # Use this project_id for subsequent operations
            args.project_id = project_id
    
    # Ensure we have a project ID for subsequent operations
    if not args.project_id and (args.analyze or args.graph or args.orphaned):
        print("Error: Please specify a project ID with --project-id or add a new project with --project-dir")
        sys.exit(1)
    
    # Analyze dependencies if requested
    if args.analyze and args.project_id:
        print(f"Analyzing dependencies for project {args.project_id}...")
        response = client.call_tool("analyze_dependencies", {
            "project_id": args.project_id
        })
        print_json(response)
        
        if response.get("status") == "success":
            print("\nAnalysis completed successfully")
    
    # Get dependency graph if requested
    if args.graph and args.project_id:
        print(f"Getting dependency graph for project {args.project_id}...")
        response = client.call_tool("get_dependency_graph", {
            "project_id": args.project_id
        })
        
        if response.get("status") == "success":
            graph = response.get("data", {}).get("graph", {})
            nodes = graph.get("nodes", [])
            links = graph.get("links", [])
            
            print(f"\nDependency Graph: {len(nodes)} nodes, {len(links)} links")
            print("\nNodes (sample):")
            for node in nodes[:5]:  # Show just the first 5 nodes
                print(f"  - {node.get('id')} (Group: {node.get('group')})")
            
            if len(nodes) > 5:
                print(f"  ... and {len(nodes) - 5} more")
            
            print("\nLinks (sample):")
            for link in links[:5]:  # Show just the first 5 links
                print(f"  - {link.get('source')} -> {link.get('target')}")
            
            if len(links) > 5:
                print(f"  ... and {len(links) - 5} more")
        else:
            print_json(response)
    
    # Find orphaned files if requested
    if args.orphaned and args.project_id:
        print(f"Finding orphaned files in project {args.project_id}...")
        response = client.call_tool("find_orphaned_files", {
            "project_id": args.project_id
        })
        
        if response.get("status") == "success":
            orphaned_files = response.get("data", {}).get("orphaned_files", [])
            print(f"\nFound {len(orphaned_files)} orphaned files:")
            for file in orphaned_files[:10]:  # Show just the first 10 files
                print(f"  - {file}")
            
            if len(orphaned_files) > 10:
                print(f"  ... and {len(orphaned_files) - 10} more")
        else:
            print_json(response)

if __name__ == "__main__":
    main() 