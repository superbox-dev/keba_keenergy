# KEBA KeEnergy – Home Assistant Integration for KEBA Heat Pumps

**KEBA KeEnergy Integration** is a powerful open-source **Home Assistant integration** that allows you to connect
and monitor KEBA-based heat pumps directly within your smart home. The integration exposes data from the KEBA KeEnergy
web interface as Home Assistant entities for monitoring, control, and automation of heating and hot water systems.

[![Dashboard](images/dashboard.png)](images/dashboard.png)

## With the KEBA KeEnergy Home Assistant Integration, you can

* Connects to your **KEBA heat pump** via the KeEnergy Web HMI API using host and port
* Monitor temperatures, operating states and system settings
* Control operating modes and parameters directly from Home Assistant
* Build automations based on heating demand, energy usage or schedules
* This turns your heat pump into a fully integrated smart-home component

## Features

* Automatic discovery of KEBA KeEnergy-based systems
* Compatible with multiple KEBA-controlled heat pumps
* Works as a Home Assistant custom integration (HACS supported)
* Provides a full set of entities – sensors, binary sensors, number and select entities for:
  * Heat pump
  * Heating circuit
  * Solar circuit
  * Hot water tank
  * Buffer tank
  * External heat source

Looking for more information? The [Wiki](https://github.com/superbox-dev/keba_keenergy/wiki) contains in-depth
documentation.

## Supported Systems

The KEBA KeEnergy Integration works with heat pumps that provide a KEBA KeEnergy Web HMI interface.
It is successfully used with devices from manufacturers such as M-TEC, Windhager and ino,
as well as other systems based on KEBA controls.

## Requirements

* A running instance of Home Assistant with [HACS](https://hacs.xyz/) installed for managing custom integrations.
* Network connectivity from the Home Assistant host to the KEBA heat pump’s Web HMI interface,
  including proper host/IP and port access.

## Getting started

[![Open HACS repository on my Home Assistant](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=mh-superbox&repository=keba_keenergy&category=integration)

1. Install this integration with HACS (search for "KEBA KeEnergy") or copy the contents of this repository into the
   `custom_components/keba_keenergy` directory.
2. Restart Home Assistant after installation completes.
3. Start the configuration flow: go to `Configuration` -> `Integrations`, click the `+ Add Integration` and select
   `KEBA KeEnergy` from the list.
4. Add IP address or hostname of your KEBA KeEnergy device.
5. Enjoy :-)

## Donation

I put a lot of time into this project. If you like it, you can support me with a donation.

[![KoFi](https://raw.githubusercontent.com/superbox-dev/.github/refs/heads/main/profile/superbox-kofi.jpg)](https://ko-fi.com/F2F0KXO6D)

## Changelog

The changelog lives in the [CHANGELOG.md](CHANGELOG.md) document.
The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## Get Involved

**The KEBA KeEnergy Integration** is an open-source project and contributions are welcome. You can:

* Report issues or request new features
* Improve documentation or translations
* Contribute code
* Support the project by starring it on GitHub ⭐

I'm happy about your contributions to the project!
You can get started by reading the [CONTRIBUTING.md](CONTRIBUTING.md).

![coverage-badge](https://raw.githubusercontent.com/superbox-dev/keba_keenergy/main/coverage-badge.svg)
[![CI](https://github.com/superbox-dev/KEBA-KeEnergy-API/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/superbox-dev/keba_keenergy/actions/workflows/ci.yml)

[![CI](https://github.com/superbox-dev/keba_keenergy/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/superbox-dev/keba_keenergy_api/actions/workflows/ci.yml)
![Typing: strict](https://img.shields.io/badge/typing-strict-green.svg)
![Code style: black](https://img.shields.io/badge/code%20style-black-black)
![Code style: Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/charliermarsh/ruff/main/assets/badge/v1.json)
