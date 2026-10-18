# KEBA KeEnergy

[![CI](https://github.com/superbox-dev/keba_keenergy/actions/workflows/ci.yml/badge.svg?branch=main)][workflow-ci]
![coverage-badge](https://raw.githubusercontent.com/superbox-dev/keba_keenergy/main/coverage-badge.svg)
![Typing: strict][typing-strict]
![Code style: Ruff][code-ruff]

A Home Assistant integration for heat pumps with a KEBA KeEnergy control unit. It exposes the values of the Web HMI
as Home Assistant entities to monitor and control heat pumps, heating circuits, hot water tanks, buffer tanks, solar
circuits, external heat sources and photovoltaics. It is used with heat pumps from M-TEC, ino and Windhager.

> [!NOTE]
> This is an unofficial integration. It is not affiliated with or supported by KEBA.

![Dashboard](assets/dashboard.png)

[workflow-ci]: https://github.com/superbox-dev/keba_keenergy/actions/workflows/ci.yml
[typing-strict]: https://img.shields.io/badge/typing-strict-green.svg
[code-ruff]: https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/charliermarsh/ruff/main/assets/badge/v1.json

## Installation

[![Open HACS repository on my Home Assistant](https://my.home-assistant.io/badges/hacs_repository.svg)][redirect-hacs]

1. Install the integration with [HACS](https://hacs.xyz/) (search for "KEBA KeEnergy").
2. Restart Home Assistant.
3. Go to **Settings** → **Devices & services**, select **+ Add integration** and search for **KEBA KeEnergy**.

Requires Home Assistant 2026.9.4 or newer and network access to the Web HMI of the control unit. See the
[installation](https://superbox-dev.github.io/keba_keenergy/#installation) and
[configuration](https://superbox-dev.github.io/keba_keenergy/#configuration) sections for a manual
installation and all parameters.

[redirect-hacs]: https://my.home-assistant.io/redirect/hacs_repository/?owner=superbox-dev&repository=keba_keenergy&category=integration

## Documentation

Read the full documentation on [GitHub Pages](https://superbox-dev.github.io/keba_keenergy/):
[supported devices](https://superbox-dev.github.io/keba_keenergy/#supported-devices),
[options](https://superbox-dev.github.io/keba_keenergy/#options),
[entities](https://superbox-dev.github.io/keba_keenergy/#supported-functionality),
[actions](https://superbox-dev.github.io/keba_keenergy/#actions),
[examples](https://superbox-dev.github.io/keba_keenergy/#examples),
[troubleshooting](https://superbox-dev.github.io/keba_keenergy/#troubleshooting) and more.

## Changelog

See [CHANGELOG.md](CHANGELOG.md).

## Get involved

Contributions are welcome: report [issues](https://github.com/superbox-dev/keba_keenergy/issues/new/choose),
request features, improve translations or contribute code. Read [CONTRIBUTING.md](CONTRIBUTING.md) to get started.

## Related projects

- [KEBA KeEnergy API](https://github.com/superbox-dev/keba_keenergy_api) is the Python library for the KEBA KeEnergy
  Web HMI used by this integration.

## Donation

<!--start-donation-->

I put a lot of time into this project. If you like it, you can support me with a donation.

[![KoFi](https://raw.githubusercontent.com/superbox-dev/.github/refs/heads/main/profile/superbox-kofi.jpg)][kofi]

or [donate with PayPal](https://www.paypal.com/donate?hosted_button_id=34ZFWTH4TNLXS)

[kofi]: https://ko-fi.com/F2F0KXO6D

<!--end-donation-->
