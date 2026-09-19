FROM python:3.11-slim AS requirements

ENV PIP_DEFAULT_TIMEOUT=100 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1

ARG POETRY_VERSION=1.8.5
WORKDIR /build
COPY pyproject.toml ./
RUN pip install "poetry==$POETRY_VERSION" \
    && poetry export --only main --without-hashes --output requirements-production.txt \
    && poetry export --with test --without-hashes --output requirements-development.txt

FROM python:3.11-slim AS runtime

ENV PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1 \
    PYTHONPATH=/app

WORKDIR /app
RUN apt-get update \
    && apt-get upgrade -y \
    && rm -rf /var/lib/apt/lists/*

FROM runtime AS development
COPY --from=requirements /build/requirements-development.txt ./requirements.txt
RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt
COPY src ./src
COPY tests ./tests
EXPOSE 8000
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload", "--log-level", "debug"]

FROM runtime AS production
COPY --from=requirements /build/requirements-production.txt ./requirements.txt
RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt
COPY src ./src
EXPOSE 80
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "80", "--log-level", "info"]
