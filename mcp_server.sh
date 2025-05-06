#!/bin/bash
# Management script for Dependency Analyzer MCP Server
# This script provides commands for starting, stopping, and managing the server

# Default configuration
PORT=8000
MODE="http"
LOG_LEVEL="INFO"
DOCKERFILE="./Dockerfile"
DOCKER_COMPOSE="./docker-compose.yml"
CONTAINER_PREFIX="dependency-analyzer"

# Function to display usage information
show_usage() {
    echo "Dependency Analyzer MCP Server Management Script"
    echo ""
    echo "Usage: $0 [command] [options]"
    echo ""
    echo "Commands:"
    echo "  start        Start the MCP server"
    echo "  stop         Stop the MCP server"
    echo "  restart      Restart the MCP server"
    echo "  status       Show server status"
    echo "  logs         Show server logs"
    echo "  build        Build the Docker image"
    echo "  shell        Open a shell in the running container"
    echo "  help         Show this help message"
    echo ""
    echo "Options:"
    echo "  --mode=MODE      Set the server mode (http or stdio, default: $MODE)"
    echo "  --port=PORT      Set the server port (default: $PORT)"
    echo "  --log-level=LEVEL Set the log level (default: $LOG_LEVEL)"
    echo "  --docker         Use Docker for server operations"
    echo "  --attach         Attach to stdio mode (when using Docker)"
    echo ""
    echo "Examples:"
    echo "  $0 start --mode=http --port=8000"
    echo "  $0 start --mode=stdio"
    echo "  $0 start --docker --mode=http"
    echo "  $0 stop"
    echo "  $0 logs"
    echo ""
}

# Parse command line arguments
COMMAND=""
USE_DOCKER=false
ATTACH=false

while [[ $# -gt 0 ]]; do
    case $1 in
        start|stop|restart|status|logs|build|shell|help)
            COMMAND="$1"
            shift
            ;;
        --mode=*)
            MODE="${1#*=}"
            shift
            ;;
        --port=*)
            PORT="${1#*=}"
            shift
            ;;
        --log-level=*)
            LOG_LEVEL="${1#*=}"
            shift
            ;;
        --docker)
            USE_DOCKER=true
            shift
            ;;
        --attach)
            ATTACH=true
            shift
            ;;
        *)
            echo "Unknown option: $1"
            show_usage
            exit 1
            ;;
    esac
done

# Function to check if Docker is available
check_docker() {
    if ! command -v docker &> /dev/null; then
        echo "Error: Docker is not installed or not in PATH"
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        echo "Error: Docker Compose is not installed or not in PATH"
        exit 1
    fi
}

# Function to start the server
start_server() {
    if [ "$USE_DOCKER" = true ]; then
        check_docker
        
        echo "Starting MCP server in Docker ($MODE mode)..."
        
        if [ "$MODE" = "stdio" ]; then
            # Start the stdio mode service
            docker-compose -f "$DOCKER_COMPOSE" up -d mcp-stdio
            
            if [ "$ATTACH" = true ]; then
                echo "Attaching to stdio mode container..."
                docker attach "${CONTAINER_PREFIX}-mcp-stdio"
            else
                echo "Server started in stdio mode, use '$0 shell --mode=stdio' to connect"
            fi
        else
            # Start the HTTP mode service
            docker-compose -f "$DOCKER_COMPOSE" up -d mcp-http
            echo "Server started at http://localhost:$PORT"
        fi
    else
        # Start natively
        echo "Starting MCP server natively ($MODE mode)..."
        
        # Check if Python and required packages are available
        if ! command -v python3 &> /dev/null; then
            echo "Error: Python 3 is not installed or not in PATH"
            exit 1
        fi
        
        # Create a log directory if it doesn't exist
        mkdir -p logs
        
        if [ "$MODE" = "stdio" ]; then
            # Start the stdio mode server
            python3 stdio_mcp.py &
            echo "Server started in stdio mode (PID: $!)"
        else
            # Start the HTTP mode server
            nohup python3 server_mcp.py --port="$PORT" > logs/server.log 2>&1 &
            echo "Server started at http://localhost:$PORT (PID: $!)"
            echo "Logs available at logs/server.log"
        fi
    fi
}

# Function to stop the server
stop_server() {
    if [ "$USE_DOCKER" = true ]; then
        check_docker
        
        echo "Stopping MCP server in Docker..."
        docker-compose -f "$DOCKER_COMPOSE" down
        echo "Server stopped"
    else
        # Stop natively
        echo "Stopping MCP server natively..."
        
        if [ "$MODE" = "stdio" ]; then
            pkill -f "python3 stdio_mcp.py"
        else
            pkill -f "python3 server_mcp.py"
        fi
        
        echo "Server stopped"
    fi
}

# Function to show server status
show_status() {
    if [ "$USE_DOCKER" = true ]; then
        check_docker
        
        echo "MCP server status (Docker):"
        docker-compose -f "$DOCKER_COMPOSE" ps
    else
        # Show native process status
        echo "MCP server status (Native):"
        
        if [ "$MODE" = "stdio" ]; then
            pgrep -f "python3 stdio_mcp.py" > /dev/null
        else
            pgrep -f "python3 server_mcp.py" > /dev/null
        fi
        
        if [ $? -eq 0 ]; then
            echo "Server is running"
            
            if [ "$MODE" = "http" ]; then
                # Try to get more information from the server API
                if command -v curl &> /dev/null; then
                    curl -s http://localhost:$PORT/api/health | grep -q "\"status\": \"healthy\""
                    if [ $? -eq 0 ]; then
                        echo "Server health: HEALTHY"
                    else
                        echo "Server health: NOT HEALTHY"
                    fi
                fi
            fi
        else
            echo "Server is not running"
        fi
    fi
}

# Function to show server logs
show_logs() {
    if [ "$USE_DOCKER" = true ]; then
        check_docker
        
        echo "MCP server logs (Docker):"
        if [ "$MODE" = "stdio" ]; then
            docker-compose -f "$DOCKER_COMPOSE" logs mcp-stdio
        else
            docker-compose -f "$DOCKER_COMPOSE" logs mcp-http
        fi
    else
        # Show native logs
        echo "MCP server logs (Native):"
        
        if [ -f logs/server.log ]; then
            tail -n 50 logs/server.log
        else
            echo "No log file found at logs/server.log"
        fi
    fi
}

# Function to build Docker image
build_docker() {
    check_docker
    
    echo "Building Docker image..."
    docker-compose -f "$DOCKER_COMPOSE" build
    echo "Build complete"
}

# Function to open a shell in the running container
open_shell() {
    if [ "$USE_DOCKER" = false ]; then
        echo "Error: Shell command is only available with --docker option"
        exit 1
    fi
    
    check_docker
    
    if [ "$MODE" = "stdio" ]; then
        echo "Opening shell in stdio mode container..."
        docker-compose -f "$DOCKER_COMPOSE" exec mcp-stdio /bin/bash
    else
        echo "Opening shell in HTTP mode container..."
        docker-compose -f "$DOCKER_COMPOSE" exec mcp-http /bin/bash
    fi
}

# Execute the requested command
case "$COMMAND" in
    start)
        start_server
        ;;
    stop)
        stop_server
        ;;
    restart)
        stop_server
        sleep 2
        start_server
        ;;
    status)
        show_status
        ;;
    logs)
        show_logs
        ;;
    build)
        build_docker
        ;;
    shell)
        open_shell
        ;;
    help|"")
        show_usage
        ;;
    *)
        echo "Unknown command: $COMMAND"
        show_usage
        exit 1
        ;;
esac

exit 0 