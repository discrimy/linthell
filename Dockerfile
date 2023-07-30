FROM python:3.7-slim as base

RUN apt-get update && \
    apt-get install git curl -y && \
    # Install poetry outside venv so poetry and linthell deps woun't be messed up
    pip install poetry==1.5.1 --no-cache

RUN python -m venv /opt/venv
ENV VIRTUAL_ENV=/opt/venv
ENV PATH=$VIRTUAL_ENV/bin:$PATH

COPY pyproject.toml poetry.lock /app/
WORKDIR /app/
RUN poetry install --no-dev


FROM base as ci
RUN poetry install 

FROM base as dev
# Example how to share same runtime base image, but use different tools in different cases
# (do not mix dev and runtime deps there)
RUN apt-get update && apt-get install wget -y && poetry install 