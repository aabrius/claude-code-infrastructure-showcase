# FastMCP Cloud Run Deployment
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN useradd -m -u 1000 mcp-user

# Set working directory
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir fastmcp>=1.0.0

# Copy application code
COPY --chown=mcp-user:mcp-user applications/mcp-server/ ./applications/mcp-server/
COPY --chown=mcp-user:mcp-user packages/ ./packages/
COPY --chown=mcp-user:mcp-user config/ ./config/

# Create necessary directories
RUN mkdir -p /app/logs /app/cache && \
    chown -R mcp-user:mcp-user /app

# Switch to non-root user
USER mcp-user

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV MCP_TRANSPORT=http
ENV PORT=8080

# Expose port
EXPOSE 8080

# Run FastMCP server with HTTP transport
CMD ["python", "applications/mcp-server/fastmcp_server.py"]