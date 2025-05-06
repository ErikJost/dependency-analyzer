#!/usr/bin/env python3
"""
Monitor Docker processes to see if Cursor is starting our container
"""
import time
import subprocess
import json
import datetime

def timestamp():
    return datetime.datetime.now().strftime("%H:%M:%S")

def get_docker_processes():
    """Get information about running Docker containers"""
    try:
        result = subprocess.run(
            ["docker", "ps", "--format", "{{json .}}"],
            capture_output=True,
            text=True,
            check=True
        )
        
        containers = []
        for line in result.stdout.splitlines():
            if line.strip():
                containers.append(json.loads(line))
        
        return containers
    except subprocess.CalledProcessError:
        print(f"[{timestamp()}] Error running docker ps")
        return []

def main():
    """Monitor Docker processes continuously"""
    print(f"[{timestamp()}] Starting Docker process monitor. Press Ctrl+C to stop.")
    
    last_seen = set()
    
    try:
        while True:
            containers = get_docker_processes()
            current = set()
            
            for container in containers:
                container_id = container.get("ID", "")
                image = container.get("Image", "")
                command = container.get("Command", "")
                status = container.get("Status", "")
                
                container_info = f"{container_id} | {image} | {command} | {status}"
                current.add(container_info)
                
                if container_info not in last_seen:
                    print(f"[{timestamp()}] NEW CONTAINER: {container_info}")
                
                if "mcp/dependmap" in image:
                    print(f"[{timestamp()}] FOUND TARGET: {container_info}")
                    
                    # Get more details about this container
                    try:
                        inspect = subprocess.run(
                            ["docker", "inspect", container_id],
                            capture_output=True,
                            text=True,
                            check=True
                        )
                        container_details = json.loads(inspect.stdout)[0]
                        
                        # Print the command and environment
                        print(f"[{timestamp()}] COMMAND: {container_details.get('Config', {}).get('Cmd', [])}")
                        print(f"[{timestamp()}] ENV: {container_details.get('Config', {}).get('Env', [])}")
                        
                        # Print the mounts
                        mounts = container_details.get('Mounts', [])
                        print(f"[{timestamp()}] MOUNTS: {json.dumps(mounts, indent=2)}")
                    except subprocess.CalledProcessError:
                        print(f"[{timestamp()}] Error inspecting container {container_id}")
            
            # Check for containers that disappeared
            for container_info in last_seen - current:
                print(f"[{timestamp()}] REMOVED: {container_info}")
            
            last_seen = current
            time.sleep(1)
    except KeyboardInterrupt:
        print(f"[{timestamp()}] Stopping monitor")

if __name__ == "__main__":
    main() 