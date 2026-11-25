#!/usr/bin/env bash

set -e

cd "$(dirname "$0")/.."

tag="$1"

if [[ -z "$tag" && "$GITHUB_REF" == refs/tags/* ]]; then
  tag="$GITHUB_REF"
fi

tag="${tag#refs/tags/}"
tag="${tag#v}"

manifest="custom_components/keba_keenergy/manifest.json"
errors=0

fail() {
  echo "Error: $1" >&2
  errors=$((errors + 1))
}

is_release() {
  [[ "$1" =~ ^[0-9]+\.[0-9]+\.[0-9]+(b[0-9]+)?$ ]]
}

is_stable() {
  [[ "$1" =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]]
}

pyproject_version="$(sed -n '/^\[project\]/,/^\[/{s/^version = "\(.*\)"/\1/p;}' pyproject.toml)"
manifest_version="$(sed -n 's/^ *"version": *"\(.*\)".*/\1/p' "$manifest")"

if [[ -z "$pyproject_version" ]]; then
  fail "No version found in pyproject.toml"
fi

if [[ -z "$manifest_version" ]]; then
  fail "No version found in $manifest"
fi

if [[ "$pyproject_version" != "$manifest_version" ]]; then
  fail "pyproject.toml ($pyproject_version) does not match manifest.json ($manifest_version)"
fi

if [[ -n "$pyproject_version" ]] && ! is_release "$pyproject_version"; then
  fail "Version '$pyproject_version' is not a release (expected X.Y.Z or X.Y.ZbN)"
fi

if [[ -n "$tag" ]]; then
  if ! is_release "$tag"; then
    fail "Tag 'v$tag' is not a release (expected vX.Y.Z or vX.Y.ZbN)"
  elif [[ "$tag" != "$pyproject_version" ]]; then
    fail "Tag ($tag) does not match pyproject.toml ($pyproject_version)"
  fi
fi

if is_stable "$pyproject_version" \
  && ! grep -Eq "^## \[${pyproject_version//./\\.}\] - [0-9]{4}-[0-9]{2}-[0-9]{2}$" CHANGELOG.md; then
  fail "CHANGELOG.md has no entry for $pyproject_version"
fi

if [[ "$errors" -gt 0 ]]; then
  exit 1
fi

echo "Release check passed: $pyproject_version"
