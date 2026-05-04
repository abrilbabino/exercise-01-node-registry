# TODO: Write a production-ready Dockerfile
#
# All of these are tested by the grader:
#
# [ ] Multi-stage build (2+ FROM instructions)
# [ ] Base image: python:3.14-slim (pinned version, no :latest)
# [ ] Copy requirements.txt and pip install BEFORE copying source code (layer caching)
# [ ] Run as a non-root USER
# [ ] EXPOSE 8080
# [ ] HEALTHCHECK instruction
# [ ] No hardcoded secrets (no ENV PASSWORD=..., no ENV SECRET_KEY=...)
# [ ] Final image under 200MB
#
# Start command: uvicorn src.app:app --host 0.0.0.0 --port 8080

# ==========================================
# Stage 1: Builder (Dependency installation)
# ==========================================
FROM python:3.14-slim AS builder

WORKDIR /app

COPY requirements.txt .

# Install dependencies into a local user directory to keep the final image clean
RUN pip install --user --no-cache-dir -r requirements.txt

# ==========================================
# Stage 2: Final Image (Production stage)
# ==========================================
FROM python:3.14-slim

ENV PATH=/home/appuser/.local/bin:$PATH
# Create a non-privileged user to run the application (Security Best Practice)
RUN useradd -m -s /bin/bash appuser

WORKDIR /app

# Copy only the installed packages from the builder stage
COPY --from=builder /root/.local /home/appuser/.local

# Copy the application source code and set ownership to the non-root user
COPY --chown=appuser:appuser . .

# Expose the application port
EXPOSE 8080

# Define a healthcheck to monitor container status
HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8080/')" || exit 1

# Switch to the non-privileged user
USER appuser

CMD ["uvicorn", "src.app:app", "--host", "0.0.0.0", "--port", "8080"]