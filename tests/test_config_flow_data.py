# Copyright 2025-2026 Michael Hacker
# SPDX-License-Identifier: Apache-2.0

"""Test data for `test_config_flow.py`."""

from ipaddress import ip_address
from typing import Final

from homeassistant.const import CONF_PASSWORD
from homeassistant.const import CONF_USERNAME
from homeassistant.helpers.service_info.zeroconf import ZeroconfServiceInfo

# The IP address of the Web HMI, also of the config entry fixture.
HOST: Final[str] = "10.0.0.100"
# The host of the Web HMI after a reconfiguration.
RECONFIGURED_HOST: Final[str] = "10.0.0.200"
# The host name of the Web HMI that the zeroconf discovery finds.
ZEROCONF_HOST: Final[str] = "ap4400.local"

CREDENTIALS: Final[dict[str, str]] = {
    CONF_USERNAME: "test",
    CONF_PASSWORD: "test",
}

ZERO_CONF_SERVICE_INFO: Final[ZeroconfServiceInfo] = ZeroconfServiceInfo(
    ip_address=ip_address(HOST),
    ip_addresses=[ip_address(HOST)],
    port=0,
    hostname=f"{ZEROCONF_HOST}.",
    type="_keba-device._tcp.local.",
    name="ap4400._keba-device._tcp.local.'",
    properties={
        "devicename": "AP 440/H-A",
        "serialnumber": "12345678",
    },
)

ZERO_CONF_IPV6_SERVICE_INFO: Final[ZeroconfServiceInfo] = ZeroconfServiceInfo(
    ip_address=ip_address("fd00::100"),
    ip_addresses=[ip_address("fd00::100")],
    port=0,
    hostname=f"{ZEROCONF_HOST}.",
    type="_keba-device._tcp.local.",
    name="ap4400._keba-device._tcp.local.'",
    properties={
        "devicename": "AP 440/H-A",
        "serialnumber": "12345678",
    },
)

OPTION_KEYS: Final[list[str]] = [
    "scan_interval",
    "scan_interval_tick_system",
    "scan_interval_tick_heat_pump",
    "scan_interval_tick_heat_circuit",
    "scan_interval_tick_solar_circuit",
    "scan_interval_tick_hot_water_tank",
    "scan_interval_tick_buffer_tank",
    "scan_interval_tick_switch_valve",
    "scan_interval_tick_external_heat_source",
    "scan_interval_tick_photovoltaics",
]
