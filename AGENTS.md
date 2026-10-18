# AGENTS.md

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

- **No breaking changes** for existing installations:
  - entity description `key`s (part of the `unique_id`)
  - device identifiers
  - option keys (`CONF_*`) and their default behaviour
  - `translation_key`s
- **Minimum versions**:
  - Python as in `pyproject.toml`, Home Assistant as in `hacs.json`
  - no deprecated Home Assistant APIs
- Code style:
  - line length 120
  - single-line imports
  - full type annotations, including local variables
- Every `.py` file starts with (after the shebang of an executable script):

  ```python
  # Copyright 2026 Michael Hacker
  # SPDX-License-Identifier: Apache-2.0
  ```

- NumPy-style docstrings everywhere, also in tests
- No lint or type suppressions (inline or in config), except the existing ignores in `ruff.toml` and `ty.toml`.
  Fix the code instead
  - only inline exception: `# noqa` for `ARG00x` in required signatures
  - no `# pragma: no cover`, test the code or remove it
- Avoid `cast()`: narrow types with checks that also run at runtime (e.g. `isinstance`) or with generics
- No real credentials, serial numbers or IP addresses, use the fake data in `tests/api_data.py`
- Device access:
  - never call the Web HMI directly
  - missing endpoints or values belong in `keba_keenergy_api`
- The flash memory of the control unit only allows a limited number of writes:
  - only write a value if it differs from the current value
  - debounce values that change quickly (numbers, target temperatures)
- `git add` new files, CI only checks tracked files
- Never edit generated or CI-managed files (`coverage-badge.svg`)
- Never edit `config/`, except `config/configuration.yaml` (local dev instance)

## Architecture

Code lives in `custom_components/keba_keenergy/`.

- `coordinator.py`:
  - `coordinator.data` maps a section (`SectionPrefix`, e.g. `heat_circuit`) to the values of all devices of it
  - `get_value_by_index()` returns the value of one device (and key index) from `coordinator.data`
  - `REQUEST_DATA_GROUPS` lists the requested values per section
  - on setup, `filter_request()` drops values the control unit or software version does not support, and sections
    without devices are not requested
  - the fixed data (`has_*`, `is_*`) is read once on setup and decides which entities are created
  - every section can be polled every n-th update (`scan_interval_tick_<section>` options)
  - sections without a response keep their previous data
  - on `APIError` the update fails and the entities are unavailable
  - on `AuthenticationError` the reauth flow starts
- Writes:
  - always through `coordinator.async_write_data()` / `async_execute_write()`
  - every write is counted per week (stored in `Store`), above `FLASH_WRITE_LIMIT_PER_WEEK` a repair issue
    (`frequent_flash_writes`) warns about the flash memory lifetime
  - entities update `coordinator.data` optimistically (`async_update_value()`)
  - number, climate and water heater writes are debounced (`FLASH_WRITE_DELAY`)
- `__init__.py`:
  - creates the control unit device, all other devices link to it with `via_device_id`
  - registers the actions (`services.py`, `services.yaml`)
- `entity.py`:
  - `_async_setup_entities()` creates one entity per description and device index, if `condition` is met
  - `SECTIONS` maps a section to the `keba_keenergy_api` enum of its values
  - `unique_id` is `<entry unique_id>[_<section>]_<key>[_<key_index + 1>][_<index + 1>]`
  - renaming a `key` creates new entities and orphans the old ones, use `new_key` / `ref_key` instead
- Every platform sets `entity_id` to `<platform>.keba_keenergy_<unique_id>`, do not change this
- `config_flow.py`: user, zeroconf discovery, auth, reauth, reconfigure and options flow
- Translations:
  - `strings.json` and `translations/en.json` must be **identical**
  - `translations/de.json` has the same keys
  - user-visible texts always use `translation_key`
  - exceptions use `translation_domain` and `translation_key` (`exceptions` in `strings.json`)
  - icons are in `icons.json`, never `icon=` in descriptions
    - exception: the existing `icon=` of translation keys that entities with different icons share

## Quality scale

- Goal: every applicable rule of the [integration quality scale](https://contributors.home-assistant.io/core/quality-scale/)
- Not applicable:
  - `entity-event-setup`: entities only use the coordinator
- Open:
  - `dynamic-devices`: devices are only detected on setup, a changed setup needs a reload
- Keep these rules satisfied:
  - `brands`: the brand images are in the `home-assistant/brands` repository (`custom_integrations/keba_keenergy/`)
  - `exception-translations`: exceptions use `translation_domain` and `translation_key`
  - `icon-translations`: icons in `icons.json`
  - `entity-device-class`: use a device class wherever one applies
    - `ENUM` needs `options` and state translations under `entity.<platform>.<key>.state`
  - `entity-category`: `EntityCategory.DIAGNOSTIC` for diagnostic entities
  - `entity-disabled-by-default`: rarely needed entities get `entity_registry_enabled_default=False`
  - `log-when-unavailable`: failed updates raise `UpdateFailed`, the coordinator logs the outage once
  - `parallel-updates`: every platform sets `PARALLEL_UPDATES`
  - `reauthentication-flow` / `reconfiguration-flow`: keep both working
  - `repair-issues`: `frequent_flash_writes`
  - `diagnostics`: `diagnostics.py` redacts the host, the credentials, the serial number and the title
  - `discovery-update-info`: the zeroconf flow updates a changed IPv4 address, a configured hostname is kept
  - `stale-devices`: on setup, devices whose identifier is not in `coordinator.device_identifiers()` are removed
    - device identifiers always come from `get_device_identifier()`, otherwise devices with entities are removed
  - `test-coverage`: 100%, see [Tests](#tests)
- Also keep:
  - the coordinator gets `config_entry` explicitly
  - the options flow aborts while the integration is not loaded (`options_not_ready`)
- Documentation (`website/content/index.md`, see [Documentation](#documentation)) covers:
  - installation parameters, options, removal
  - supported devices, entities, actions, data updates
  - use cases, examples, known limitations, troubleshooting
  - update it when entities, options, actions or behaviour change

## Adding an entity

1. Platform module (e.g. `sensor.py`): add an entity description to the matching section
   - use a `condition` if the value depends on the heat pump setup
2. `strings.json` and all translations: add the name under `entity.<platform>.<key>`
3. `icons.json`: add the icon under `entity.<platform>.<key>`, if it has no device class
4. `coordinator.py`: add the value to `REQUEST_DATA_GROUPS`, if it is not requested yet
5. `website/content/index.md`: add it to the supported functionality
6. Tests: see [Tests](#tests)

## Adding an option

1. `const.py`: add `CONF_*` (and a default)
2. `config_flow.py`: add it to the options schema
3. `strings.json` and all translations: add `data` and `data_description`
4. `website/content/index.md`: add it to the options table

## Documentation

- Docusaurus website in `website/`, deployed to <https://superbox.one> from `main` (`.github/workflows/page.yml`)
- `scripts/generate-docs.py` writes all pages into `website/docs/` (not tracked, run by `scripts/docs.sh`):
  - hand-written pages from `website/content/`
  - donation, contributing and changelog from the `<!--start-…-->` / `<!--end-…-->` markers
    in `README.md`, `CONTRIBUTING.md` and `CHANGELOG.md`, so keep the markers
- `website/content/index.md` is the integration page:
  - sections in the order of the home-assistant.io integration pages
  - examples use the serial number `12345678` of the test data
- Images are in `assets/` (also used by `README.md`)
- `website/static/keba-keenergy/` redirects the URLs of the old MkDocs pages, keep them
- Keep `README.md` short (install, links to the sections), details go to `website/content/index.md`
- Design after home-assistant.io:
  - `website/src/css/custom.css` and the wrapped `website/src/theme/TOC/`
  - the integration card in `website/src/components/ProjectInfo/` reads `manifest.json` and `hacs.json`

## Tests

- **100% test coverage** (lines and branches) is enforced
  - every new code path needs a test
- Warnings fail the tests (`filterwarnings = ["error"]`)
- Errors logged by the integration fail the tests (`fail_on_log_errors`), opt out with
  `@pytest.mark.no_fail_on_keba_errors`
- Mock HTTP with `FakeKebaKeEnergyAPI` (`fake_api` fixture) in `tests/conftest.py` and the responses in
  `tests/api_data.py`:
  - `fake_api.responses` are the responses of the read requests, in order, an `HTTPStatus` fails a request
  - `await fake_api.setup_integration()` registers the requests and sets up the `config_entry`
  - `system_name` and `write_status` change the system name and the status of the write requests
  - `write_requests()`, `read_requests()` and `assert_called_write_with()` check the requests
- Assert the entities with snapshots in `tests/snapshots/`:
  - regenerate them serially (`-n 0`), parallel runs drop snapshots
  - always review the diff
- New entity:
  - add the values to the responses in `tests/api_data.py`
  - regenerate the snapshots and review the new entities
- The `config_entry` fixture is parametrized indirectly with `data` / `options`
- The `language` fixture is parametrized indirectly with the language of Home Assistant
- Use `hass_storage` for stored data, patch `dt_util.now` for date-dependent values
- At most 5 arguments per test: split the test or use the fixtures above
- Test only through Home Assistant:
  - never call, patch or inspect `_`-prefixed methods or attributes, or the API library
  - set up the integration and drive it through the mocked HTTP responses
  - call actions (`hass.services.async_call`) instead of entity methods
  - trigger updates with `coordinator.async_refresh()` and debounced writes with `async_fire_time_changed()`
  - assert entity states, `ConfigEntryState`, the device registry or the requests

## Changelog, versions and git

- `CHANGELOG.md`:
  - every user-visible change gets an entry under `## [Unreleased]`
  - Keep a Changelog format, past tense
  - identifiers in backticks
  - issues as `([Issue #25][issue-25])`, pull requests as `([PR #19][pr-19])`
  - issue and PR links are defined at the end of their release section, not at the bottom
    - a link that an older section already defines is reused, not defined again
  - releases are linked at the bottom, before `<!--end-->`:
    - `[Unreleased]` compares the latest release tag (no pre-release) with `HEAD`
    - each release compares its tag with the previous one
    - the first release links to its release tag
  - the release workflow links the release notes to the section of the tag, so a release needs its section
- Versions:
  - the version is in `pyproject.toml` and `manifest.json`
  - only change it when asked
  - the `keba_keenergy_api` requirement is in both files too
  - run `uv lock` after changing it
- Branches:
  - work on `develop`
  - `main` is the release branch
  - `v*` tags create a GitHub release for HACS, `v*b*` tags a pre-release
- Only commit or push when asked
