#!/usr/bin/env python3
"""
Helper script to run all tests for the MCP server.

This script runs both unit and integration tests, and can enable Docker tests
when the --docker flag is provided.
"""

import os
import sys
import argparse
import subprocess

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Run tests for the MCP server")
    parser.add_argument("--docker", action="store_true", help="Enable Docker integration tests")
    parser.add_argument("--coverage", action="store_true", help="Generate coverage report")
    parser.add_argument("--unit-only", action="store_true", help="Run only unit tests")
    parser.add_argument("--integration-only", action="store_true", help="Run only integration tests")
    return parser.parse_args()

def main():
    """Run the tests based on command line arguments."""
    args = parse_args()
    
    # Set environment variable for Docker tests if enabled
    if args.docker:
        os.environ["DOCKER_TEST_ENABLED"] = "true"
    
    # Build command
    cmd = ["pytest", "-v"]
    
    # Add coverage if requested
    if args.coverage:
        cmd.extend(["--cov=.", "--cov-report=term", "--cov-report=html"])
    
    # Determine which tests to run
    if args.unit_only:
        cmd.append("tests/unit/")
    elif args.integration_only:
        cmd.append("tests/integration/")
    
    # Print command
    print(f"Running: {' '.join(cmd)}")
    
    # Run the tests
    result = subprocess.run(cmd)
    
    # Return the exit code
    return result.returncode

if __name__ == "__main__":
    sys.exit(main()) 