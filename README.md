# Dependency Analyzer MCP Server

A Model Context Protocol (MCP) server for analyzing and visualizing code dependencies in JavaScript and TypeScript projects. Designed for AI agents and Cursor to gain deeper understanding of codebases.

## Features

- **MCP API**: Standardized API for AI agents to access dependency information
- **Dependency Analysis**: Static code analysis to identify imports and exports
- **Multi-Project Support**: Analyze multiple projects simultaneously
- **Interactive Visualization**: Force-directed graph visualization of dependencies
- **Orphaned File Detection**: Identify unused files in the codebase
- **Docker Integration**: Easy deployment in containerized environments

## Installation

### Prerequisites

- Docker & Docker Compose (recommended)
- Alternatively: Node.js (v14+) and Python 3.6+

### Quick Start with Docker (Recommended)

```bash
# Clone the repository
git clone https://github.com/ErikJost/dependency-analyzer.git
cd dependency-analyzer

# Build and start with Docker Compose
docker-compose up -d
```

The MCP server will be available at http://localhost:8000

### Local Installation

If you prefer a local installation without Docker:

```bash
# Clone the repository
git clone https://github.com/ErikJost/dependency-analyzer.git
cd dependency-analyzer

# Install dependencies
pip install -r requirements.txt
npm install

# Start the server
python server.py
```

## MCP API Reference

The Dependency Analyzer MCP server provides a set of tools and resources for AI agents and Cursor to analyze code dependencies.

### MCP Tools

#### Dependency Analysis

- **analyze_dependencies**: Analyze dependencies for a project
  ```json
  {
    "project_id": "my-project",
    "options": {
      "exclude": ["node_modules", "dist"]
    }
  }
  ```

- **get_dependency_graph**: Retrieve the dependency graph
  ```json
  {
    "project_id": "my-project",
    "format": "json"
  }
  ```

- **find_orphaned_files**: Find files not imported anywhere
  ```json
  {
    "project_id": "my-project",
    "exclude_patterns": ["*.test.ts", "*.spec.ts"]
  }
  ```

#### Project Management

- **list_projects**: List all available projects
- **add_project**: Add a new project for analysis
  ```json
  {
    "name": "my-new-project",
    "source": "https://github.com/username/repo.git",
    "branch": "main"
  }
  ```

### MCP Resources

- **Project Structure**: `project://{project_id}/structure`
- **Dependency Graph**: `project://{project_id}/dependencies`
- **File Dependencies**: `project://{project_id}/file/{path}/dependencies`
- **Component Dependencies**: `project://{project_id}/component/{component_name}/dependencies`

## Usage with AI Agents

The Dependency Analyzer MCP server is designed to work with AI agents like GPT and Claude. AI agents can:

1. Query the dependency structure of your code
2. Find unused files or circular dependencies
3. Understand the relationships between components
4. Analyze the impact of potential code changes

Example prompts for AI agents:

- "Analyze the dependencies of the authentication module in my-project"
- "Find unused files in the components directory"
- "Show me the dependencies of the UserProfile component"
- "Identify circular dependencies in the utils directory"

## Docker Configuration

The Docker container can be configured through environment variables:

```yaml
environment:
  - PORT=8000
  - PROJECTS_DIR=/app/projects
  - ANALYSIS_DIR=/app/analysis
```

You can mount projects directly into the container:

```yaml
volumes:
  - ./my-project:/app/projects/my-project
```

## Analysis Tools

The Dependency Analyzer MCP server includes these core analysis scripts:

- **enhanced-dependency-analysis.cjs**: Main dependency analysis
- **check-dynamic-imports.cjs**: Detect dynamically imported modules
- **verify-route-components.cjs**: Verify route components
- **batch-archive-orphaned.cjs**: Manage orphaned files

## Visualizations

The server provides several visualization options:

- Interactive force-directed graph visualization
- Tabular dependency views
- Orphaned file reports
- Build dependency analysis

## Development

### Running Tests

```bash
npm test
```

### Building Docker Image

```bash
docker build -t dependency-analyzer-mcp .
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Inspired by [GitHub's MCP Server](https://github.com/github/github-mcp-server) for AI agent integration
- Built to enhance AI understanding of code structure

## MCP SDK Server (Working Implementation)

This project now includes a fully working Model Context Protocol (MCP) server using the official Python SDK. The server exposes all required tools for dependency analysis and is compatible with Cursor and other MCP clients.

### How to Build and Run

1. **Build the Docker image:**
   ```bash
   docker build -t mcp/sdk-minimal -f archive/Dockerfile.sdk_minimal .
   ```
2. **Run the server (for testing):**
   ```bash
   echo '{"jsonrpc":"2.0","id":"test","method":"initialize"}' | docker run -i --rm mcp/sdk-minimal
   ```
3. **Configure Cursor:**
   In your `~/.cursor/mcp.json`:
   ```json
   {
     "mcpServers": {
       "dependencyAnalyzer": {
         "command": "docker",
         "args": [
           "run",
           "-i",
           "--rm",
           "mcp/sdk-minimal"
         ]
       }
     }
   }
   ```

### Exposed Tools
- `list_projects`
- `add_project`
- `analyze_dependencies`
- `get_dependency_graph`
- `find_orphaned_files`
- `check_circular_dependencies`

All tools are implemented in `sdk_minimal_server.py` and return mock data by default. You can extend them to provide real analysis logic as needed.

---

## Next Steps

- **Replace mock logic** in each tool with real dependency analysis code.
- **Persist project and analysis data** (currently in-memory only).
- **Add error handling and validation** for tool arguments.
- **Expand test coverage** for all MCP tools.
- **Document API and tool usage** for other developers.
- **Integrate with CI/CD** to run dependency analysis automatically.
- **Contribute improvements** back to the MCP SDK or this repo as needed.

For questions or contributions, please open an issue or pull request.

## Running the MCP Server with Docker

1. **Build the Docker image (no data volumes attached at build time):**
   ```bash
   docker build --no-cache -t mcp/sdk-minimal -f Dockerfile.sdk_minimal .
   ```
   > **Note:** Do NOT attach any data volumes during the build step. The build step is for image creation only.

2. **Start the container with persistent data and project directories mounted (attach volumes at runtime):**
   ```bash
   docker run -d --name DependencyMCP -v /Users/erikjost/data:/data -v /Users/erikjost:/Users/erikjost -p 8000:8000 mcp/sdk-minimal
   ```
   > This ensures persistent data is available to the running container, but not baked into the image.

## Persistent Data and Project Access with Docker

To ensure your analysis data persists and your projects are accessible for validation, use multiple host path volume mappings when running the container:

```bash
# Example: Run the container with persistent data and full project access
# Replace /Users/erikjost/data and /Users/erikjost with your actual directories

docker run -d --name DependencyMCP \
  -v /Users/erikjost/data:/data \
  -v /Users/erikjost:/Users/erikjost \
  mcp/sdk-minimal
```

- `/Users/erikjost/data` is a directory on your host machine for persistent analysis data.
- `/Users/erikjost` is your user/project directory, making all your projects accessible inside the container.
- `/data` and `/Users/erikjost` are the corresponding paths inside the container.

## Cursor MCP Configuration (with multiple mounts)

For Cursor integration, configure your `mcp.json` as follows:

```json
"dependencyAnalyzer": {
  "command": "docker",
  "args": [
    "run",
    "-i",
    "--rm",
    "-v",
    "/Users/erikjost/data:/data",
    "-v",
    "/Users/erikjost:/Users/erikjost",
    "mcp/sdk-minimal"
  ]
}
```

- This will start a new container for each request, with both persistent data and project directories mounted.
- Adjust the paths as needed for your environment.

## Release Notes

See `RELEASE_NOTES.md` for a summary of recent changes and upgrade instructions.

## Orphaned File Archival

When archiving orphaned files, they are now moved to the `archived_orphan` folder in the project root. If a file with the same name already exists, a dash and the next available number is appended (e.g., `file.md`, `file-1.md`, `file-2.md`). No files are deleted. 