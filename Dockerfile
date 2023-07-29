FROM python:3.7-slim as base

RUN apt-get update && \
    apt-get install git curl -y

COPY pyproject.toml poetry.lock /app/
WORKDIR /app/
RUN pip install poetry==1.5.1 --no-cache && \
    poetry install


FROM base as ci

FROM base as dev
# Example how to share same runtime base image, but use different tools in different cases
# (do not mix dev and runtime deps there)
RUN apt-get update && apt-get install wget -y