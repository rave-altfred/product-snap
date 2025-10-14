# Multi-stage Dockerfile for ProductSnap Backend
FROM python:3.11-slim as base

# Install system dependencies in base layer
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    curl \
    imagemagick \
    libheif-examples \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user in base
RUN useradd -m -u 1000 appuser

WORKDIR /app

# Development stage
FROM base as development

# Copy requirements first (cached layer)
COPY --chown=appuser:appuser requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY --chown=appuser:appuser . .

USER appuser
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

# Production stage
FROM base as production

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .
RUN chown -R appuser:appuser /app

# Remove unnecessary files
RUN find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
RUN find . -type f -name "*.pyc" -delete
RUN rm -rf .git .gitignore .env* tests/ *.md

USER appuser
EXPOSE 8000

# Use production server settings
# Workers configurable via WEB_CONCURRENCY env var (defaults to 1)
# Recommended: 1 worker per 512MB RAM (1 for 512MB, 2 for 1GB, 4 for 2GB)
# Use shell form to enable variable expansion
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers ${WEB_CONCURRENCY:-1}"]
