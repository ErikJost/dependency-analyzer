from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Dependency Analyzer")

projects = [
    {"id": "project1", "name": "Sample Project 1", "path": "/path/to/sample1"},
    {"id": "project2", "name": "Sample Project 2", "path": "/path/to/sample2"},
]

analysis_results = {}

@mcp.tool()
def list_projects() -> list:
    return projects

@mcp.tool()
def add_project(name: str, path: str) -> dict:
    new_id = f"project{len(projects)+1}"
    project = {"id": new_id, "name": name, "path": path}
    projects.append(project)
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

if __name__ == "__main__":
    mcp.run() 