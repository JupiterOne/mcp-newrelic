FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Copy project configuration and install dependencies
COPY pyproject.toml .
RUN uv sync

# Copy application code
COPY server.py .
COPY newrelic_mcp/ ./newrelic_mcp/
COPY newrelic-config.json.example .

# Create non-root user and setup directories with proper permissions
RUN useradd -r -s /bin/false mcp && \
    mkdir -p /app/config /home/mcp/.cache && \
    chown -R mcp:mcp /app /home/mcp

USER mcp

# Expose port (if needed for HTTP transport)
EXPOSE 8000

# Default command - can be overridden with docker run
CMD ["uv", "run", "python", "server.py"]