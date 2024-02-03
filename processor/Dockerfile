FROM python:3.11-slim as builder

ENV PIP_DEFAULT_TIMEOUT=100 \
    # Allow statements and log messages to immediately appear
    PYTHONUNBUFFERED=1 \
    # disable a pip version check to reduce run-time & log-spam
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    # cache is useless in docker image, so disable to reduce image size
    PIP_NO_CACHE_DIR=1

ARG POETRY_VERSION=1.7.1

WORKDIR /app

COPY pyproject.toml ./

RUN pip install "poetry==$POETRY_VERSION" \
    && poetry config virtualenvs.create false \
    && poetry install --no-root --no-dev \
    && poetry export -f requirements.txt -o requirements.txt


### Final stage - to reduce image size
FROM python:3.11-slim as final

WORKDIR /app

COPY --from=builder /app/requirements.txt .

RUN set -ex \
    # Security - Upgrade the package index and install security upgrades
    && apt-get update \
    && apt-get upgrade -y \
    # Install dependencies
    && pip install --no-cache-dir -r requirements.txt \
    # Clean up after upgrading - save space in the docker image
    && apt-get autoremove -y \
    && apt-get clean -y \
    && rm -rf /var/lib/apt/lists/*

ENV PYTHONPATH=/app

COPY . .

CMD ["python", "kafka/consumer.py"]