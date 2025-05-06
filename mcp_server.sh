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
HOST_PROJECT_DIR=${HOST_PROJECT_DIR:-$(cd .. && pwd)}  # Default to parent directory

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
    echo "  shell        Open a shell in the container"
    echo ""
    echo "Options:"
    echo "  --port       Port to run the server on (default: $PORT)"
    echo "  --mode       Server mode: http or stdio (default: $MODE)"
    echo "  --docker     Use Docker mode"
    echo "  --log-level  Set log level: DEBUG, INFO, WARNING, ERROR (default: $LOG_LEVEL)"
    echo "  --host-dir   Host directory to mount in Docker (default: $HOST_PROJECT_DIR)"
    echo ""
    echo "Examples:"
    echo "  $0 start --port 9000 --mode http"
    echo "  $0 start --docker --mode stdio"
    echo "  $0 logs --docker"
    echo "  $0 stop"
    echo ""
}

# Parse command
if [ $# -eq 0 ]; then
    show_usage
    exit 1
fi

COMMAND=$1
shift

# Parse options
USE_DOCKER=false
DOCKER_ARGS=""

while [ $# -gt 0 ]; do
    case "$1" in
        --port=*)
            PORT="${1#*=}"
            shift
            ;;
        --port)
            PORT="$2"
            shift 2
            ;;
        --mode=*)
            MODE="${1#*=}"
            shift
            ;;
        --mode)
            MODE="$2"
            shift 2
            ;;
        --docker)
            USE_DOCKER=true
            shift
            ;;
        --log-level=*)
            LOG_LEVEL="${1#*=}"
            shift
            ;;
        --log-level)
            LOG_LEVEL="$2"
            shift 2
            ;;
        --host-dir=*)
            HOST_PROJECT_DIR="${1#*=}"
            shift
            ;;
        --host-dir)
            HOST_PROJECT_DIR="$2"
            shift 2
            ;;
        *)
            echo "Unknown option: $1"
            show_usage
            exit 1
            ;;
    esac
done

# Function to get the Docker compose service name
get_service_name() {
    local mode=$1
    if [ "$mode" = "http" ]; then
        echo "mcp-http"
    elif [ "$mode" = "stdio" ]; then
        echo "mcp-stdio"
    else
        echo "Unknown mode: $mode"
        exit 1
    fi
}

# Execute a command
case "$COMMAND" in
    # Start the server
    start)
        if [ "$USE_DOCKER" = true ]; then
            echo "Starting MCP server in Docker ($MODE mode)..."
            export HOST_PROJECT_DIR="$HOST_PROJECT_DIR"
            docker-compose -f "$DOCKER_COMPOSE" up -d "$(get_service_name $MODE)"
            echo "Server started at http://localhost:$PORT"
        else
            echo "Starting MCP server natively..."
            if [ "$MODE" = "http" ]; then
                python3 server_mcp.py --port "$PORT" --log-level "$LOG_LEVEL" &
                echo "Server started at http://localhost:$PORT"
                echo $! > .server.pid
            elif [ "$MODE" = "stdio" ]; then
                python3 stdio_mcp.py
            else
                echo "Unknown mode: $MODE"
                exit 1
            fi
        fi
        ;;

    # Stop the server
    stop)
        if [ "$USE_DOCKER" = true ]; then
            echo "Stopping MCP server in Docker..."
            docker-compose -f "$DOCKER_COMPOSE" down
            echo "Server stopped"
        else
            echo "Stopping MCP server natively..."
            if [ -f .server.pid ]; then
                kill -15 $(cat .server.pid) 2>/dev/null || true
                rm .server.pid
                echo "Server stopped"
            else
                echo "No running server found"
            fi
        fi
        ;;

    # Restart the server
    restart)
        $0 stop "$@"
        sleep 2
        $0 start "$@"
        ;;

    # Show server status
    status)
        if [ "$USE_DOCKER" = true ]; then
            echo "MCP server status (Docker):"
            docker-compose -f "$DOCKER_COMPOSE" ps
        else
            echo "MCP server status (native):"
            if [ -f .server.pid ] && ps -p $(cat .server.pid) > /dev/null; then
                echo "Server is running with PID $(cat .server.pid)"
            else
                echo "Server is not running"
            fi
        fi
        ;;

    # Show server logs
    logs)
        if [ "$USE_DOCKER" = true ]; then
            echo "MCP server logs (Docker):"
            if [ "$MODE" = "http" ] || [ "$MODE" = "stdio" ]; then
                docker-compose -f "$DOCKER_COMPOSE" logs "$(get_service_name $MODE)"
            else
                docker-compose -f "$DOCKER_COMPOSE" logs
            fi
        else
            echo "MCP server logs (native):"
            if [ -f server.log ]; then
                tail -n 100 server.log
            else
                echo "No log file found"
            fi
        fi
        ;;

    # Build Docker image
    build)
        echo "Building Docker image..."
        docker-compose -f "$DOCKER_COMPOSE" build
        echo "Build complete"
        ;;

    # Open a shell in the container
    shell)
        if [ "$USE_DOCKER" = true ]; then
            echo "Opening shell in Docker container..."
            if [ "$MODE" = "http" ] || [ "$MODE" = "stdio" ]; then
                docker-compose -f "$DOCKER_COMPOSE" exec "$(get_service_name $MODE)" /bin/bash
            else
                echo "Please specify --mode=http or --mode=stdio"
                exit 1
            fi
        else
            echo "Shell command is only available in Docker mode"
            exit 1
        fi
        ;;

    # Show usage for unknown commands
    *)
        echo "Unknown command: $COMMAND"
        show_usage
        exit 1
        ;;
esac 