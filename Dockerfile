# Multi-stage build for Aegis AWS Infrastructure Automation Tool
FROM python:3.11-slim as builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt


# Final stage
FROM python:3.11-slim

WORKDIR /app

# Install AWS CLI for debugging (optional)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Copy Python dependencies from builder
COPY --from=builder /root/.local /root/.local

# Set PATH for pip installations
ENV PATH=/root/.local/bin:$PATH \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Copy project files
COPY . .

# Create non-root user for security
RUN useradd -m -u 1000 aegis && chown -R aegis:aegis /app
USER aegis

# Volume for AWS credentials
VOLUME ["/home/aegis/.aws"]

# Health check - verify Python environment
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import boto3; print('AWS SDK ready')" || exit 1

# Default command - provision infrastructure
ENTRYPOINT ["python", "main.py"]
CMD ["--help"]
