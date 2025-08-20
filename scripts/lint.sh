#!/usr/bin/env bash

set -e

cd "$(dirname "$0")/.."

uv run black .
uv run mypy .
uv run ruff check . --fix
uv run yamllint .
uv run rumdl check . --fix
