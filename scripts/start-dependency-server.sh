#!/bin/bash

# Script to start the dependency analysis server with cancel feature and custom root support
#
# Usage:
#   ./start-dependency-server.sh [--root=<path>] [--port=<port>]

PORT=8000
ROOT_DIR=""

# Check for custom port
if [[ "$1" == "--port="* ]]; then
  PORT="${1#*=}"
fi

# Check for custom root directory
if [[ "$1" == "--root="* ]]; then
  ROOT_DIR="${1#*=}"
elif [[ "$2" == "--root="* ]]; then
  ROOT_DIR="${2#*=}"
fi

# Check if there's already an HTTP server running on the port
echo "Checking for existing HTTP servers on port $PORT..."
if command -v lsof &> /dev/null; then
  EXISTING_PID=$(lsof -ti:$PORT)
  if [ ! -z "$EXISTING_PID" ]; then
    echo "Killing existing server (PID: $EXISTING_PID)..."
    kill -9 $EXISTING_PID
  fi
fi

echo "Starting dependency analysis server with run/cancel capability..."
echo "Access the visualization at: http://localhost:$PORT/dependency-visualizer.html"
echo "Features:"
echo "  • Run dependency analysis directly from the UI"
echo "  • Cancel running analysis with the stop button"
echo "  • Specify custom project root directory"
echo "  • Real-time status updates"
echo "  • Interactive graph visualization"

# Auto-detect project root if not specified
if [ -z "$ROOT_DIR" ]; then
  echo "Auto-detecting project root directory"
  
  # Start at the current directory
  DIR=$(pwd)
  
  # Go up the directory tree until we find a .git folder or reach the root
  while [ "$DIR" != "/" ]; do
    if [ -d "$DIR/.git" ]; then
      ROOT_DIR="$DIR"
      echo "Detected project root at: $ROOT_DIR (found marker: .git)"
      break
    fi
    DIR=$(dirname "$DIR")
  done
  
  # If we couldn't find a project root, use the current directory
  if [ -z "$ROOT_DIR" ]; then
    ROOT_DIR=$(pwd)
  fi
fi

# Find the analysis script
ANALYSIS_SCRIPT="$ROOT_DIR/dependency-analysis/scripts/enhanced-dependency-analysis.cjs"

echo "Project root: $ROOT_DIR"
echo "Analysis script: $ANALYSIS_SCRIPT"
echo "Server port: $PORT"

# Go to the project root for serving
cd "$ROOT_DIR"

# Start the Python server (with Flask if available, otherwise simple HTTP server)
echo "Serving dependency analysis at http://localhost:$PORT"
echo "Access the visualization at http://localhost:$PORT/dependency-visualizer.html"
echo "Use Ctrl+C to stop"

# Check if the project has a Python server script
if [ -f "dependency-analysis/server.py" ]; then
  CMD="python3 dependency-analysis/server.py --port=$PORT --root=$ROOT_DIR --script=$ANALYSIS_SCRIPT"
  $CMD
else
  # Fall back to basic HTTP server
  python3 -m http.server $PORT
fi 