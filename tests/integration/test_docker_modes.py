#!/usr/bin/env python3
"""
Integration tests for Docker container modes.

This module tests the Docker container in both HTTP and stdio modes.
"""

import os
import json
import time
import pytest
import requests
import subprocess
from typing import Dict, Any, List

# Skip these tests when not in a Docker test environment
pytestmark = pytest.mark.skipif(
    not os.environ.get("DOCKER_TEST_ENABLED", "").lower() in ("true", "1", "yes"),
    reason="Docker tests are only run when DOCKER_TEST_ENABLED is set"
)

class TestDockerModes:
    """Tests for the Docker container in different modes"""

    def test_http_mode_container(self):
        """Test the Docker container in HTTP mode"""
        # Start the container in HTTP mode
        container_name = "dependency-analyzer-test-http"
        try:
            # Remove any existing container with the same name
            subprocess.run(
                ["docker", "rm", "-f", container_name],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False  # Don't fail if container doesn't exist
            )

            # Start the container in HTTP mode
            process = subprocess.Popen(
                [
                    "docker", "run", "--name", container_name, "-d",
                    "-p", "8000:8000",
                    "-e", "MCP_MODE=http",
                    "-e", "LOG_LEVEL=INFO",
                    "dependency-analyzer-mcp"
                ],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            stdout, stderr = process.communicate()
            assert process.returncode == 0, f"Failed to start container: {stderr.decode()}"

            # Wait for the container to start
            time.sleep(2)

            # Check container is running
            process = subprocess.run(
                ["docker", "ps", "--filter", f"name={container_name}", "--format", "{{.Status}}"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=True
            )
            status = process.stdout.decode().strip()
            assert "Up" in status, f"Container not running: {status}"

            # Test the HTTP API health endpoint
            response = requests.get("http://localhost:8000/api/health")
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "ok"
            assert "version" in data

            # Test a basic API endpoint
            response = requests.post(
                "http://localhost:8000/api/tools/list_projects",
                json={}
            )
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "success"
            assert "projects" in data

        finally:
            # Clean up: stop and remove the container
            subprocess.run(
                ["docker", "rm", "-f", container_name],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False  # Don't fail if cleanup fails
            )

    def test_stdio_mode_container(self):
        """Test the Docker container in stdio mode"""
        container_name = "dependency-analyzer-test-stdio"
        try:
            # Remove any existing container with the same name
            subprocess.run(
                ["docker", "rm", "-f", container_name],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False  # Don't fail if container doesn't exist
            )

            # Create a test request file
            test_requests = [
                # Handshake request
                json.dumps({
                    "jsonrpc": "2.0",
                    "method": "mcp.handshake",
                    "params": {
                        "version": "0.1.0",
                        "capabilities": ["tools"]
                    },
                    "id": "handshake-1"
                }),
                # List projects request
                json.dumps({
                    "jsonrpc": "2.0",
                    "method": "mcp.execute_tool",
                    "params": {
                        "tool": "list_projects",
                        "parameters": {}
                    },
                    "id": "list-projects-1"
                })
            ]
            
            # Run the container in stdio mode with the test requests
            process = subprocess.Popen(
                [
                    "docker", "run", "--name", container_name,
                    "-e", "MCP_MODE=stdio",
                    "-e", "LOG_LEVEL=INFO",
                    "dependency-analyzer-mcp"
                ],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True  # Use text mode for easier JSON handling
            )
            
            # Send requests and get responses
            responses = []
            for request in test_requests:
                process.stdin.write(request + "\n")
                process.stdin.flush()
                
                # Read the response line
                response_line = process.stdout.readline().strip()
                responses.append(json.loads(response_line))
            
            # Close stdin to signal end of input
            process.stdin.close()
            
            # Wait for the process to end
            returncode = process.wait(timeout=5)
            assert returncode == 0, f"Process failed with return code {returncode}"
            
            # Check the responses
            assert len(responses) == 2
            
            # Check handshake response
            handshake_response = responses[0]
            assert handshake_response["jsonrpc"] == "2.0"
            assert handshake_response["id"] == "handshake-1"
            assert "result" in handshake_response
            assert "version" in handshake_response["result"]
            assert "capabilities" in handshake_response["result"]
            
            # Check list_projects response
            list_projects_response = responses[1]
            assert list_projects_response["jsonrpc"] == "2.0" 
            assert list_projects_response["id"] == "list-projects-1"
            assert "result" in list_projects_response
            assert list_projects_response["result"]["status"] == "success"
            assert "projects" in list_projects_response["result"]

        finally:
            # Clean up: stop and remove the container
            subprocess.run(
                ["docker", "rm", "-f", container_name],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False  # Don't fail if cleanup fails
            ) 