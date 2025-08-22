#!/usr/bin/env bash

set -e

cd "$(dirname "$0")/.."

export PYTHONPATH="${PYTHONPATH}:${PWD}/custom_components"

# Start Home Assistant
uv run hass --config "${PWD}/config" --debug
