# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

<!--start-->

### Changed

- Moved the documentation on <https://superbox.one> to Docusaurus, styled after the integration pages of
  Home Assistant, with all information on one page. The old wiki URLs redirect to the new sections.
- Shortened the `README.md` to the installation and moved the details to the documentation.
- Linked the GitHub release notes to the matching section of the changelog.
- Extended the issue templates with the environment and debug logs.
- Moved the static entity icons to `icons.json`. The icons are unchanged, but the entities no longer have an `icon`
  state attribute.
- Wrote the HVAC mode of a heating circuit only if it differs from the current operating mode.
- Translated the error message of failed data updates.

### Fixed

- Fixed the missing state icons of the operating mode sensors since 1.10.0.
- Fixed the away date range being written to the control unit even if it did not change. ([Issue #23][issue-23])

## [1.10.4] - 2026-09-30

### Changed

- Required Home Assistant 2026.9.4 or newer.

### Fixed

- Fixed Home Assistant device registry deprecation warnings by linking the devices to the control unit with
  `via_device_id` instead of `via_device`.
- Fixed an error when opening the options if the control unit has no photovoltaics. ([Issue #66][issue-66])

[issue-66]: https://github.com/superbox-dev/keba_keenergy/issues/66

## [1.10.3] - 2026-07-28

### Fixed

- Required Home Assistant 2026.7.0 or newer, which includes `aiohttp` 3.14 with `encode_basic_auth()`.
  ([Issue #65][issue-65])

[issue-65]: https://github.com/superbox-dev/keba_keenergy/issues/65

## [1.10.2] - 2026-07-18

### Changed

- Updated `keba_keenergy_api` to 2.12.2. ([Issue #63][issue-63])

### Fixed

- Fixed the missing "Auto cool" option of the control unit operating mode select. ([Issue #60][issue-60])

[issue-60]: https://github.com/superbox-dev/keba_keenergy/issues/60
[issue-63]: https://github.com/superbox-dev/keba_keenergy/issues/63

## [1.10.1] - 2026-05-21

### Fixed

- Fixed the missing translation of the photovoltaics device.
- Fixed the missing API error message and improved the error logging. ([Issue #59][issue-59])
- Fixed API requests for values that the control unit or its software version does not provide. These values are
  now filtered before the first update. ([Issue #59][issue-59])

[issue-59]: https://github.com/superbox-dev/keba_keenergy/issues/59

## [1.10.0] - 2026-05-19

### Added

- Added numbers and sensors for the heating limits (day and night) of the heating circuits. ([Issue #46][issue-46])
- Added support for heating circuits with active or passive cooling: the climate entity supports the cool mode, and
  the heating circuits got the cooling curve select, the cooling curve offset and slope, the cooling limits, the
  target room cooling temperatures and the cool request sensor. ([Issue #47][issue-47])
- Added the passive cooling device with temperature, switch valve position, circulation pump speed and mixer
  sensors. ([Issue #47][issue-47])
- Added the sensor "Return flow temperature (mixer)" to the heating circuit.
- Added the photovoltaics device with the sensors "Excess power", "Daily energy" and "Total energy".
  ([Issue #55][issue-55])
- Added the entities to use the excess energy (PV surplus) of photovoltaics: "PV surplus" binary sensors, "Use PV
  surplus" switches, target temperatures, hystereses and heating and cooling limits for PV surplus, the electricity
  consumption from PV surplus and the operating hours, maximum runtime and activation counter during PV surplus.
  ([Issue #55][issue-55])
- Added the sensor "Mixer" and the binary sensor "Pump state" to the heating circuit. ([Issue #57][issue-57])
- Added attributes to the mixer position sensor. ([Issue #58][issue-58])

### Changed

- Required Python 3.14 and Home Assistant 2026.3.0 or newer.
- Updated `keba_keenergy_api` to 2.12.0.
- Hid the sensors that are not available in the heat pump setup, e.g. room temperature, room humidity, mixer, pump,
  return flow temperature, fresh water module and outdoor temperature. ([Issue #47][issue-47])
- Moved the coefficient of performance, the seasonal performance factors and other technical sensors to the
  diagnostic entity category.
- Renamed the heat pump sensor "Circulation pump" to "Circulation pump speed". Existing entity IDs are not changed.
- Updated the English and German translations.

### Fixed

- Fixed the state of the control unit "Operating mode" select being updated with a delay.
- Fixed connection failures with `.local` hostnames by using IPv4 for the HTTP client.
- Fixed duplicate entities.
- Fixed the wrong detection of the heating circuit pump. ([Issue #57][issue-57])

[issue-46]: https://github.com/superbox-dev/keba_keenergy/issues/46
[issue-47]: https://github.com/superbox-dev/keba_keenergy/issues/47
[issue-55]: https://github.com/superbox-dev/keba_keenergy/issues/55
[issue-57]: https://github.com/superbox-dev/keba_keenergy/issues/57
[issue-58]: https://github.com/superbox-dev/keba_keenergy/issues/58

## [1.9.1] - 2026-04-03

### Security

- Updated `keba_keenergy_api` to 2.10.2, which updates `aiohttp` from 3.13.3 to 3.13.4.
  ([CVE-2026-34513][CVE-2026-34513])

[CVE-2026-34513]: https://github.com/advisories/GHSA-hcc4-c3v8-rx92

## [1.9.0] - 2026-03-15

### Added

- Added the "Scan interval" option and an update multiplier option for each device type, to update the values of a
  device only every n-th scan interval. The options only show the device types of the heat pump setup.
  ([Issue #30][issue-30])
- Added the sensor "Pump speed" to the heating circuit. ([Issue #34][issue-34])
- Added reauthentication. If the Web HMI rejects the credentials, Home Assistant asks for the new credentials.
  ([Issue #35][issue-35])
- Added the reconfiguration flow to change the host and the credentials. ([Issue #35][issue-35])

### Changed

- Implemented rules of the Home Assistant [integration quality scale][qs-checklist]: `runtime-data`,
  `config-entry-unloading`, `action-setup`, `parallel-updates`, `entity-category`, `icon-translations`,
  `strict-typing` and descriptions for all config flow fields. ([Issue #35][issue-35])
- Added support for Python 3.14.
- Updated `keba_keenergy_api` to 2.10.1.

[qs-checklist]: https://developers.home-assistant.io/docs/core/integration-quality-scale/rules/
[issue-30]: https://github.com/superbox-dev/keba_keenergy/issues/30
[issue-34]: https://github.com/superbox-dev/keba_keenergy/issues/34
[issue-35]: https://github.com/superbox-dev/keba_keenergy/issues/35

## [1.8.1] - 2026-02-20

### Fixed

- Fixed the missing names of the heating curves. ([Issue #36][issue-36])

[issue-36]: https://github.com/superbox-dev/keba_keenergy/issues/36

## [1.8.0] - 2026-02-17

### Added

- Added the sensors "Target overheating", "Current overheating" and "Expansion valve position" to the heat pump.
  ([Issue #29][issue-29])
- Added the sensor "Circulation return temperature" (disabled by default) and the binary sensor "Circulation pump
  state" to the hot water tank. ([Issue #24][issue-24])
- Added the select "Heating curve", the numbers "Heating curve offset" and "Heating curve slope" and the switch "Use
  heating curve" to the heating circuit. ([Issue #24][issue-24])
- Added the `set_heating_curve_points` action to set up to 16 points of a heating curve. ([Issue #24][issue-24])
- Added the sensor "Heating curve" with the points of the heating curve as attributes. ([Issue #28][issue-28])

### Changed

- Updated `keba_keenergy_api` to 2.9.0.
- Rejected an end date before the start date in the `set_away_date_range` action.
- Translated the error messages of the actions and of failed write requests.
- Added a default display precision to the sensors without a unit.
- Improved the entity icons and disabled some rarely used entities by default.
- Updated the English and German translations.

### Fixed

- Fixed the unit of the solar circuit sensors "Heating energy" and "Daily energy", which showed J as kWh.
  ([Issue #32][issue-32])
- Fixed the translation of the switch valve position. ([Issue #31][issue-31])

[issue-24]: https://github.com/superbox-dev/keba_keenergy/issues/24
[issue-28]: https://github.com/superbox-dev/keba_keenergy/issues/28
[issue-29]: https://github.com/superbox-dev/keba_keenergy/issues/29
[issue-31]: https://github.com/superbox-dev/keba_keenergy/issues/31
[issue-32]: https://github.com/superbox-dev/keba_keenergy/issues/32

## [1.7.0] - 2026-01-31

### Added

- Added the `set_away_date_range` action to set the away period of the heating circuits. ([Issue #20][issue-20])
- Added a [blueprint][blueprint] to set the away date range from a calendar event. ([Issue #20][issue-20])
- Added a repair issue if more than 30 write operations are performed in a week, because frequent writes reduce
  the lifetime of the flash memory of the control unit. The counter is kept across restarts. ([Issue #23][issue-23])

### Changed

- Wrote values only if they changed, and wrote changes of numbers, target temperatures and the climate entity after
  a short delay, so several quick changes result in one write operation. ([Issue #23][issue-23])
- Disabled the numbers that are rarely changed by default. ([Issue #23][issue-23])
- Updated `keba_keenergy_api` to 2.8.1.
- Changed the documentation link to <https://superbox.one>.

### Fixed

- Fixed the missing English translations.

[blueprint]: https://superbox.one/#set-the-away-date-range-from-a-calendar
[issue-20]: https://github.com/superbox-dev/keba_keenergy/issues/20
[issue-23]: https://github.com/superbox-dev/keba_keenergy/issues/23

## [1.6.1] - 2026-01-24

### Added

- Added the sensor "Target room temperature (selected)" to the heating circuit. It always shows the current target
  temperature (day, night, ...) without the offset.

### Changed

- Updated `keba_keenergy_api` to 2.8.0.

### Fixed

- Fixed the slow update of entities after a change, e.g. of the operating mode or the preset mode of the climate
  entity.
- Fixed the wrong target temperature of the climate entity. ([Issue #19][issue-19])
- Fixed the preset mode "away" of the climate entity. ([Issue #21][issue-21])

[issue-19]: https://github.com/superbox-dev/keba_keenergy/issues/19
[issue-21]: https://github.com/superbox-dev/keba_keenergy/issues/21

## [1.6.0] - 2026-01-18

### Added

- Added support for switch valves.
- Added the diagnostic binary sensors "Compressor", "Source actuator", "Source", "Source pressure", "Three-phase" and
  "Variable drive frequency" to the heat pump to show failures.

### Changed

- Read values that never change, e.g. the number of heating circuits, only once on setup.
- Skipped API requests that the KEBA software version does not support.
- Updated `keba_keenergy_api` to 2.7.0.

## [1.5.0] - 2026-01-11

### Added

- Added support for buffer tanks.
- Added the sensors "Source pump speed", "Vaporization temperature", "Condensation temperature" and "Substate" to the
  heat pump.
- Added the number "Compressor speed (night)" and the switch "Compressor speed limit (night)" to the heat pump.
- Added the switch "Priority 1 before 2" to the solar circuit.

### Changed

- Enabled more sensors by default.
- Updated `keba_keenergy_api` to 2.6.0.

### Fixed

- Fixed the authentication with umlauts in the credentials.

## [1.4.0] - 2026-01-03

### Added

- Added support for solar circuits.

### Changed

- Updated `keba_keenergy_api` to 2.4.0.

## [1.3.1] - 2025-12-09

### Fixed

- Fixed the missing heat request states of the heating circuit in the HVAC action of the climate entity.

## [1.3.0] - 2025-10-29

### Added

- Added the diagnostic sensors "CPU usage", "WebView CPU usage", "WebServer CPU usage", "Control CPU usage",
  "RAM usage" and "Free RAM" to the control unit.

### Changed

- Attached `keba_keenergy.zip` to the GitHub releases, HACS installs the integration from it.

## [1.2.2] - 2025-10-19

### Changed

- Requested only the values that the hardware and software version of the Web HMI support.
- Removed the discovery of AP 420 control units.
- Updated `keba_keenergy_api` to 2.3.1.
- Updated the English and German translations.

### Fixed

- Fixed API errors for devices that are not installed, e.g. if there is no external heat source.

## [1.2.1] - 2025-10-15

### Added

- Added the discovery of AP 420 control units and of all AP 440 control units.

### Changed

- Logged the authentication check of the config flow as debug message instead of error.

### Fixed

- Fixed requests to API endpoints that some control units, e.g. AP 420/H-A, do not support.

## [1.2.0] - 2025-10-15

### Added

- Added the username and password for Web HMIs with login, required by newer software versions.
- Added the number "Target room temperature (offset)" to the heating circuit.
- Added support for external heat sources with operating mode, target temperature, heat request, operating hours,
  maximum runtime and activation counter.
- Added the sensors "Operating hours", "Maximum runtime" and "Activation counter" to the heat pump.
- Added the flow and return flow temperature sensors of the heating circuits.
- Added the manufacturer "ino" to the device info.

### Changed

- Disabled the sensors that not all heat pumps support by default.
- Disabled the SSL certificate verification, because newer software versions of the Web HMI use self-signed
  certificates.
- Changed the device class of the operating hours to duration.
- Updated `keba_keenergy_api` to 2.2.0.
- Updated the English and German translations.

### Removed

- Removed the entities to limit the compressor speed at night, for compatibility with older software versions.

### Fixed

- Fixed the state class of sensors.

## [1.1.0] - 2025-09-30

### Added

- Added the energy management sensors to the heat pump, e.g. power, energy, electricity consumption and coefficient
  of performance.
- Added selects for the operating modes of the control unit, heating circuits and hot water tanks.
- Added the number and switch to limit the compressor speed at night.
- Added the sensors "Hot water flow", "Fresh water module temperature" and "Flow temperature setpoint".
- Added the heat request state "Off (room temperature reached)" of the heating circuit.

### Changed

- Translated the manufacturer and model name of the heat pump device.
- Logged API errors as errors instead of debug messages.
- Updated `keba_keenergy_api` to 2.0.0.
- Updated the English and German translations.

### Fixed

- Fixed the slow update after changing a number.
- Fixed the upper target temperature of the water heater.

## [1.0.1] - 2025-09-12

### Added

- Added German translations, also for the heating circuit and hot water tank devices.

### Fixed

- Fixed the wrong unit of the room humidity sensor.

## [1.0.0] - 2025-09-01

### Added

- Added the config flow with host and SSL, and the discovery of AP 440 control units.
- Added the control unit, heat pump, heating circuit and hot water tank devices.
- Added the climate entities of the heating circuits and the water heater entities of the hot water tanks.
- Added the numbers for the target temperatures of the heating circuits (day, night, holiday) and the hot water tanks.
- Added the sensors for the outdoor temperature, the operating modes, the heat pump state, temperatures, pressures
  and compressor, and the binary sensor for the heat request.

[Unreleased]: https://github.com/superbox-dev/keba_keenergy/compare/v1.10.4...HEAD
[1.10.4]: https://github.com/superbox-dev/keba_keenergy/compare/v1.10.3...v1.10.4
[1.10.3]: https://github.com/superbox-dev/keba_keenergy/compare/v1.10.2...v1.10.3
[1.10.2]: https://github.com/superbox-dev/keba_keenergy/compare/v1.10.1...v1.10.2
[1.10.1]: https://github.com/superbox-dev/keba_keenergy/compare/v1.10.0...v1.10.1
[1.10.0]: https://github.com/superbox-dev/keba_keenergy/compare/v1.9.1...v1.10.0
[1.9.1]: https://github.com/superbox-dev/keba_keenergy/compare/v1.9.0...v1.9.1
[1.9.0]: https://github.com/superbox-dev/keba_keenergy/compare/v1.8.1...v1.9.0
[1.8.1]: https://github.com/superbox-dev/keba_keenergy/compare/v1.8.0...v1.8.1
[1.8.0]: https://github.com/superbox-dev/keba_keenergy/compare/v1.7.0...v1.8.0
[1.7.0]: https://github.com/superbox-dev/keba_keenergy/compare/v1.6.1...v1.7.0
[1.6.1]: https://github.com/superbox-dev/keba_keenergy/compare/v1.6.0...v1.6.1
[1.6.0]: https://github.com/superbox-dev/keba_keenergy/compare/v1.5.0...v1.6.0
[1.5.0]: https://github.com/superbox-dev/keba_keenergy/compare/v1.4.0...v1.5.0
[1.4.0]: https://github.com/superbox-dev/keba_keenergy/compare/v1.3.1...v1.4.0
[1.3.1]: https://github.com/superbox-dev/keba_keenergy/compare/v1.3.0...v1.3.1
[1.3.0]: https://github.com/superbox-dev/keba_keenergy/compare/v1.2.2...v1.3.0
[1.2.2]: https://github.com/superbox-dev/keba_keenergy/compare/v1.2.1...v1.2.2
[1.2.1]: https://github.com/superbox-dev/keba_keenergy/compare/v1.2.0...v1.2.1
[1.2.0]: https://github.com/superbox-dev/keba_keenergy/compare/v1.1.0...v1.2.0
[1.1.0]: https://github.com/superbox-dev/keba_keenergy/compare/v1.0.1...v1.1.0
[1.0.1]: https://github.com/superbox-dev/keba_keenergy/compare/v1.0.0...v1.0.1
[1.0.0]: https://github.com/superbox-dev/keba_keenergy/releases/tag/v1.0.0

<!--end-->
