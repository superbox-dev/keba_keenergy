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
  - never call, patch or inspect `_`-prefixed methods or attributes of the integration, or the API library
  - set up the integration and drive it through the mocked HTTP responses
  - call actions (`hass.services.async_call`) instead of entity methods
  - trigger updates with `coordinator.async_refresh()` and debounced writes with `async_fire_time_changed()`
  - assert entity states, `ConfigEntryState`, the device registry or the requests
