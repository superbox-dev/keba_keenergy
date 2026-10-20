# Tests

- Every new code path needs a test
- Mock HTTP with the `fake_api` fixture (`tests/conftest.py`), responses in `tests/api_data.py`
- Assert entities with snapshots in `tests/snapshots/`
- New entity:
  - add the values to the responses in `tests/api_data.py`
  - regenerate the snapshots and review the new entities
- Use `hass_storage` for stored data, patch `dt_util.now` for date-dependent values
- Test only through Home Assistant:
  - exception: static checks of files (e.g. `test_translations.py`), with `_`-prefixed helpers in the test module
  - never call, patch or inspect `_`-prefixed methods or attributes of the integration
  - never patch the API library, mock its HTTP requests instead
  - set up the integration and drive it through the mocked HTTP responses
  - call actions (`hass.services.async_call`) instead of entity methods
  - trigger updates with `coordinator.async_refresh()` and debounced writes with `async_fire_time_changed()`
  - assert entity states, `ConfigEntryState`, the device registry or the requests
- `pytest.mark.parametrize` with `ids=` naming each case
- Constants of a test module in a module with its name and `_data.py` (`test_api.py` → `test_api_data.py`)
  - shared by several test modules: `tests/api_data.py`
- Helper functions that only check (no return value) start with `assert_`
  - helpers that return a value and only assert to narrow types keep their name
  - shared by several test modules: `tests/asserts.py`, registered with `pytest.register_assert_rewrite()` in
    `tests/conftest.py`
