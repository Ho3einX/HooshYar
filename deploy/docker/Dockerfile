FROM python:3.11-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /build

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential libpq-dev && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml poetry.lock* ./
RUN pip install --no-cache-dir poetry==1.8.3 && \
    poetry config virtualenvs.create false && \
    poetry install --only main --no-interaction --no-ansi

FROM python:3.11-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN useradd -m -u 10001 appuser
WORKDIR /app

COPY --from=builder /usr/local /usr/local
COPY . /app

RUN chown -R appuser:appuser /app
USER appuser

EXPOSE 8000
CMD ["gunicorn", "-k", "uvicorn.workers.UvicornWorker", "-c", "deploy/docker/gunicorn_conf.py", "app.api.main:app"]
