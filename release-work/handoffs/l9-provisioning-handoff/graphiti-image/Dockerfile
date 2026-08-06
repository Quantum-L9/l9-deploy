# Container image for l9-graphiti-memory (l9-memory-server MCP + worker).
# Commit this at the ROOT of Quantum-L9/l9-graphiti-memory. See ./README.md.
FROM python:3.12-slim AS build
WORKDIR /src
COPY . .
# Install the package with the server + active-memory (Redis) extras into a venv.
RUN python -m venv /opt/venv \
 && /opt/venv/bin/pip install --no-cache-dir --upgrade pip \
 && /opt/venv/bin/pip install --no-cache-dir ".[server,active]"

FROM python:3.12-slim AS runtime
# Runtime deps for the SQLite backup toolchain used by the deploy backup step.
RUN apt-get update \
 && apt-get install -y --no-install-recommends sqlite3 \
 && rm -rf /var/lib/apt/lists/*
COPY --from=build /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH" \
    L9_MEMORY_DB_PATH="/var/lib/l9-memory/memory.db"
# Non-root user; canonical SQLite store on a persistent volume.
RUN useradd --system --uid 10001 --home-dir /var/lib/l9-memory --create-home l9memory \
 && chown -R l9memory:l9memory /var/lib/l9-memory
USER l9memory
WORKDIR /var/lib/l9-memory
VOLUME ["/var/lib/l9-memory"]
EXPOSE 8200
# /healthz returns 200 when health is complete (503 otherwise).
HEALTHCHECK --interval=15s --timeout=5s --start-period=30s --retries=5 \
  CMD python -c "import urllib.request,sys; sys.exit(0 if urllib.request.urlopen('http://127.0.0.1:8200/healthz').status==200 else 1)"
# HTTP transport bound to all interfaces (auth tokens injected at runtime via the
# deploy-render env file; the server requires auth when not on loopback).
ENTRYPOINT ["l9-memory-server"]
CMD ["--transport", "http", "--host", "0.0.0.0", "--port", "8200"]
