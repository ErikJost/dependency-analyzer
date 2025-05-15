## Example Build and Run Commands (Updated)

To build the image:

```bash
docker build -t mcp/sdk-minimal:latest -f src/Dockerfile.sdk_minimal .
```

To run the container:

```bash
docker run -d --name DependencyMCP \
  -v /Users/erikjost/data:/data \
  -v /Users/erikjost:/Users/erikjost \
  -p 8000:8000 \
  mcp/sdk-minimal:latest
``` 