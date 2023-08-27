FROM python:3.7-slim as base

RUN apt-get update && \
    apt-get install git curl -y && \
    # Install poetry globally so poetry and linthell deps won't be messed up
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
RUN apt-get update && apt-get install wget jq -y
# Preinstall vscode extensions
COPY .devcontainer/ /app/.devcontainer/
ARG VSCODE_VERSION=2ccd690cbff1569e4a83d7c43d45101f817401dc
RUN bash .devcontainer/preinstall-vscode-extensions.sh $VSCODE_VERSION /app/.devcontainer/devcontainer.json

# Install dev deps
RUN poetry install
