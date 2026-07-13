FROM python:3.12-slim AS builder

ENV PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /build
COPY pyproject.toml ./
COPY src ./src
RUN python -m pip install --prefix=/install .

FROM python:3.12-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app/src

RUN addgroup --system classpath && adduser --system --ingroup classpath classpath
WORKDIR /app
RUN mkdir -p /app/private-data && chown classpath:classpath /app/private-data
COPY --from=builder /install /usr/local
COPY alembic.ini ./alembic.ini
COPY alembic ./alembic
COPY src ./src
USER classpath
EXPOSE 8000
CMD ["uvicorn", "classpath.main:app", "--host", "0.0.0.0", "--port", "8000"]
