# syntax=docker/dockerfile:1
# Explicit Python minor version; rebuild regularly for OS/security updates.
FROM python:3.15-slim AS builder
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PYTHONPATH=/app/src
WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY src/ src/
COPY sql/ sql/
COPY config/ config/
COPY docs/ docs/
RUN python -m solar_grid build --output /tmp/solar-artifacts --publish-snapshot

# Only the generated, public demo is shipped; no ML dependencies or input credentials.
FROM python:3.15-slim AS runtime
RUN useradd --uid 10001 --create-home --shell /usr/sbin/nologin app
WORKDIR /site
COPY --from=builder --chown=10001:10001 /app/docs/ ./
USER 10001
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/data.json', timeout=2)"
CMD ["python", "-m", "http.server", "8000", "--bind", "0.0.0.0", "--directory", "/site"]
