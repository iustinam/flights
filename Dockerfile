FROM python:3.12-slim

ENV FLIGHTS_BASE_DIR=/mnt/

WORKDIR /app

COPY pyproject.toml .
COPY src/ src/

RUN pip install --no-cache-dir -e .

ENTRYPOINT ["flights"]
