# ==============================================================================
# SECURE MULTI-STAGE DOCKERFILE
# Architecture: Python 3.12 Slim -> Hardened Unprivileged Non-Root Runtime
# Compliance: CIS Docker Benchmark, NIST SP 800-190 Container Security Guide
# ==============================================================================

# Stage 1: Build & Dependency Resolution Stage
FROM python:3.12-slim AS builder

WORKDIR /build

# Install build-time dependencies safely without caching
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        build-essential \
        curl && \
    rm -rf /var/lib/apt/lists/*

# Copy only dependency definitions first for optimal layer caching
COPY requirements.txt .

# Install dependencies into dedicated prefix
RUN pip install --no-cache-dir --user -r requirements.txt

# ==============================================================================
# Stage 2: Hardened Production Runtime Stage
# ==============================================================================
FROM python:3.12-slim AS runner

# Metadata Labels (Open Containers Initiative - OCI standard)
LABEL org.opencontainers.image.title="Secure Cloud Microservice" \
      org.opencontainers.image.description="Hardened, production-ready microservice with integrated CI/CD security controls" \
      org.opencontainers.image.vendor="Enterprise DevSecOps" \
      org.opencontainers.image.version="1.2.0" \
      org.opencontainers.image.licenses="Apache-2.0"

# Install curl for container health checks and remove package manager caches
RUN apt-get update && \
    apt-get install -y --no-install-recommends curl ca-certificates && \
    rm -rf /var/lib/apt/lists/*

# Create unprivileged system group and user (UID 10001)
RUN groupadd -g 10001 appgroup && \
    useradd -u 10001 -g appgroup -s /sbin/nologin -M appuser

WORKDIR /app

# Copy installed Python packages from builder stage
COPY --from=builder --chown=appuser:appgroup /root/.local /home/appuser/.local
# Copy application source code
COPY --chown=appuser:appgroup src/ /app/src/

# Update PATH to include user packages
ENV PATH="/home/appuser/.local/bin:${PATH}" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=8080 \
    ENVIRONMENT=production

# Switch to unprivileged non-root user
USER appuser

# Expose microservice port
EXPOSE 8080

# Health check configuration adhering to container security standards
HEALTHCHECK --interval=20s --timeout=4s --start-period=5s --retries=3 \
    CMD curl -f http://127.0.0.1:8080/healthz || exit 1

# Entrypoint running production WSGI server
CMD ["python", "-m", "src.app.main"]
