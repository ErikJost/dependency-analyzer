import os
import json
import sys
import logging
import traceback
from mcp.server.fastmcp import FastMCP

DATA_PATH = "/data/projects.json"
LOG_PATH = "/data/mcp_debug.log"

# Create data directory if it doesn't exist
os.makedirs(os.path.dirname(DATA_PATH), exist_ok=True)

# Set up logging
logging.basicConfig(
    filename=LOG_PATH,
    level=logging.DEBUG,
    format="%(asctime)s %(levelname)s %(message)s"
)

def load_projects():
    print(f"Loading projects from {DATA_PATH}", file=sys.stderr)
    if os.path.exists(DATA_PATH):
        try:
            with open(DATA_PATH, "r") as f:
                projects = json.load(f)
                print(f"Loaded {len(projects)} projects from file", file=sys.stderr)
                return projects
        except Exception as e:
            print(f"Error loading projects: {str(e)}", file=sys.stderr)
            traceback.print_exc(file=sys.stderr)
    print("Using default projects", file=sys.stderr)
    return [
        {"id": "project1", "name": "Sample Project 1", "path": "/path/to/sample1"},
        {"id": "project2", "name": "Sample Project 2", "path": "/path/to/sample2"},
    ]

def save_projects(projects):
    print(f"Saving {len(projects)} projects to {DATA_PATH}", file=sys.stderr)
    os.makedirs(os.path.dirname(DATA_PATH), exist_ok=True)
    try:
        with open(DATA_PATH, "w") as f:
            json.dump(projects, f)
        print(f"Projects saved successfully to {DATA_PATH}", file=sys.stderr)
        # Verify the file exists after saving
        if os.path.exists(DATA_PATH):
            print(f"Verified: {DATA_PATH} exists with size {os.path.getsize(DATA_PATH)}", file=sys.stderr)
        else:
            print(f"Warning: {DATA_PATH} does not exist after save attempt", file=sys.stderr)
    except Exception as e:
        print(f"Error saving projects: {str(e)}", file=sys.stderr)
        traceback.print_exc(file=sys.stderr)

mcp = FastMCP("Dependency Analyzer")
projects = load_projects()

analysis_results = {}

@mcp.tool()
def list_projects() -> list:
    logging.debug(f"list_projects called, returning {len(projects)} projects")
    print(f"list_projects called, returning {len(projects)} projects", file=sys.stderr)
    return projects

@mcp.tool()
def add_project(name: str, path: str) -> dict:
    logging.debug(f"add_project called with name={name}, path={path}")
    print(f"add_project called with name={name}, path={path}", file=sys.stderr)
    new_id = f"project{len(projects)+1}"
    project = {"id": new_id, "name": name, "path": path}
    projects.append(project)
    logging.debug(f"Current projects: {projects}")
    print(f"Current projects after adding: {len(projects)} projects", file=sys.stderr)
    
    # Call save_projects and capture any errors
    try:
        save_projects(projects)
        logging.debug(f"Saved projects to {DATA_PATH}")
    except Exception as e:
        logging.error(f"Failed to save projects: {str(e)}")
        print(f"Failed to save projects: {str(e)}", file=sys.stderr)
    
    return project

@mcp.tool()
def analyze_dependencies(project_id: str) -> dict:
    # For now, return mock analysis results
    result = {
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
    analysis_results[project_id] = result
    return result

@mcp.tool()
def get_dependency_graph(project_id: str) -> dict:
    # Return the graph for the project if analyzed, else empty
    result = analysis_results.get(project_id)
    if result:
        return {"graph": result["graph"]}
    else:
        return {"graph": {"nodes": [], "edges": []}}

@mcp.tool()
def find_orphaned_files(project_id: str) -> dict:
    # Return mock orphaned files
    return {
        "orphaned_files": [
            {"path": "unused.js", "type": "JavaScript"},
            {"path": "old_utils.js", "type": "JavaScript"}
        ]
    }

@mcp.tool()
def check_circular_dependencies(project_id: str) -> dict:
    # Return mock circular dependencies
    return {
        "circular_dependencies": [
            {
                "cycle": ["moduleA.js", "moduleB.js", "moduleC.js", "moduleA.js"],
                "severity": "high"
            }
        ]
    }

# Check /data volume is accessible
print(f"Starting server...", file=sys.stderr)
print(f"Checking /data directory:", file=sys.stderr)
print(f"  Exists: {os.path.exists('/data')}", file=sys.stderr)
print(f"  Writable: {os.access('/data', os.W_OK)}", file=sys.stderr)
print(f"  Contents: {os.listdir('/data')}", file=sys.stderr)

if __name__ == "__main__":
    mcp.run() 