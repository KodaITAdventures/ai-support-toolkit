FROM python:3.13-slim-bookworm AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

RUN apt-get update \
    && apt-get install --yes --no-install-recommends \
        build-essential \
        libcairo2-dev \
        pkg-config \
    && rm --recursive --force /var/lib/apt/lists/*

WORKDIR /build

COPY requirements.txt .

RUN python -m pip install --upgrade pip \
    && python -m pip wheel \
        --wheel-dir /wheels \
        --requirement requirements.txt

FROM python:3.13-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

RUN apt-get update \
    && apt-get install --yes --no-install-recommends \
        fonts-dejavu-core \
        libcairo2 \
    && rm --recursive --force /var/lib/apt/lists/*

RUN groupadd --system app \
    && useradd --system --gid app --home-dir /app app

WORKDIR /app

COPY --from=builder /wheels /wheels

RUN python -m pip install /wheels/* \
    && rm --recursive --force /wheels

COPY --chown=app:app . .

RUN mkdir --parents /data \
    && chown app:app /data \
    && ln --symbolic /data/support_history.db /app/support_history.db

USER app

EXPOSE 8000

VOLUME ["/data"]

HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/', timeout=3)" || exit 1

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "1", "--threads", "4", "--timeout", "120", "--no-control-socket", "--access-logfile", "-", "--error-logfile", "-", "app:app"]
