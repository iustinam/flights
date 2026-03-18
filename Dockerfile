FROM python:3.12-slim

ENV FLIGHTS_DATA_DIR=/mnt/data \
    FLIGHTS_REPORT_DIR=/mnt/reports

WORKDIR /app

COPY pyproject.toml .
COPY src/ src/

RUN pip install --no-cache-dir -e .

ENTRYPOINT ["flights"]
