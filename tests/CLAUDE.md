# Tests

- Every new code path needs a test
- Mock HTTP with the `fake_api` fixture (`tests/conftest.py`), responses in `tests/api_data.py`
  - set `fake_api.responses` (`get_single_device_responses()`, `get_multiple_devices_responses()`), then
    `fake_api.setup_integration()`, every response must be read
  - `init_integration` for the setup with `get_multiple_devices_responses(MULTIPLE_DEVICES_DATA_RESPONSE)`
- Config entry: `mock_config_entry`, or `init_integration` after its setup
  - only as an argument when the test needs the entry itself (`add_to_hass()`, `state`, `data`), otherwise
    `usefixtures`
  - its ID always as `ENTRY_ID` (`tests/api_data.py`)
- Variants as fixtures with a default value, overridden by `parametrize` (`entry_data`, `entry_options`)
  - `indirect` for fixtures with `params`, e.g. a single language (`language`)
- Assert entities, devices and issues with snapshots in `tests/snapshots/`
  - entities of a platform with `snapshot_platform()`, only this platform set up (`fake_api.platforms`), with
    `entity_registry_enabled_by_default` and `language` (EN and DE)
- New entity:
  - add the values to the responses in `tests/api_data.py`
  - regenerate the snapshots and review the new entities
- Registries with the `entity_registry`, `device_registry` and `issue_registry` fixtures, never `er.async_get()`,
  `dr.async_get()` or `ir.async_get()`
- Use `hass_storage` for stored data
- Time frozen with `pytestmark = pytest.mark.freeze_time(NOW)` in every module that sets up the integration
  - another time as `pytest.mark.freeze_time` of the test or of a case (`pytest.param(..., marks=...)`)
  - never patch `dt_util.now`
- Test only through Home Assistant:
  - exception: static checks of files (e.g. `test_translations.py`), with `_`-prefixed helpers in the test module
  - never call, patch or inspect `_`-prefixed methods or attributes of the integration
  - never patch the API library, mock its HTTP requests instead
  - only patch: `async_setup_entry` with `mock_setup_entry` in config, reauth and reconfigure flow tests
  - drive the integration through the mocked HTTP responses
  - call actions with the helpers in `tests/__init__.py` (`hass.services.async_call`) instead of entity methods
  - trigger updates with `next_update()`, debounced writes with `fire_debounced_writes()` (both `freezer`), never
    through `runtime_data`
  - assert entity states, `ConfigEntryState`, the registries or the requests (`fake_api.write_requests()`,
    `read_requests()`)
- Config flows: `FlowResultType` with `is`, no errors on the first form, `unique_id` of the created entry
- `pytest.mark.parametrize` with `ids=` naming each case
- Constants of a test module in a module with its name and `_data.py` (`test_api.py` → `test_api_data.py`)
  - shared by several test modules: `tests/api_data.py`
- Helper functions that only check (no return value) start with `assert_`
  - helpers that return a value and only assert to narrow types keep their name
  - shared by several test modules: `tests/__init__.py`
- Tests as functions, no test classes
- Error cases next to the tests of the code they check, named `test_<function>_<condition>`
- Every bug fix gets a regression test that fails without the fix
- Exceptions: assert the type and the message (`pytest.raises(..., match=...)` or `error.value`)
- Never wait in real time, advance the time with `freezer`, no `sleep()`
- Fixtures only in `tests/conftest.py`
- Tests are independent of each other, they run in parallel (`pytest-xdist`) and in any order
- No logic in tests (`if`, loops over cases), use `parametrize` instead
  - except loops that only build test data
