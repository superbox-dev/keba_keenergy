# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.5.0b2] - 2025-01-07

### Added

- Support for buffer tanks
- Add sensor for the heat pump substate

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
