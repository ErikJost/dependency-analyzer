from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Dependency Analyzer")

@mcp.tool()
def list_projects() -> list:
    """Lists all projects available for analysis"""
    return [
        {"id": "project1", "name": "Sample Project 1", "path": "/path/to/sample1"},
        {"id": "project2", "name": "Sample Project 2", "path": "/path/to/sample2"},
    ]

if __name__ == "__main__":
    mcp.run() 