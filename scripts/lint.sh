#!/usr/bin/env bash

set -e

cd "$(dirname "$0")/.."

uv run ruff format --check
uv run ruff check --fix
uv run ty check
uv run yamllint .
uv run rumdl check --fix
