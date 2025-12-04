# Use official uv Docker image for fast Python dependency management
FROM ghcr.io/astral-sh/uv:python3.11-bookworm-slim

# Set working directory
WORKDIR /app

# Copy dependency files first for better layer caching
COPY pyproject.toml uv.lock ./

# Install dependencies with uv (frozen lockfile, no dev dependencies)
RUN uv sync --frozen --no-dev

# Copy application code
COPY config ./config
COPY core ./core
COPY endpoints ./endpoints
COPY models ./models
COPY server.py search.py ./

# Set environment variables for Cloud Run best practices
ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PORT=8080 \
    MCP_TRANSPORT=http

# Expose port
EXPOSE 8080

# Health check for load balancers
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8080/health').read()" || exit 1

# Reset ENTRYPOINT to run CMD directly
ENTRYPOINT []

# Run the server with uv (manages virtual environment automatically)
CMD ["uv", "run", "server.py"]
