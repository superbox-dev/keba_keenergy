# KEBA KeEnergy integration

[![CI](https://github.com/superbox-dev/keba_keenergy/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/superbox-dev/keba_keenergy_api/actions/workflows/ci.yml)
![Typing: strict](https://img.shields.io/badge/typing-strict-green.svg)
![Code style: black](https://img.shields.io/badge/code%20style-black-black)
![Code style: Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/charliermarsh/ruff/main/assets/badge/v1.json)

A Home Assistant integration for heaters with a KEBA KeEnergy control system.

This integration supports the following manufacturers and devices:

| Manufacturer                           | Supported | Tested devices |
|----------------------------------------|-----------|----------------|
| [M-TEC](https://m-tec.at/)             | ✅        | WPS26          |
| [ÖkoFEN](https://www.oekofen.com/) *1) | ❌        |                |

*1) KEBA AP 440/H-A controller has no activated Web GUI

## Table of Contents

- [Screenshots](#screenshots)
- [Installation](#installation)
- [Changelog](#changelog)
- [Contributing](#contributing)
- [Donation](#donation)

## Screenshots

### Climate card

![Inverter Sensors](images/climate_card.png)

### KEBA AP 440/H-A controller sensors

![Inverter Sensors](images/keba_cpntroller.png)

### Heat circuit controls and sensors

![Inverter Sensors](images/heat_circuit.png)

### Heat pump sensors

![Inverter Sensors](images/heat_pump.png)

### Hot water tank controls and sensors

![Inverter Sensors](images/hot_water_tank.png)

## Installation

1. Install this integration with HACS, or copy the contents of this repository into the
   `custom_components/keba_keenery` directory.
2. Restart Home Assistant.
3. Start the configuration flow: go to `Configuration` -> `Integrations`, click the `+ Add Integration` and select
   `KEBA KeEnergy` from the list.
4. Add IP address or hostname of your KEBA KeEnergy device.
5. Enjoy :-)

## Changelog

The changelog lives in the [CHANGELOG.md](CHANGELOG.md) document. The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## Contributing

We're happy about your contributions to the project!
You can get started by reading the [CONTRIBUTING.md](CONTRIBUTING.md).

## Donation

We put a lot of time into this project. If you like it, you can support us with a donation.

[![ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/F2F0KXO6D)
