# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

<!--start-->

### Added

- Added service to set away date range [(Issue #20)](https://github.com/superbox-dev/keba_keenergy/issues/20)

## Changed

- Bump `keba_keenergy_api` to v2.8.1
- Changed documentation link to <www.superbox.one>

## [1.6.1] - 2025-01-24

### Added

- Added new sensor "Target temperature (selected)" to the heat circuit.
  This sensor show always the right target temperature (day, night, ...) without the offset.

### Fixed

- Fixed slow API update and refresh on entities that can changed e.g. "Operation mode" or the "Preset mode"
  in the climate entity
- Fixed climate entity show wrong target temperature [(Issue #19)](https://github.com/superbox-dev/keba_keenergy/issues/19)
- Fixed preset mode "away" in the climate entity [(Issue #21)](https://github.com/superbox-dev/keba_keenergy/issues/21)

## [1.6.0] - 2025-01-18

### Added

- Added support for switch valves
- Added diagnostic sensors "Compressor", "Source actuator", "Source", "Source pressure",
  "Three-phase" and "Variable drive frequency" to the heat pump device

### Fixed

- Fixed unnecessary API calls for values that did never change e.g. number of heating circuits
- Don't execute API calls for KEBA software versions that did not support this API call

## [1.5.0] - 2025-01-11

### Added

- Support for buffer tanks
- Added sensors "Source pump speed", "Vaporizer temperature", "Condenser temperature" and "Substate" to the heat pump
- Added number control for the "compressor night speed" to the heat pump
- Added switch control for the "compressor use night speed" to the heat pump
- Added switch control for the "priority 1 before 2" to the solar circuit

### Fixed

- Authentication does not work with umlauts

## [1.4.0] - 2025-01-03

### Added

- Support for solar circuits

## [1.3.1] - 2025-12-09

### Fixed

- missing heating circuit heat request modes in the climate entity HAVC action

## [1.3.0] - 2025-10-29

### Added

- Diagnostic sensors for CPU usage, RAM usage and free RAM

## [1.2.2] - 2025-10-19

### Fixed

- API errors when fetch data from a device that is not installed e.g. zero external heat sources

### Changed

- Update translations

## [1.2.1] - 2025-10-15

### Fixed

- invalid API endpoints for devices (e.g. AP420/H-A) that did not support this

## [1.2.0] - 2025-10-15

### Added

- Number entities to control the target temperature offset
- Support username and password for basic auth (newer software versions now required basic auth)
- External heat source device and entities
- Entity "Operating hours", "Maximum runtime" and "Activation counter" to the head pump
- Entity "Heat request", "Operating hours", "Maximum runtime" and "Activation counter" to the external heat source

### Changed

- Updated german and english translations
- Removed entities to control the night speed of the compressor (for backward compatibility with older software
  versions)

## [1.1.0] - 2025-09-30

### Added

- Energy management sensors for the head pump device
- Select entities for all operation modes
- Switch entity to control the compressor speed at night

### Changed

- German and english translations
- The manufacturer and model name from the head pump device translation

## [1.0.1] - 2025-09-12

### Added

- German translations

### Fixed

- Wrong unit for room humidity sensor

## [1.0.0] - 2025-09-1

Initial release

<!--end-->
