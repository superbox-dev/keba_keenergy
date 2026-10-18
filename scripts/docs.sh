#!/usr/bin/env bash

set -e

cd "$(dirname "$0")/.."

mode="${1:-build}"

if [[ "$mode" != "build" && "$mode" != "start" ]]; then
  echo "Usage: $0 [build|start]" >&2
  exit 1
fi

./scripts/generate-docs.py
npm --prefix website ci --prefer-offline --no-audit --no-fund

if [[ "$mode" == "build" ]]; then
  npm --prefix website run typecheck
fi

npm --prefix website run docusaurus -- "$mode"
