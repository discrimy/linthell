#!/bin/bash

function init {
    poetry run pre-commit install
}

function lint {
    poetry run pre-commit run --all
}

function ci:on_pull_request() {
    whoami
    git config --global --add safe.directory /app
    poetry --version
    git status
    lint
}

function help {
    echo "$0 <task> <args>"
    echo "Tasks:"
    compgen -A function | cat -n
}

TIMEFORMAT="Task completed in %3lR"
time "$@"
