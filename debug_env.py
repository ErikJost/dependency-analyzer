#!/usr/bin/env python3
import os
import sys
import json

print("Debugging environment variables")
print(f"Current working directory: {os.getcwd()}")
print(f"localProjectDir would be: {os.getcwd()}")
print("Environment variables:")
for key, value in os.environ.items():
    print(f"  {key}={value}")

# Just echo back any input so Cursor sees a response
for line in sys.stdin:
    print(line.strip()) 