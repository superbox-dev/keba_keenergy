#!/usr/bin/env bash

set -e

cd "$(dirname "$0")/.."

uv sync --locked --all-extras --dev
uv run pre-commit install
