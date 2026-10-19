# CLAUDE.md

Home Assistant custom integration (HACS) for heat pumps with a KEBA KeEnergy control unit (Web HMI, local polling),
with all device access going through the separate PyPI library `keba_keenergy_api`.

## Commands

- Use `uv`, always via `uv run`
- Setup: `./scripts/setup.sh`

```bash
uv run ruff format                   # format (lint.sh only checks)
./scripts/lint.sh                    # all linters and type checks
uv run pytest                        # tests + coverage
uv run pytest --snapshot-update -n 0 # regenerate snapshots (serial only), then review the diff
./scripts/develop.sh                 # start a local Home Assistant instance with ./config
./scripts/docs.sh                    # docs (Docusaurus, needs Node.js)
./scripts/docs.sh start              # docs with live reload
```

Before finishing a change, run all of them except the snapshot update, `develop.sh` and the live reload.

## Rules

- **No breaking changes** for installations: never change what Home Assistant stores or users reference
  (IDs, keys, option defaults)
  - rename entity `key`s only via `new_key` / `ref_key`
- No deprecated Home Assistant APIs
- Type annotations also for local variables
- Every `.py` file starts with (after the shebang of an executable script):

  ```python
  # Copyright 2026 Michael Hacker
  # SPDX-License-Identifier: Apache-2.0
  ```

- No new lint/type suppressions or `# pragma: no cover`, fix or test the code
  - only exception: `# noqa: ARG00x` in required signatures
- No real credentials, serial numbers or IP addresses, use the fake data in `tests/api_data.py`
- Missing device endpoints or values belong in `keba_keenergy_api`
- Limited flash writes: write only changed values, only via the coordinator write methods, debounce fast-changing values
- `strings.json` and `translations/en.json` identical, `translations/de.json` with the same keys
- Never edit generated files (`coverage-badge.svg`) or `config/` (except `config/configuration.yaml`)
- **Never edit `CLAUDE.md` files or `.claude/skills/` on your own**, only when asked
  - if a change conflicts with them, stop and ask

## Architecture

- Follow the Home Assistant integration conventions, code in `custom_components/keba_keenergy/`

## Quality scale

- Goal: every applicable rule of the [integration quality scale](https://contributors.home-assistant.io/core/quality-scale/),
  audit with the `quality-scale` skill
- `entity-device-class`: use a device class wherever one applies
  - `ENUM` needs `options` and state translations under `entity.<platform>.<key>.state`
- `entity-category`: `EntityCategory.DIAGNOSTIC` for diagnostic entities
- `entity-disabled-by-default`: rarely needed entities get `entity_registry_enabled_default=False`
- `log-when-unavailable`: failed updates raise `UpdateFailed`, the coordinator logs the outage once
- `parallel-updates`: every platform sets `PARALLEL_UPDATES`
- `stale-devices`: device identifiers always come from `get_device_identifier()`, otherwise devices with entities
  are removed
- The coordinator gets `config_entry` explicitly
- The options flow aborts while the integration is not loaded (`options_not_ready`)

## Documentation

- Update `website/content/index.md` when entities, options, actions or behaviour change
- Keep the `<!--start-…-->` / `<!--end-…-->` markers in `README.md`, `CONTRIBUTING.md` and `CHANGELOG.md`
- Keep `README.md` short (install, links to the sections), details go to `website/content/index.md`
- Images are in `assets/` (also used by `README.md`)

## Changelog, versions and git

- Every user-visible change gets an entry under `## [Unreleased]` in `CHANGELOG.md`, use the `changelog` skill
- Version: only change it when asked, use the `release` skill
- `keba_keenergy_api` requirement is in `pyproject.toml` and `manifest.json`, run `uv lock` after changing it
- Work on `develop`
- Only commit or push when asked
