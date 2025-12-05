# Build stage
FROM python:3.11-slim AS build
WORKDIR /app

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

RUN useradd -r -u 1001 -m builder && chown -R builder:builder /app
USER builder

COPY --chown=builder:builder requirements.txt requirements-dev.txt ./
RUN pip install --no-cache-dir --user -r requirements.txt -r requirements-dev.txt

COPY --chown=builder:builder . .
RUN python -m pytest -q

# Runtime stage
FROM python:3.11-slim

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    curl \
    libcap2-bin \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

RUN useradd -r -u 1001 -m -d /app appuser

WORKDIR /app

COPY --from=build --chown=appuser:appuser /home/builder/.local /home/appuser/.local
COPY --from=build --chown=appuser:appuser /app/app ./app
COPY --from=build --chown=appuser:appuser /app/mypy.ini ./
COPY --from=build --chown=appuser:appuser /app/.env.example ./

ENV PATH="/home/appuser/.local/bin:${PATH}"
ENV PYTHONPATH="/app"

RUN chmod -R 755 /app && \
    chmod 644 /app/.env.example && \
    chown -R appuser:appuser /app

RUN mkdir -p /tmp/app && chown -R appuser:appuser /tmp/app

RUN if command -v setcap >/dev/null 2>&1; then \
        setcap -r /usr/local/bin/python3.11 || echo "setcap failed, continuing..."; \
    else \
        echo "setcap not found, skipping..."; \
    fi

HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8001/health || exit 1

USER appuser

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

EXPOSE 8001

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8001"]
