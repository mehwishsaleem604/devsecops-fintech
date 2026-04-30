# ─────────────────────────────────────────────
# Stage 1: Build Stage
# ─────────────────────────────────────────────
FROM python:3.11-slim AS builder

WORKDIR /build

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
# Install to a specific prefix to make copying easier
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt


# ─────────────────────────────────────────────
# Stage 2: Runtime Stage
# ─────────────────────────────────────────────
FROM python:3.11-slim AS runtime

# Create a non-privileged user
RUN groupadd -r appgroup && useradd -r -g appgroup appuser

WORKDIR /app

# Copy installed dependencies from builder
COPY --from=builder /install /usr/local

# Fix: Copy the entire project context to keep the 'app/' directory structure
# This ensures that 'import app' works in main.py
COPY . /app/

# Set permissions for the app user
RUN chown -R appuser:appgroup /app

# Environment variables
ENV PYTHONUNBUFFERED=1
ENV FLASK_ENV=production
# Add the current directory to PYTHONPATH so main.py can find the app package
ENV PYTHONPATH=/app

USER appuser

EXPOSE 5000

# Updated CMD: If main.py is in the root, use main:app
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "--timeout", "120", "main:app"]

