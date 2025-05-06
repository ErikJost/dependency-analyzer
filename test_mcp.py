import subprocess
import json

# Prepare the two requests
initialize = {
    "jsonrpc": "2.0",
    "id": "init1",
    "method": "initialize",
    "params": {
        "protocolVersion": "1.0.0",
        "capabilities": {},
        "clientInfo": {"name": "TestClient", "version": "0.1"}
    }
}
list_projects = {
    "jsonrpc": "2.0",
    "id": "call1",
    "method": "tools/call",
    "params": {
        "name": "list_projects",
        "arguments": {}
    }
}

# Start the Docker container
proc = subprocess.Popen(
    ["docker", "run", "-i", "--rm", "mcp/sdk-minimal"],
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True
)

# Send both requests (newline-delimited)
proc.stdin.write(json.dumps(initialize) + "\n")
proc.stdin.write(json.dumps(list_projects) + "\n")
proc.stdin.flush()

# Read and print responses
try:
    for _ in range(2):
        print(proc.stdout.readline().strip())
finally:
    proc.stdin.close()
    proc.terminate() 