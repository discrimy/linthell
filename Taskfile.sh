#!/bin/bash

set +e

function init {
    echo "Init"
    poetry run pre-commit install
}

function lint {
    echo "Lint"
    poetry run pre-commit run --all
}

function publish() {
    poetry config repositories.pypi "$1"
    poetry config pypi-token.pypi "$2"

    echo "Publish"
    rm -rd dist
    poetry publish --build --repository pypi
}

function ci:before() {
    git config --global --add safe.directory /app
}

function ci:on_pull_request() {
    ci:before
    lint
}

function ci:on_push_main() {
    ci:before
    lint
}

function ci:on_tag_main() {
    local pypi_token="${PYPI_TOKEN:?}"

    ci:before
    publish "https://upload.pypi.org/legacy/" "$pypi_token"
}

function help {
    echo "$0 <task> <args>"
    echo "Tasks:"
    compgen -A function | cat -n
}

TIMEFORMAT="Task completed in %3lR"
time "$@"
