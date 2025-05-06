#!/usr/bin/env python3
"""
MCP Server for Dependency Analysis.
This server provides an MCP-compatible API for AI agents to analyze code dependencies.

Usage:
    python3 server_mcp.py [--port=<port>] [--no-browser]
"""

import os
import sys
import json
import time
import argparse
import signal
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from socketserver import ThreadingMixIn
import urllib.parse
from datetime import datetime
import traceback

# Import the config module
from config import config, initialize_config

# Import the MCP API module
from mcp_api import handle_mcp_request, handle_mcp_resource
from error_handler import handle_exception, create_error_response, get_http_status_for_error
from validation import validate_resource_uri, validate_tool_parameters
from structured_logging import get_logger, create_correlation_id
# Import the MCP compatibility endpoints
from mcp_endpoints import get_tools_list, get_capabilities

# Initialize configuration
initialize_config()

# Configure logging
logger = get_logger("mcp_server", config.get("logging.level"))

# Set up argument parser
parser = argparse.ArgumentParser(description='Start the dependency analyzer MCP server')
parser.add_argument('--port', type=int, default=config.get("server.port", 8000), help='Port to run the server on')
parser.add_argument('--no-browser', action='store_true', help='Don\'t open the browser automatically')
parser.add_argument('--config', help='Path to the configuration file')
args = parser.parse_args()

# If a config file was specified, reload with that file
if args.config:
    initialize_config(args.config)

# Set the server port (command line overrides config)
PORT = args.port

# Constants for project and analysis directories
PROJECTS_DIR = config.get("projects.projects_dir", os.path.join(os.getcwd(), "projects"))
ANALYSIS_DIR = config.get("projects.analysis_dir", os.path.join(os.getcwd(), "analysis"))
CONFIG_DIR = os.path.join(os.getcwd(), "config")

# Server start time for uptime tracking
SERVER_START_TIME = datetime.now()

# Ensure directories exist
os.makedirs(PROJECTS_DIR, exist_ok=True)
os.makedirs(ANALYSIS_DIR, exist_ok=True)
os.makedirs(CONFIG_DIR, exist_ok=True)

# Handler for graceful shutdown
def signal_handler(sig, frame):
    logger.info("Shutting down MCP server...")
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    """Handle requests in a separate thread."""
    pass

class MCPRequestHandler(BaseHTTPRequestHandler):
    """Custom handler for MCP API requests."""
    
    def __init__(self, *args, **kwargs):
        self.correlation_id = create_correlation_id()
        self.request_logger = logger.with_correlation_id(self.correlation_id)
        super().__init__(*args, **kwargs)
    
    def log_request(self, code='-', size='-'):
        """Log requests with timestamps"""
        self.request_logger.info(
            f"{self.command} {self.path} - {code}",
            method=self.command,
            path=self.path,
            status_code=code,
            client_address=self.client_address[0]
        )
    
    def log_error(self, format, *args):
        """Log errors with timestamps"""
        self.request_logger.error(
            format % args,
            method=self.command,
            path=self.path,
            client_address=self.client_address[0]
        )
    
    def send_json_response(self, data, status=200):
        """Helper method to send JSON responses"""
        self.send_response(status)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
        self.send_header('Pragma', 'no-cache')
        self.send_header('Expires', '0')
        self.send_header('X-Correlation-ID', self.correlation_id)
        self.end_headers()
        
        # Add correlation ID to the response
        if isinstance(data, dict) and 'correlation_id' not in data:
            data['correlation_id'] = self.correlation_id
        
        # Convert data to JSON
        response = json.dumps(data, indent=2).encode('utf-8')
        self.wfile.write(response)
        
        # Log response size and status
        self.request_logger.debug(
            f"Response sent: {status}",
            status_code=status,
            response_size=len(response)
        )
    
    def do_OPTIONS(self):
        """Handle OPTIONS requests for CORS preflight"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.send_header('X-Correlation-ID', self.correlation_id)
        self.end_headers()
    
    def do_GET(self):
        """Handle GET requests."""
        try:
            self.request_logger.info(
                f"Received GET request: {self.path}",
                path=self.path
            )
            
            # Parse the URL
            parsed_url = urllib.parse.urlparse(self.path)
            path = parsed_url.path
            query = urllib.parse.parse_qs(parsed_url.query)
            
            # Handle MCP protocol endpoints
            if path == '/api/tools':
                self.request_logger.info("MCP tools list request")
                tools_response = get_tools_list()
                self.send_json_response(tools_response)
                return
                
            if path == '/api/v1/capabilities':
                self.request_logger.info("MCP capabilities request")
                capabilities_response = get_capabilities()
                self.send_json_response(capabilities_response)
                return
            
            # Handle health check endpoint
            if path == '/api/health':
                self.handle_health_check()
                return
            
            # Handle server info endpoint
            if path == '/api/info':
                self.handle_server_info()
                return
            
            # Handle config endpoint
            if path == '/api/config':
                self.handle_config_info()
                return
            
            # Handle MCP resource requests
            if path.startswith('/api/resource/'):
                # Extract the resource URI from the path
                resource_uri = path[len('/api/resource/'):]
                resource_uri = urllib.parse.unquote(resource_uri)
                
                self.request_logger.info(
                    f"Resource request: {resource_uri}",
                    resource_uri=resource_uri
                )
                
                # Validate the resource URI
                is_valid, error_details = validate_resource_uri(resource_uri)
                if not is_valid:
                    self.request_logger.warning(
                        f"Invalid resource URI: {resource_uri}",
                        error=error_details
                    )
                    error_response = create_error_response(
                        code=error_details["code"],
                        message=error_details["message"],
                        details=error_details.get("details")
                    )
                    self.send_json_response(error_response, get_http_status_for_error(error_details["code"]))
                    return
                
                # Handle the resource request
                response = handle_mcp_resource(resource_uri)
                self.send_json_response(response)
                return
            
            # Handle MCP tool requests
            elif path.startswith('/api/tools/'):
                # Extract the tool name from the path
                tool_name = path.split('/')[-1]
                
                self.request_logger.info(
                    f"Tool request: {tool_name}",
                    tool=tool_name,
                    parameters=query
                )
                
                # Prepare parameters from query string
                params = {}
                for key, value_list in query.items():
                    if len(value_list) == 1:
                        # Try to parse JSON values
                        try:
                            params[key] = json.loads(value_list[0])
                        except:
                            params[key] = value_list[0]
                    else:
                        params[key] = value_list
                
                # Validate the tool parameters
                is_valid, error_details = validate_tool_parameters(tool_name, params)
                if not is_valid:
                    self.request_logger.warning(
                        f"Invalid parameters for tool {tool_name}",
                        error=error_details,
                        parameters=params
                    )
                    error_response = create_error_response(
                        code=error_details["code"],
                        message=error_details["message"],
                        details=error_details.get("details")
                    )
                    self.send_json_response(error_response, get_http_status_for_error(error_details["code"]))
                    return
                
                # Handle the tool request
                response = handle_mcp_request(tool_name, params)
                self.send_json_response(response)
                return
            
            # Handle static files
            elif path == '/':
                # Serve the index/dashboard page
                self.serve_file('index.html')
                return
            else:
                # Serve other static files
                file_path = path.lstrip('/')
                self.serve_file(file_path)
                return
        
        except Exception as e:
            # Use our standardized error handler
            self.request_logger.error(
                f"Error handling GET request: {str(e)}",
                exception=traceback.format_exc()
            )
            
            context = {
                "path": self.path,
                "method": self.command,
                "client_address": self.client_address[0],
                "correlation_id": self.correlation_id
            }
            error_response = handle_exception(e, context)
            self.send_json_response(error_response, get_http_status_for_error(error_response["error"]["code"]))
    
    def handle_config_info(self):
        """Handle configuration info endpoint"""
        try:
            self.request_logger.debug("Handling config info request")
            
            # Get config file path
            config_file_path = config.get_config_file_path()
            
            # Create safe configuration to expose (remove sensitive info)
            safe_config = config.to_dict()
            if "auth" in safe_config and "password" in safe_config["auth"]:
                safe_config["auth"]["password"] = "********" if safe_config["auth"]["password"] else None
            
            config_data = {
                "status": "success",
                "data": {
                    "config": safe_config,
                    "config_file": config_file_path,
                    "env_vars": {
                        "PORT": os.environ.get("PORT"),
                        "HOST": os.environ.get("HOST"),
                        "MCP_MODE": os.environ.get("MCP_MODE"),
                        "LOG_LEVEL": os.environ.get("LOG_LEVEL"),
                        "PROJECTS_DIR": os.environ.get("PROJECTS_DIR"),
                        "ANALYSIS_DIR": os.environ.get("ANALYSIS_DIR"),
                    }
                }
            }
            
            self.send_json_response(config_data)
        except Exception as e:
            # Use our standardized error handler
            self.request_logger.error(
                f"Error in config info: {str(e)}",
                exception=traceback.format_exc()
            )
            
            error_response = handle_exception(e, {
                "endpoint": "config",
                "correlation_id": self.correlation_id
            })
            self.send_json_response(error_response, get_http_status_for_error(error_response["error"]["code"]))
    
    def handle_health_check(self):
        """Handle health check endpoint for Docker health checks"""
        try:
            self.request_logger.debug("Handling health check request")
            
            # Check if critical components are functioning
            # 1. Check if we can access the project directory
            projects_accessible = os.access(PROJECTS_DIR, os.R_OK | os.W_OK)
            
            # 2. Check if we can access the analysis directory
            analysis_accessible = os.access(ANALYSIS_DIR, os.R_OK | os.W_OK)
            
            # 3. Check if MCP API is responsive
            api_responsive = True  # Simplified check
            
            # Calculate uptime
            uptime_seconds = (datetime.now() - SERVER_START_TIME).total_seconds()
            
            if projects_accessible and analysis_accessible and api_responsive:
                health_data = {
                    "status": "healthy",
                    "uptime": uptime_seconds,
                    "version": "1.0.0",
                    "checks": {
                        "projects_directory": "accessible" if projects_accessible else "inaccessible",
                        "analysis_directory": "accessible" if analysis_accessible else "inaccessible",
                        "api": "responsive" if api_responsive else "unresponsive"
                    }
                }
                self.send_json_response(health_data)
            else:
                self.request_logger.warning(
                    "Health check failed",
                    projects_accessible=projects_accessible,
                    analysis_accessible=analysis_accessible,
                    api_responsive=api_responsive
                )
                
                health_data = {
                    "status": "unhealthy",
                    "uptime": uptime_seconds,
                    "version": "1.0.0",
                    "checks": {
                        "projects_directory": "accessible" if projects_accessible else "inaccessible",
                        "analysis_directory": "accessible" if analysis_accessible else "inaccessible",
                        "api": "responsive" if api_responsive else "unresponsive"
                    }
                }
                self.send_json_response(health_data, 503)  # Service Unavailable
        except Exception as e:
            # Use our standardized error handler
            self.request_logger.error(
                f"Error in health check: {str(e)}",
                exception=traceback.format_exc()
            )
            
            error_response = handle_exception(e, {
                "endpoint": "health",
                "correlation_id": self.correlation_id
            })
            self.send_json_response(error_response, get_http_status_for_error(error_response["error"]["code"]))
    
    def handle_server_info(self):
        """Handle server info endpoint"""
        try:
            self.request_logger.debug("Handling server info request")
            
            # Get system information
            import platform
            import psutil
            
            process = psutil.Process()
            memory_info = process.memory_info()
            
            # Get project statistics
            project_count = len([name for name in os.listdir(PROJECTS_DIR) 
                              if os.path.isdir(os.path.join(PROJECTS_DIR, name))])
            
            # Calculate uptime
            uptime_seconds = (datetime.now() - SERVER_START_TIME).total_seconds()
            
            info_data = {
                "status": "success",
                "data": {
                    "server": {
                        "version": "1.0.0",
                        "uptime": uptime_seconds,
                        "start_time": SERVER_START_TIME.isoformat(),
                        "mode": config.get("server.mode", "http")
                    },
                    "system": {
                        "platform": platform.platform(),
                        "python": platform.python_version(),
                        "memory_usage": {
                            "rss_mb": memory_info.rss / (1024 * 1024),
                            "vms_mb": memory_info.vms / (1024 * 1024)
                        },
                        "cpu_percent": process.cpu_percent(interval=0.1)
                    },
                    "projects": {
                        "count": project_count,
                        "directory": PROJECTS_DIR
                    },
                    "config": {
                        "file": config.get_config_file_path(),
                        "log_level": config.get("logging.level")
                    }
                }
            }
            
            self.send_json_response(info_data)
        except Exception as e:
            # Use our standardized error handler
            self.request_logger.error(
                f"Error in server info: {str(e)}",
                exception=traceback.format_exc()
            )
            
            error_response = handle_exception(e, {
                "endpoint": "info",
                "correlation_id": self.correlation_id
            })
            self.send_json_response(error_response, get_http_status_for_error(error_response["error"]["code"]))
    
    def do_POST(self):
        """Handle POST requests."""
        try:
            self.request_logger.info(
                f"Received POST request: {self.path}",
                path=self.path
            )
            
            # Parse the URL
            parsed_url = urllib.parse.urlparse(self.path)
            path = parsed_url.path
            
            # Read the request body
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length).decode('utf-8')
            
            # Parse the request body as JSON
            try:
                params = json.loads(body) if body else {}
                
                self.request_logger.debug(
                    "Parsed request body",
                    body_size=content_length,
                    params=params
                )
            except json.JSONDecodeError:
                self.request_logger.warning(
                    "Invalid JSON in request body",
                    body=body[:1000] if len(body) > 1000 else body
                )
                
                error_response = create_error_response(
                    code="invalid_json",
                    message="Invalid JSON in request body"
                )
                self.send_json_response(error_response, get_http_status_for_error("invalid_json"))
                return
            
            # Handle MCP tool requests
            if path.startswith('/api/tools/'):
                # Extract the tool name from the path
                tool_name = path.split('/')[-1]
                
                self.request_logger.info(
                    f"Tool request: {tool_name}",
                    tool=tool_name
                )
                
                # Validate the tool parameters
                is_valid, error_details = validate_tool_parameters(tool_name, params)
                if not is_valid:
                    self.request_logger.warning(
                        f"Invalid parameters for tool {tool_name}",
                        error=error_details,
                        parameters=params
                    )
                    
                    error_response = create_error_response(
                        code=error_details["code"],
                        message=error_details["message"],
                        details=error_details.get("details")
                    )
                    self.send_json_response(error_response, get_http_status_for_error(error_details["code"]))
                    return
                
                # Handle the tool request
                response = handle_mcp_request(tool_name, params)
                self.send_json_response(response)
                return
            
            else:
                self.request_logger.warning(
                    f"Endpoint not found: {path}",
                    path=path
                )
                
                error_response = create_error_response(
                    code="not_found",
                    message=f"Endpoint not found: {path}"
                )
                self.send_json_response(error_response, get_http_status_for_error("not_found"))
        
        except Exception as e:
            # Use our standardized error handler
            self.request_logger.error(
                f"Error handling POST request: {str(e)}",
                exception=traceback.format_exc()
            )
            
            context = {
                "path": self.path,
                "method": self.command,
                "client_address": self.client_address[0],
                "correlation_id": self.correlation_id
            }
            error_response = handle_exception(e, context)
            self.send_json_response(error_response, get_http_status_for_error(error_response["error"]["code"]))
    
    def serve_file(self, file_path):
        """Serve a static file."""
        # Default to index.html
        if not file_path or file_path == 'index.html':
            file_path = 'dependency-visualizer.html'
        
        self.request_logger.debug(
            f"Serving file: {file_path}",
            file_path=file_path
        )
        
        # Security check - prevent path traversal
        if '..' in file_path:
            self.request_logger.warning(
                "Path traversal attempt detected",
                file_path=file_path
            )
            
            error_response = create_error_response(
                code="forbidden",
                message="Forbidden: Path traversal attempt detected"
            )
            self.send_json_response(error_response, get_http_status_for_error("forbidden"))
            return
        
        # Try to find the file
        for base_dir in [os.getcwd(), os.path.join(os.getcwd(), 'static')]:
            full_path = os.path.join(base_dir, file_path)
            if os.path.exists(full_path) and os.path.isfile(full_path):
                try:
                    content_type = self.get_content_type(file_path)
                    with open(full_path, 'rb') as f:
                        content = f.read()
                    
                    self.send_response(200)
                    self.send_header('Content-type', content_type)
                    self.send_header('Content-Length', len(content))
                    self.send_header('X-Correlation-ID', self.correlation_id)
                    self.end_headers()
                    self.wfile.write(content)
                    
                    self.request_logger.debug(
                        f"File served successfully: {file_path}",
                        file_path=file_path,
                        file_size=len(content),
                        content_type=content_type
                    )
                    return
                except Exception as e:
                    self.request_logger.error(
                        f"Error serving file {file_path}: {e}",
                        file_path=file_path,
                        exception=traceback.format_exc()
                    )
                    
                    error_response = handle_exception(e, {
                        "file_path": file_path,
                        "correlation_id": self.correlation_id
                    })
                    self.send_json_response(error_response, get_http_status_for_error(error_response["error"]["code"]))
                    return
        
        # File not found
        self.request_logger.warning(
            f"File not found: {file_path}",
            file_path=file_path
        )
        
        error_response = create_error_response(
            code="not_found",
            message=f"File not found: {file_path}"
        )
        self.send_json_response(error_response, get_http_status_for_error("not_found"))
    
    def get_content_type(self, file_path):
        """Determine the content type based on file extension."""
        _, ext = os.path.splitext(file_path)
        ext = ext.lower()
        
        content_types = {
            '.html': 'text/html',
            '.js': 'application/javascript',
            '.css': 'text/css',
            '.json': 'application/json',
            '.png': 'image/png',
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.gif': 'image/gif',
            '.svg': 'image/svg+xml',
            '.ico': 'image/x-icon',
        }
        
        return content_types.get(ext, 'application/octet-stream')

def run(server_class=ThreadedHTTPServer, handler_class=MCPRequestHandler, port=PORT):
    """Run the MCP server."""
    host = config.get("server.host", "")
    server_address = (host, port)
    httpd = server_class(server_address, handler_class)
    
    logger.info(f"Dependency Analyzer MCP Server started at http://{host or 'localhost'}:{port}/")
    logger.info(f"API endpoints available at http://{host or 'localhost'}:{port}/api/tools/ and http://{host or 'localhost'}:{port}/api/resource/")
    logger.info(f"Health check available at http://{host or 'localhost'}:{port}/api/health")
    logger.info(f"Config info available at http://{host or 'localhost'}:{port}/api/config")
    logger.info(f"Using configuration: {config.get_config_file_path() or 'default values with environment overrides'}")
    logger.info("Press Ctrl+C to stop the server")
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    
    httpd.server_close()
    logger.info("Server stopped.")

if __name__ == '__main__':
    run() 