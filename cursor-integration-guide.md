# Cursor Integration Guide - Dependency Analyzer

This guide explains how to properly integrate the Dependency Analyzer with Cursor using the [Model Context Protocol (MCP)](https://modelcontextprotocol.io/).

## MCP Architecture Overview

MCP follows a client-server architecture where:
- **Hosts** are LLM applications (like Cursor) that initiate connections
- **Clients** maintain connections with servers, inside the host application
- **Servers** provide context, tools, and resources to clients

Our dependency analyzer acts as an MCP server that Cursor connects to for analyzing code dependencies.

## JSON-RPC 2.0 Requirements

MCP uses JSON-RPC 2.0 as its message format. All messages must adhere to these requirements:

1. Every message must include the `jsonrpc: "2.0"` field
2. All responses must include the same `id` field as the request
3. Responses must contain either a `result` object or an `error` object
4. **Important**: Only send responses to messages from Cursor - never send unsolicited messages
5. **Protocol Version**: The initialization response **must** include the `protocolVersion` field (e.g., "0.1.0")

### Message Types

The MCP protocol defines these main types of messages:

1. **Requests** - Expect a response:
   ```json
   {
     "jsonrpc": "2.0",
     "id": "request-id",
     "method": "method-name",
     "params": { ... }
   }
   ```

2. **Results** - Successful responses:
   ```json
   {
     "jsonrpc": "2.0",
     "id": "request-id",
     "result": { ... }
   }
   ```

3. **Errors** - Error responses:
   ```json
   {
     "jsonrpc": "2.0",
     "id": "request-id",
     "error": {
       "code": -32600,
       "message": "Error message"
     }
   }
   ```

## Connection Lifecycle

### 1. Initialization

1. Cursor sends `initialize` request with capabilities
2. Our server responds with its capabilities
3. Normal message exchange begins

Example initialization request:
```json
{
  "jsonrpc": "2.0",
  "id": "request-123",
  "method": "initialize"
}
```

Example initialization response:
```json
{
  "jsonrpc": "2.0",
  "id": "request-123",
  "result": {
    "protocolVersion": "0.1.0",
    "serverInfo": {
      "name": "Dependency Analyzer",
      "version": "1.0.0"
    },
    "capabilities": {
      "functions": [
        {
          "name": "analyze_dependencies",
          "description": "Analyzes dependencies in a project",
          "parameters": {
            "type": "object",
            "properties": {},
            "required": []
          }
        }
      ]
    }
  }
}
```

### 2. Message Exchange

After initialization, Cursor can:
- Send function requests using the `mcp/invokeFunction` method
- Receive responses with results or errors

## Current Implementation (sdk_mcp_server.py)

Our current implementation uses a robust JSON-RPC 2.0 compliant server with fallback capabilities if the MCP SDK is not available. It provides:

- Strict adherence to JSON-RPC 2.0 format
- Proper error handling with standard error codes
- Support for multiple dependency analysis tools
- Sample data for testing and demonstration

The server implements the following tools:
1. `list_projects` - Lists available projects for analysis
2. `add_project` - Adds a new project for analysis
3. `analyze_dependencies` - Performs dependency analysis on a project
4. `get_dependency_graph` - Returns the dependency graph for a project
5. `find_orphaned_files` - Identifies files not imported by others
6. `check_circular_dependencies` - Detects circular dependencies

## Setting Up MCP Integration

### 1. Build the Docker Image

To build the MCP server Docker image:

```bash
docker build --no-cache -t mcp/sdk-minimal -f Dockerfile.sdk_minimal .
```

### 2. Cursor Configuration

Create or update `~/.cursor/mcp.json` with:
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
      ],
      "env": {}
    }
  }
}
```

### 3. Testing the Server

For testing independently, use:

```bash
echo '{"jsonrpc":"2.0","id":"test","method":"initialize"}' | docker run -i --rm mcp/sdk-minimal
```

## Error Handling

MCP defines standard error codes:

| Code     | Meaning                    |
|----------|----------------------------|
| -32700   | Parse error                |
| -32600   | Invalid request            |
| -32601   | Method not found           |
| -32602   | Invalid parameters         |
| -32603   | Internal error             |
| -32000+  | Custom application errors  |

Common error messages in Cursor:
1. **"No server info found"** - The server's initialization response format is incorrect
2. **"Client closed"** - The communication was closed unexpectedly
3. **"Invalid type"** - Response fields don't match the expected JSON-RPC 2.0 schema
4. **"Unknown message ID"** - The server sent a response that doesn't correspond to any request

## Troubleshooting

If Cursor doesn't display the tools:

1. Check Docker container is running properly
2. Verify the server is sending correct JSON-RPC 2.0 responses
3. Look for errors in stderr output: `docker logs $(docker ps -q --filter ancestor=mcp/sdk-minimal)`
4. Ensure the Docker image has the correct permissions
5. Make sure the server is responding properly to the initialize request

## Best Practices

1. Follow strict JSON-RPC 2.0 format for all communication
2. Never send unsolicited messages to Cursor
3. Add proper error handling with appropriate error codes
4. Ensure response IDs match request IDs exactly
5. Keep responses reasonably sized (under 10MB) to prevent memory issues
6. Use the most minimal configuration possible in `mcp.json`
7. Validate all incoming messages thoroughly
8. Test thoroughly before integrating with Cursor

## Resources

- [Official MCP Documentation](https://modelcontextprotocol.io/docs/concepts/architecture)
- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk)
- [JSON-RPC 2.0 Specification](https://www.jsonrpc.org/specification) 