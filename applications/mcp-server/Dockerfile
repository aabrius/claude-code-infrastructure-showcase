# FastMCP Cloud Run Deployment using uv
# Based on: https://github.com/astral-sh/uv-docker-example

# Use official uv image with Python pre-installed
FROM ghcr.io/astral-sh/uv:python3.11-bookworm-slim

# Setup a non-root user
RUN groupadd --system --gid 999 nonroot \
 && useradd --system --gid 999 --uid 999 --create-home nonroot

# Install the project into `/app`
WORKDIR /app

# Enable bytecode compilation for faster startup
ENV UV_COMPILE_BYTECODE=1

# Copy from the cache instead of linking since it's a mounted volume
ENV UV_LINK_MODE=copy

# Copy package sources first (needed for uv to resolve local deps)
COPY --chown=nonroot:nonroot packages/ ./packages/

# Copy application code with pyproject.toml and uv.lock
COPY --chown=nonroot:nonroot applications/mcp-server/ ./applications/mcp-server/
COPY --chown=nonroot:nonroot config/ ./config/

# Install dependencies using the lockfile
WORKDIR /app/applications/mcp-server
RUN uv sync --frozen --no-dev

# Create necessary directories
RUN mkdir -p /app/logs /app/cache && \
    chown -R nonroot:nonroot /app

# Place executables in the environment at the front of the path
ENV PATH="/app/applications/mcp-server/.venv/bin:$PATH"

# Reset the entrypoint, don't invoke `uv`
ENTRYPOINT []

# Use the non-root user to run our application
USER nonroot

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV MCP_SERVER_PORT=8080
ENV MCP_SERVER_HOST=0.0.0.0

# OAuth settings (MCP_RESOURCE_URI must be set at deploy time)
ENV OAUTH_GATEWAY_URL=https://ag.etus.io

# Note: googleads.yaml should be mounted as a secret at runtime via:
#   --set-secrets "/app/applications/mcp-server/googleads.yaml=google-ads-yaml:latest"

# Set working directory for runtime
WORKDIR /app/applications/mcp-server

# Expose port
EXPOSE 8080

# Run FastMCP server directly using the venv python (no uv needed at runtime)
CMD ["python", "main.py"]
