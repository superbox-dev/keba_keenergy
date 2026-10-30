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

Before finishing a change, run `ruff format`, `lint.sh` and `pytest`, in this order.
`docs.sh` only when `website/`, `README.md`, `CONTRIBUTING.md` or `CHANGELOG.md` changed.

## Rules

- **No breaking changes** for installations: nothing a user notices later and has to fix by hand
  (unique IDs, entity `key`s, device identifiers, config entry data, option keys and defaults, action names and
  fields, removed entities, device classes, units, state classes, enum states)
  - only when asked, then as a major release
  - `key` is the API value name and part of the unique ID, never change it
  - API value renamed in `keba_keenergy_api`: keep `key`, set the new name as `new_key`
  - second entity on the same API value: `key` is the API value, `ref_key` its own name for the unique ID
- No deprecated Home Assistant APIs
- Type annotations also for local variables (not for loop, `with`, `except`, comprehension or unpacking targets)
  - union order, also in `isinstance()`: general before specific types, each alphabetical, containers after
    single types and less nested first, `None` last (`float | int | str`, `Exception | HTTPStatus`,
    `Value | list[Value] | list[list[Value]] | None`)
  - type alias for complex annotations (nested or repeated unions)
- Module-level constants with `Final` (`NAME: Final = ...`)
- Comments as complete sentences with a trailing period
  - planned cleanups as `# TODO: …`, without author or issue link
- `TypedDict` only for JSON data from or to the Web HMI (optional keys as `NotRequired`), `NamedTuple` only for
  small values that are unpacked (points, pairs), otherwise `@dataclass(frozen=True, kw_only=True)`, mutable only
  when needed
- `Enum` for a fixed set of values (modes, states, types, values of the Web HMI), never loose strings or ints
  for them
  - not for open values (names, IDs, numbers) or a one-off choice in a signature (`Literal`)
- Parameters: options keyword-only (after `*`), `/` only for `_`-prefixed helpers
- Credentials, tokens and serial numbers never in log or exception messages, dumps of device or portal data only
  redacted (`async_redact_data(data, TO_REDACT)`)
- New texts in `strings.json`, `translations/en.json` and `translations/de.json`, keys sorted
- Entity names (EN / DE), Home Assistant adds the device name
  - readable form of the `keba_keenergy_api` 3.0 endpoint name, no device name, unit or state
    (`RETURN_TEMPERATURE`: `Return temperature` / `Rücklauftemperatur`)
  - mode before the quantity in EN, after it in DE (`Heating power` / `Leistung Heizen`), sum of all modes
    `Total …` / `… gesamt`
  - qualifiers in parentheses at the end, comma-separated: `(PV surplus)` / `(PV-Überschuss)`, `(normal)` /
    `(Normal)`, `(reduced)` / `(Abgesenkt)`, `(away)` / `(Urlaub)` (like the climate preset), `(mixer)` /
    `(Mischer)`, daily meter values `(today)` / `(heute)`
  - `Target …` / `Soll-…`, actual values without `Current` / `Ist-`
  - thermal energy `… energy` / `Wärmemenge …` (`Kältemenge` for cooling), electrical `… electrical energy` /
    `Elektrische Energie …`
  - `sStatisticalData` operating times `… operating time` / `Laufzeit …`, `operationalData` `Operating hours` /
    `Betriebsstunden`
  - binary sensors only the component or condition, the device class shows the state (`Compressor` / `Kompressor`,
    `PV surplus` / `PV-Überschuss`)
  - DHW as `Hot water` / `Warmwasser`, abbreviations only when common (`COP`, `SPF` / `JAZ`, `PF` / `AZ`, `PV`),
    never those of the Web HMI
  - DE compounds of at most two parts, longer ones as `<quantity> <component>` (`Drehzahl Umwälzpumpe`,
    `Eintrittstemperatur Kompressor`), established terms stay one word (`Vorlauftemperatur`, `Hochdruckschalter`)
- Energy entities like the energy monitor of the Web HMI: accumulated energies from `sStatisticalData`, meters
  (`*_METER_*`) only for power, daily energy and mass flow
  - exception: meters without a usable statistic (`HeatPump` source, `SolarCircuit`, `Photovoltaics`)
  - thermal statistics (`*_THERMAL_ENERGY`, `*_SPF`, `*_PF`) only when the meter of the mode is not deactivated,
    otherwise they are always `0`
- Log messages start with a capital letter, no trailing period, values as `%s` arguments
- Debug logs only for events and decisions the diagnostics do not show (writes, skipped or removed entities and
  devices, read retries), never for data the diagnostics contain (device counts, options, values, message IDs), at
  most one line per update
- Every file follows `.editorconfig`, whether a linter checks it or not
- Style rules apply to new and changed code, existing code only adapted when asked
- Every `.py` file starts with (after the shebang of an executable script, update the end year when editing a
  file, a single year while it equals the start year):

  ```python
  # Copyright 2025-<current year> Michael Hacker
  # SPDX-License-Identifier: Apache-2.0
  ```

- No inline lint/type suppressions, no new ones in the config, no `# pragma: no cover`, fix or test the code
  - only exception: `# noqa: ARG00x` in required signatures
- No real credentials, serial numbers or IP addresses, use the fake data in `tests/api_data.py`
- Missing device endpoints or values belong in `keba_keenergy_api`, stop and ask how to proceed
  - values calculated from existing ones are fine in the integration
- Limited flash writes: write only changed values, only via the coordinator write methods, debounce fast-changing
  values (e.g. temperatures set with a slider)
- No new dependencies (`pyproject.toml`, `manifest.json`, also dev dependencies) without asking first
- `git add` new files, the pre-commit hooks only check tracked files
- Never edit generated files (`coverage-badge.svg`) or `config/` (except `config/configuration.yaml`)
- **Never edit `CLAUDE.md` files or `.claude/skills/` on your own**, only when asked
  - if a change conflicts with them, stop and ask

## Architecture

- Follow the Home Assistant integration conventions, code in `custom_components/keba_keenergy/`
- Helpers are `_`-prefixed methods of the class that uses them (`@staticmethod` if they need no `self`)
  - module-level functions only when shared across classes or modules, for Home Assistant callbacks (action
    handlers, validators), as helpers of module-level Home Assistant functions (`async_setup_entry`) or to build
    the entity descriptions of a platform
- Constants always in `const.py`
  - except what Home Assistant reads from the module itself (`_LOGGER`, `PARALLEL_UPDATES`, `CONFIG_SCHEMA`) and
    the entity descriptions of a platform (`SENSOR_TYPES`, ...)
- Code only needed to keep the keys and states of `keba_keenergy_api` 2.x (no breaking changes) in `legacy.py`,
  also its constants (`SECTIONS`, `LEGACY_STATES`, `get_state()`, `new_key` via `get_data_key()`)
- Class member order: `__init__`, dunder methods, properties, public methods (also Home Assistant overrides)
  grouped by topic, helpers directly below their first caller
  - applies to new methods, existing ones only moved when asked

## Quality scale

- Goal: every applicable rule of the [integration quality scale](https://contributors.home-assistant.io/core/quality-scale/),
  audit with the `quality-scale` skill
- `entity-device-class`: use a device class wherever one applies
  - `ENUM` needs `options` and state translations under `entity.<platform>.<key>.state`
- `entity-category`: `EntityCategory.DIAGNOSTIC` for diagnostic entities
- `entity-disabled-by-default`: `entity_registry_enabled_default=False` for redundant or derived entities, entities
  only for diagnosis or service, or entities only useful for rare setups
- `log-when-unavailable`: failed updates raise `UpdateFailed`, the coordinator logs the outage once
- `parallel-updates`: every platform sets `PARALLEL_UPDATES`
- `stale-devices`: device identifiers always come from `coordinator.device_identifier()`, otherwise devices with
  entities are removed
- The coordinator gets `config_entry` explicitly
- The options flow aborts while the integration is not loaded (`options_not_ready`), it needs the detected devices

## Documentation

- Update `website/content/index.md` when entities, options, actions or behavior change
- Keep the `<!--start-…-->` / `<!--end-…-->` markers in `README.md`, `CONTRIBUTING.md` and `CHANGELOG.md`
- Keep `README.md` short (install, links to the sections), details go to `website/content/index.md`
- Images are in `assets/` (also used by `README.md`)

## Changelog, versions and git

- Every change users notice gets an entry under `## [Unreleased]` in `CHANGELOG.md` (not refactorings, tests, CI,
  `CLAUDE.md` or skills), use the `changelog` skill
- Version: only change it when asked, use the `release` skill
- `keba_keenergy_api` requirement is in `pyproject.toml` and `manifest.json`, run `uv lock` after changing it
- Work on `develop`
- Only commit or push when asked
- Commit message of a change for an issue starts with its number (`#67 Fix sensors that are not in use`)
