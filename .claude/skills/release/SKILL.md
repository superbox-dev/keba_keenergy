---
name: release
description: Release or pre-release the integration (version bump, changelog, tag). Use when asked to release, pre-release, tag or bump the version.
---

# Release

- Version from the changelog: breaking → major, `Added`/`Changed` → minor, else patch
- Ask before pushing, show version, branch and tag

1. On `develop`: set the version in `pyproject.toml` and `manifest.json`, run `uv lock`
   - **always** identical in both files, `uv.lock` and the tag (without `v`), also for pre-releases
2. `CHANGELOG.md`, use the `changelog` skill:
   - pre-release `vX.Y.ZbN`: entries stay under `## [Unreleased]`
   - release `vX.Y.Z`: `## [Unreleased]` becomes `## [X.Y.Z] - YYYY-MM-DD`
3. Commit on `develop`
4. Pre-release: tag `develop`, push `develop` and the tag
5. Release:
   - pre-release `keba_keenergy_api` requirement: ask first
   - merge `develop` into `main`, tag `main`, push `main`, `develop` and the tag
