#!/usr/bin/env python3
"""
Enhanced server for dependency analysis visualization.
This server provides an interface to run the dependency analysis script directly from the browser,
visualize the results, and allow for cancelling running processes.

Usage:
    python3 server.py [--root=<path>] [--port=<port>] [--script=<path>] [--no-browser]
"""

import os
import sys
import json
import time
import argparse
import subprocess
import webbrowser
import signal
import threading
from http.server import HTTPServer, SimpleHTTPRequestHandler
from socketserver import ThreadingMixIn
import urllib.parse
from datetime import datetime
import shutil

# Set up argument parser
parser = argparse.ArgumentParser(description='Start the dependency visualization server')
parser.add_argument('--port', type=int, default=8000, help='Port to run the server on')
parser.add_argument('--root', type=str, default='', help='Root directory of the project to analyze')
parser.add_argument('--script', type=str, default='', help='Path to the analysis script')
parser.add_argument('--no-browser', action='store_true', help='Don\'t open the browser automatically')
args = parser.parse_args()

# Set the server port
PORT = args.port

# Detect the project root if not provided
ROOT_DIR = args.root
if not ROOT_DIR:
    # Try to find a .git directory going up from the current directory
    current_dir = os.path.abspath(os.getcwd())
    while current_dir != os.path.dirname(current_dir):  # Stop at root directory
        if os.path.exists(os.path.join(current_dir, '.git')):
            ROOT_DIR = current_dir
            print(f"Detected project root at: {ROOT_DIR}")
            break
        current_dir = os.path.dirname(current_dir)
    
    # If we still don't have a root, use the current directory
    if not ROOT_DIR:
        ROOT_DIR = os.path.abspath(os.getcwd())
        print(f"Using current directory as project root: {ROOT_DIR}")

# Get the dependency analyzer tool directory (where this server.py is located)
TOOL_DIR = os.path.dirname(os.path.abspath(__file__))

# Determine the analysis script path
SCRIPT_PATH = args.script
if not SCRIPT_PATH:
    # First look in the scripts directory relative to this server.py
    SCRIPT_PATH = os.path.join(TOOL_DIR, 'scripts', 'enhanced-dependency-analysis.cjs')
    if not os.path.exists(SCRIPT_PATH):
        print(f"Error: Could not find enhanced-dependency-analysis.cjs at {SCRIPT_PATH}")
        # Try the current directory's scripts folder
        SCRIPT_PATH = os.path.join(ROOT_DIR, 'scripts', 'enhanced-dependency-analysis.cjs')
        if not os.path.exists(SCRIPT_PATH):
            print(f"Error: Could not find enhanced-dependency-analysis.cjs at {SCRIPT_PATH}")
            print("Please provide the script path with --script option")
            sys.exit(1)

print(f"Using analysis script at: {SCRIPT_PATH}")
print(f"Analyzing project at: {ROOT_DIR}")

# Global variables for tracking the analysis process
current_process = None
process_output = []
process_complete = False
process_running = False
process_start_time = None
process_exit_code = None

# Create a lock for thread-safe operations
process_lock = threading.Lock()

# Handler for graceful shutdown
def signal_handler(sig, frame):
    print("Shutting down server...")
    if current_process:
        try:
            current_process.terminate()
            print("Terminated running analysis process")
        except:
            pass
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

# Thread for capturing process output
def capture_output(process):
    global process_output, process_complete, process_running, process_exit_code
    
    for line in iter(process.stdout.readline, b''):
        with process_lock:
            process_output.append(line.decode('utf-8', errors='replace').rstrip())
    
    process.stdout.close()
    return_code = process.wait()
    
    with process_lock:
        process_exit_code = return_code
        process_complete = True
        process_running = False
    
    print(f"Process completed with exit code: {return_code}")

class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    """Handle requests in a separate thread."""
    pass

class DependencyAnalysisHandler(SimpleHTTPRequestHandler):
    """Custom handler for dependency analysis visualization."""
    
    def __init__(self, *args, directory=None, **kwargs):
        self.directory = directory
        super().__init__(*args, **kwargs)
    
    def translate_path(self, path):
        """Translate request path to server filesystem path.
        Modified to serve files from the tool directory and the project directory."""
        # Parse path
        path = path.split('?', 1)[0]
        path = path.split('#', 1)[0]
        
        # Normalize the path
        trailing_slash = path.rstrip().endswith('/')
        path = urllib.parse.unquote(path)
        
        # Default to index.html if root is requested
        if path == '/':
            path = '/dependency-visualizer.html'
        
        # Convert path to filesystem path
        path = path.strip('/')
        
        # First look in the tool directory
        full_path = os.path.join(TOOL_DIR, path)
        
        # If not found there, look in project root
        if not os.path.exists(full_path):
            full_path = os.path.join(ROOT_DIR, path)
        
        return full_path
    
    def list_directory(self, path):
        """Override to redirect to the visualizer."""
        self.send_response(302)
        self.send_header('Location', '/dependency-visualizer.html')
        self.end_headers()
        return None
    
    def do_GET(self):
        """Handle GET requests."""
        if self.path == '/api/status':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
            self.send_header('Pragma', 'no-cache')
            self.send_header('Expires', '0')
            self.end_headers()
            
            with process_lock:
                status = {
                    'running': process_running,
                    'complete': process_complete,
                    'exitCode': process_exit_code,
                    'output': process_output[-50:] if process_output else [],  # Send last 50 lines to prevent large responses
                    'outputLength': len(process_output),
                    'startTime': process_start_time
                }
            
            self.wfile.write(json.dumps(status).encode())
            return
        
        if self.path == '/api/run':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            with process_lock:
                if process_running:
                    self.wfile.write(json.dumps({'error': 'Process already running'}).encode())
                    return
                
                try:
                    # Use global variables declared at module level
                    global current_process, process_start_time
                    
                    # Reset state
                    process_output.clear()
                    global process_complete, process_running, process_exit_code
                    process_complete = False
                    process_running = True
                    process_start_time = datetime.now().isoformat()
                    process_exit_code = None
                    
                    # Start the analysis process
                    current_process = subprocess.Popen(
                        ['node', SCRIPT_PATH, f'--root-dir={ROOT_DIR}'],
                        stdout=subprocess.PIPE,
                        stderr=subprocess.STDOUT,
                        bufsize=1,
                        universal_newlines=False,
                        cwd=TOOL_DIR
                    )
                    
                    # Start a thread to capture output
                    output_thread = threading.Thread(target=capture_output, args=(current_process,))
                    output_thread.daemon = True
                    output_thread.start()
                    
                    self.wfile.write(json.dumps({'status': 'started'}).encode())
                
                except Exception as e:
                    process_running = False
                    self.wfile.write(json.dumps({'error': str(e)}).encode())
            
            return
        
        if self.path == '/api/cancel':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            with process_lock:
                if not process_running or not current_process:
                    self.wfile.write(json.dumps({'status': 'not_running'}).encode())
                    return
                
                try:
                    current_process.terminate()
                    global process_running, process_complete, process_exit_code
                    process_running = False
                    process_complete = True
                    process_exit_code = -1
                    process_output.append("Process cancelled by user")
                    self.wfile.write(json.dumps({'status': 'cancelled'}).encode())
                
                except Exception as e:
                    self.wfile.write(json.dumps({'error': str(e)}).encode())
            
            return
        
        # Default: serve files
        try:
            super().do_GET()
        except Exception as e:
            print(f"Error handling GET request: {e}")
            self.send_error(500, f"Internal server error: {e}")

# Start the server
def run(server_class=ThreadedHTTPServer, handler_class=DependencyAnalysisHandler, port=PORT):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print(f"Server started at http://localhost:{port}/")
    print(f"Access the visualization at http://localhost:{port}/dependency-visualizer.html")
    print("Press Ctrl+C to stop the server")
    
    # Open the browser if requested
    if not args.no_browser:
        webbrowser.open(f"http://localhost:{port}/dependency-visualizer.html")
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()
    print("Server stopped.")

if __name__ == '__main__':
    run() 