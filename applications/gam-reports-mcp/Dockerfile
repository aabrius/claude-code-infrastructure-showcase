# Use official uv Docker image
FROM ghcr.io/astral-sh/uv:python3.11-bookworm-slim

# Set working directory
WORKDIR /app

# Copy project files
COPY pyproject.toml uv.lock ./
COPY config ./config
COPY core ./core
COPY endpoints ./endpoints
COPY models ./models
COPY server.py search.py ./

# Install dependencies with uv
RUN uv sync --frozen --no-dev

# Add .venv/bin to PATH for direct python access
ENV PATH="/app/.venv/bin:$PATH"

# Expose port
EXPOSE 8080

# Reset ENTRYPOINT to run CMD directly
ENTRYPOINT []

# Run the server
CMD ["python", "server.py"]
