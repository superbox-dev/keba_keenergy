#!/usr/bin/env bash

set -e

cd "$(git rev-parse --show-toplevel)"

# stdin: <local ref> <local sha> <remote ref> <remote sha>
while read -r local_ref _ _ _; do
  if [[ "$local_ref" == refs/tags/* ]]; then
    ./scripts/check-release.sh "$local_ref"
  fi
done
