FROM python:3.7-slim

RUN apt-get update && \
    apt-get install git curl -y

COPY pyproject.toml poetry.lock /app/
WORKDIR /app/
RUN pip install poetry==1.5.1 --no-cache && \
    poetry install