# syntax=docker/dockerfile:1

FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PYTHONPATH=/app

WORKDIR /app

# Runtime library required by NumPy/scikit-learn wheels.
RUN apt-get update \
    && apt-get install -y --no-install-recommends libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Install the repository dependencies first for Docker layer caching.
COPY requirements.txt ./requirements.txt
RUN python -m pip install --upgrade pip \
    && python -m pip install -r requirements.txt \
    && python -m pip install \
        "numpy==2.2.2" \
        "joblib==1.4.2" \
        "scikit-learn==1.6.1"

# Runtime source and model/data assets.
COPY app ./app
COPY data ./data
COPY models ./models

# Keep runtime-generated files outside the image layer.
RUN mkdir -p /app/logs \
    && useradd --create-home --uid 10001 --shell /usr/sbin/nologin mindcare \
    && chown -R mindcare:mindcare /app

USER mindcare

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=30s --retries=3 \
    CMD python -c "import os, urllib.request; port=os.getenv('PORT','8000'); urllib.request.urlopen(f'http://127.0.0.1:{port}/health', timeout=3)" || exit 1

# Uvicorn is already a pinned project dependency. Render supplies PORT.
CMD ["sh", "-c", "exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
