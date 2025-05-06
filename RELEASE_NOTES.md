# Release Notes: Dependency Analyzer MCP Server v2.0.0

## Major Update: AI-Powered Code Analysis with MCP

We're excited to announce version 2.0.0 of the Dependency Analyzer, now available as a Model Context Protocol (MCP) server! This release transforms the tool into an AI-first code analysis platform designed specifically for AI agents and code editors like Cursor.

### What's New

#### MCP API Implementation
- **Standardized MCP Interface**: API compatible with AI agents like Claude and GPT
- **Resource Format**: URI-based resource access following MCP conventions
- **Tool Endpoints**: Rich set of code analysis tools accessible through the MCP protocol
- **Cursor Integration**: Designed to work seamlessly with Cursor editor

#### Enhanced Code Analysis
- **Multi-Project Support**: Analyze and navigate between multiple codebases
- **Component-Level Analysis**: Fine-grained dependency tracking for components
- **Improved Visualization**: Better visualizations of code relationships
- **Contextual Responses**: Results formatted for optimal AI agent understanding

#### Docker & Containerization
- **Dockerized Application**: Easy deployment with Docker and Docker Compose
- **Volume Management**: Persistent storage for projects and analysis results
- **Environment Configuration**: Flexible configuration through environment variables

### AI Agent Features

The MCP server provides AI agents with powerful capabilities:

- **Contextual Code Understanding**: Gain insights into code structure and relationships
- **Impact Analysis**: Understand how changes might affect different parts of the codebase
- **Dependency Mapping**: Trace imports and exports throughout the codebase
- **Architectural Insights**: Visualize high-level component relationships

### Breaking Changes
- Configuration format has changed to support the MCP protocol
- API endpoints follow MCP conventions rather than traditional REST patterns
- Tool names and parameters have been standardized for AI agent compatibility

### Upgrade Guide

#### From v1.x to v2.0.0 (MCP Server)
1. Pull the latest code:
   ```bash
   git pull origin main
   ```

2. Build and start the Docker container:
   ```bash
   docker build --no-cache -t mcp/sdk-minimal -f Dockerfile.sdk_minimal .
   docker run -d --name DependencyMCP -v /Users/erikjost/data:/data mcp/sdk-minimal
   ```

3. Access the MCP server at http://localhost:8000

4. For AI agent integration, direct your agent to use the MCP protocol endpoints

### Future Plans
- Enhanced AI agent capabilities through specialized embeddings
- Training data generation for better code understanding
- Team collaboration features
- Support for additional programming languages

### Contributors
- Erik Jost (@ErikJost)

### Feedback and Issues
We welcome your feedback and bug reports! Please submit issues on our [GitHub repository](https://github.com/ErikJost/dependency-analyzer/issues).

## v1.0.0 (2024-05-06)

### Major Changes
- **Docker image now based on python:3.13-slim** for improved security and up-to-date dependencies.
- **Persistent data strategy updated:**
  - Use a host path volume mapping (e.g., `/Users/erikjost/data:/data`) for all project and analysis data.
  - This ensures data is never lost, even if the container is removed or the image is updated.
- **Cursor MCP integration:**
  - Recommended configuration now uses `docker run` with the image name and host path volume mapping.
  - Removed use of `docker exec` and container-based communication for Cursor.
  - No `env` block is required in the MCP config.
- **Documentation updated** to reflect these best practices and provide clear setup instructions.

### Upgrade Instructions
- Rebuild your Docker image:
  ```bash
  docker build --no-cache -t mcp/sdk-minimal -f Dockerfile.sdk_minimal .
  ```
- When running the container manually, use:
  ```bash
  docker run -d --name DependencyMCP -v /Users/erikjost/data:/data mcp/sdk-minimal
  ```
- For Cursor integration, update your `mcp.json`:
  ```json
  "dependencyAnalyzer": {
    "command": "docker",
    "args": [
      "run",
      "-i",
      "--rm",
      "-v",
      "/Users/erikjost/data:/data",
      "mcp/sdk-minimal"
    ]
  }
  ```

### Notes
- Using a host path for `/data` ensures your analysis results and project data persist across container and image changes.
- The MCP server is now fully compatible with Cursor's recommended integration pattern.
- See the README for more details and troubleshooting tips.
- Data volumes should NOT be attached during the Docker build step. Only mount persistent data at runtime when starting the container.
- This keeps the image portable and ensures persistent data is not baked into the image. 