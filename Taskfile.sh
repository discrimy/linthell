#!/bin/bash

function init {
    pre-commit install
}

function lint {
  pre-commit run --all
}

function help {
    echo "$0 <task> <args>"
    echo "Tasks:"
    compgen -A function | cat -n
}

TIMEFORMAT="Task completed in %3lR"
time "$@"
