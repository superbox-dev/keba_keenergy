# Tests

- Every new code path needs a test
- Mock HTTP with the `fake_api` fixture (`tests/conftest.py`)
  - responses in `tests/fixtures/` as JSON, exactly as the Web HMI returns them
    - `common/` for every setup, `single_device/` and `multiple_devices/` per device
    - only `fake_api` loads them, never on import
    - every test loads its device first: `fake_api.load_device("multiple_devices")` or `"single_device"`,
      `init_integration` loads `multiple_devices`
    - variants derived in the tests from `fake_api.data` / `fake_api.fixed_data` with `replace_values()` /
      `replace_attributes()`, never as another JSON file, their values as `dict` in `tests/const.py` or `_data.py`
  - `fake_api.setup_integration()` sets up the device with its `data`, or with own `fake_api.responses`
    (`fake_api.setup_responses(...)` for the setup and the updates), every response must be read
  - other values read on setup with `fake_api.fixed_data`
  - `init_integration` for the setup of the device without own responses
- Config entry and its ID from `mock_config_entry`, or from `init_integration` after its setup
- Variants as fixtures with a default value, overridden by `parametrize` (`entry_data`, `entry_options`)
- Assert entities, devices and issues with snapshots in `tests/snapshots/`
  - entities of a platform with `snapshot_platform()`, only this platform set up (`fake_api.platforms`), with
    `entity_registry_enabled_by_default`
- Translated texts in both languages: `pytest.mark.parametrize("language", ["de", "en"])`, the test sets
  `hass.config.language` before the setup
- New entity:
  - add the values to the responses in `tests/fixtures/`
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
  - every error test fixes the cause and finishes the flow (`CREATE_ENTRY`, `reauth_successful`,
    `reconfigure_successful`)
- Failed updates: entities unavailable, the outage in the log (`caplog`), after the fix available again and the
  recovery in the log
- `pytest.mark.parametrize` with `ids=` naming each case
- Constants of a test module in a module with its name and `_data.py` (`test_api.py` → `test_api_data.py`)
  - shared by several test modules: `tests/const.py`
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
