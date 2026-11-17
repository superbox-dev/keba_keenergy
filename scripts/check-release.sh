#!/usr/bin/env bash

set -e

cd "$(dirname "$0")/.."

tag_only=false
tag=""

for arg in "$@"; do
  case "$arg" in
    --tag-only) tag_only=true ;;
    *) tag="$arg" ;;
  esac
done

# Tag from argument, GitHub Actions or the prek pre-push hook
if [[ -z "$tag" ]]; then
  for ref in "$GITHUB_REF" "$PRE_COMMIT_LOCAL_BRANCH"; do
    if [[ "$ref" == refs/tags/* ]]; then
      tag="$ref"
      break
    fi
  done
fi

tag="${tag#refs/tags/}"
tag="${tag#v}"

if [[ "$tag_only" == true && -z "$tag" ]]; then
  exit 0
fi

manifest="custom_components/keba_keenergy/manifest.json"
errors=0

fail() {
  echo "Error: $1" >&2
  errors=$((errors + 1))
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

if [[ -n "$pyproject_version" ]] && ! is_stable "$pyproject_version"; then
  fail "Version '$pyproject_version' is not a stable release (expected X.Y.Z)"
fi

if [[ -n "$tag" ]]; then
  if ! is_stable "$tag"; then
    fail "Tag '$tag' is not a stable release (expected vX.Y.Z)"
  elif [[ "$tag" != "$pyproject_version" ]]; then
    fail "Tag ($tag) does not match pyproject.toml ($pyproject_version)"
  fi
fi

if [[ -n "$pyproject_version" ]] && ! grep -Eq "^## \[?${pyproject_version//./\\.}\]?( |$)" CHANGELOG.md; then
  fail "CHANGELOG.md has no entry for $pyproject_version"
fi

if [[ "$errors" -gt 0 ]]; then
  exit 1
fi

echo "Release check passed: $pyproject_version"
