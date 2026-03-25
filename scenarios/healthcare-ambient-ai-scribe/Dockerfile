# ================================================================
# Ambient AI Scribe — G-PRE-04 Compliant Dockerfile
# ================================================================
# Multi-Stage Build | Non-Root | No Secrets | Slim Base
#
# G-PRE-04 Compliance:
#   P1: USER appuser (Non-Root)          → runAsNonRoot: true
#   P4: No secrets in ENV/COPY           → .dockerignore excludes .env
#   P5: python:3.11-slim base            → minimal attack surface
#   P2, P3, P6: enforced in K8s manifest → deployment.yaml
#
# Traceability (DP2):
#   - OCI labels link image to source code and version
#   - Image tagged with Commit-SHA in CI pipeline (Phase 10)
# ================================================================

# --- Stage 1: BUILDER (discarded after build) ---
FROM python:3.11-slim AS builder

WORKDIR /app

COPY app/requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# --- Stage 2: RUNTIME (final image) ---
FROM python:3.11-slim

# OCI Labels for traceability (DP2)
LABEL org.opencontainers.image.title="Ambient AI Scribe" \
      org.opencontainers.image.description="Healthcare PoC — GenAIOps Quality Gate Reference Architecture" \
      org.opencontainers.image.source="https://github.com/MustDemir/genaiops-compliance-gates" \
      org.opencontainers.image.authors="Mustafa Demir" \
      org.opencontainers.image.licenses="CC-BY-NC-4.0"

# Non-sensitive environment variables only (G-PRE-04 P4)
ENV APP_ENV=production \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Copy only installed packages from builder (no pip, no cache, no build tools)
COPY --from=builder /usr/local/lib/python3.11/site-packages \
                    /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin/uvicorn \
                    /usr/local/bin/uvicorn

# Create non-root user (G-PRE-04 P1)
RUN groupadd -r appuser && useradd -r -g appuser appuser && \
    chown -R appuser:appuser /app

# Copy application code (owned by appuser)
COPY --chown=appuser:appuser app/ .

# Switch to non-root user (G-PRE-04 P1)
USER appuser

# Port 8080: non-privileged (ports < 1024 require root)
EXPOSE 8080

# Exec-form for graceful shutdown (PID 1 receives SIGTERM)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
