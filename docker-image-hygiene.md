# Docker Image Hygiene Rule (Updated)

When building a new Docker image for the dependency analyzer MCP server, always remove any old containers that use the previous image before starting a new one. This prevents clutter and resource waste from having multiple containers and images running simultaneously.

## Steps

1. **Stop and remove the old container before running a new one:**
   - Use the following commands before starting a new container:
     ```bash
     docker stop DependencyMCP || true
     docker rm DependencyMCP || true
     ```
   - This ensures that the container named `DependencyMCP` is not left running or in a stopped state.

2. **Build the new image:**
   - **Do NOT attach any data volumes during the build step.**
   - Example:
     ```bash
     docker build --no-cache -t mcp/sdk-minimal -f Dockerfile.sdk_minimal .
     ```
   - The build step is for image creation only. Persistent data should not be included in the image.

3. **Start the new container with the updated image:**
   - **Attach the data volume and any other required mounts at runtime, not build time:**
     ```bash
     docker run -d --name DependencyMCP -v /Users/erikjost/data:/data mcp/sdk-minimal
     ```
   - This ensures persistent data is available to the running container, but not baked into the image.

## Rationale
- Keeps the Docker image clean and portable.
- Ensures persistent data is not included in the image, but is available at runtime.
- Follows best practices for Docker volume management.

## See Also
- [README.md](mdc:README.md) for persistent data and container management instructions.
- [RELEASE_NOTES.md](mdc:RELEASE_NOTES.md) for upgrade steps and best practices.
- Orphaned files are now moved to the `archived_orphan` folder in the project root. If a file with the same name exists, a dash and the next available number is appended (e.g., `file.md`, `file-1.md`, `file-2.md`). No files are deleted. 