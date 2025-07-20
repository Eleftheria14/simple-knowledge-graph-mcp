FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install UV
RUN pip install uv

# Copy project files
COPY pyproject.toml .
COPY requirements.txt .
COPY src/ ./src/
COPY .env.example .env

# Install dependencies
RUN uv pip install --system -r requirements.txt

# Create ChromaDB directory
RUN mkdir -p /app/chroma_db

# Set Python path to include src
ENV PYTHONPATH=/app/src

# Expose port
EXPOSE 3001

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:3001/mcp/ || exit 1

# Start HTTP server
CMD ["python", "src/server/main.py", "--http"]