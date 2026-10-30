# Tests

- Every new code path needs a test
- Mock HTTP with the `fake_api` fixture (`tests/conftest.py`), responses in `tests/api_data.py`
  - set `fake_api.responses` (`get_single_device_responses()`, `get_multiple_devices_responses()`), then
    `fake_api.setup_integration()`, every response must be read
  - config entry via `fake_api.config_entry`, the `config_entry` fixture only when needed before the setup, change
    `data` / `options` with `indirect` parametrization
- Assert entities, devices and issues with snapshots in `tests/snapshots/`
  - entities one snapshot each (`get_platform_states()`, `snapshot(name=state.entity_id)`), with
    `entity_registry_enabled_by_default` and `language` (EN and DE)
- New entity:
  - add the values to the responses in `tests/api_data.py`
  - regenerate the snapshots and review the new entities
- Use `hass_storage` for stored data, set the time with the `freezer` fixture (`freezer.move_to()`), never patch
  `dt_util.now`
- Test only through Home Assistant:
  - exception: static checks of files (e.g. `test_translations.py`), with `_`-prefixed helpers in the test module
  - never call, patch or inspect `_`-prefixed methods or attributes of the integration
  - never patch the API library, mock its HTTP requests instead
  - set up the integration and drive it through the mocked HTTP responses
  - call actions with the helpers in `tests/__init__.py` (`hass.services.async_call`) instead of entity methods
  - trigger updates with `coordinator.async_refresh()`, debounced writes with `fire_debounced_writes()`
  - assert entity states, `ConfigEntryState`, the device registry or the requests (`fake_api.write_requests()`,
    `read_requests()`)
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
- Never wait in real time, advance the time (`freezer`, `async_fire_time_changed()`), no `sleep()`
- Fixtures only in `tests/conftest.py`
- Tests are independent of each other, they run in parallel (`pytest-xdist`) and in any order
- No logic in tests (`if`, loops over cases), use `parametrize` instead
  - except loops that only build test data
