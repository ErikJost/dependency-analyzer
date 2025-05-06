FROM python:3.10-slim

# Install essential tools and setup Node.js from NodeSource repo
RUN apt-get update && apt-get install -y \
    curl \
    git \
    gnupg \
    && rm -rf /var/lib/apt/lists/*

# Add NodeSource repository and install modern Node.js
RUN curl -fsSL https://deb.nodesource.com/setup_18.x | bash - \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/*

# Update to a compatible npm version
RUN npm install -g npm@8

# Set working directory for the MCP server
WORKDIR /app

# Copy dependency files first for better layer caching
COPY package*.json ./
COPY requirements.txt ./

# Install dependencies for the MCP server
# Python dependencies for server, Node.js dependencies for analysis
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir psutil
RUN npm install

# Copy application code
# This includes the MCP API implementation and analysis tools
COPY . .

# Create directories for projects and analysis results
# These will be used by the MCP server to store data
RUN mkdir -p /app/projects /app/analysis /app/config

# Expose the port for the MCP server (HTTP mode)
EXPOSE 8000

# Set environment variables for the MCP server
ENV PORT=8000
ENV PROJECTS_DIR=/app/projects
ENV ANALYSIS_DIR=/app/analysis
ENV CONFIG_DIR=/app/config
ENV MCP_MODE=http
ENV LOG_LEVEL=DEBUG

# Add health check for HTTP mode
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:${PORT}/api/health || exit 1

# Create a wrapper script to directly use the appropriate server implementations
RUN echo '#!/bin/bash\n\
echo "Starting MCP server in $MCP_MODE mode"\n\
if [ "$MCP_MODE" = "stdio" ]; then\n\
    # Use stdio mode directly\n\
    exec python3 stdio_mcp.py\n\
else\n\
    # Use HTTP mode directly\n\
    exec python3 server_mcp.py --port $PORT\n\
fi' > /app/entrypoint.sh && chmod +x /app/entrypoint.sh

# Set the entry point to the wrapper script
ENTRYPOINT ["/app/entrypoint.sh"] 