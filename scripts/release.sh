#!/usr/bin/env bash

set -e

cd "$(dirname "$0")/.."

tag="$1"

if [[ ! "$tag" =~ ^v[0-9]+\.[0-9]+\.[0-9]+(b[0-9]+)?$ ]]; then
  echo "Usage: $0 vX.Y.Z[bN]" >&2
  exit 1
fi

# Pre-releases come from develop, stable releases from main
if [[ "$tag" =~ b[0-9]+$ ]]; then
  allowed="develop"
else
  allowed="main"
fi

branch="$(git rev-parse --abbrev-ref HEAD)"

if [[ "$branch" != "$allowed" ]]; then
  echo "Error: $tag must be released from $allowed (current branch: $branch)" >&2
  exit 1
fi

if [[ -n "$(git status --porcelain)" ]]; then
  echo "Error: Working tree is not clean" >&2
  exit 1
fi

git fetch origin --quiet

if [[ "$(git rev-parse HEAD)" != "$(git rev-parse "origin/$branch")" ]]; then
  echo "Error: HEAD is not pushed to origin/$branch" >&2
  exit 1
fi

if git ls-remote --exit-code --tags origin "refs/tags/$tag" > /dev/null 2>&1; then
  echo "Error: Tag $tag already exists on origin" >&2
  exit 1
fi

./scripts/check-release.sh "$tag"

git tag "$tag"
git push origin "$tag"
