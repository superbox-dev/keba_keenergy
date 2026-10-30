# Copyright 2025-2026 Michael Hacker
# SPDX-License-Identifier: Apache-2.0

"""Test data for `test_config_flow.py`."""

from ipaddress import ip_address
from typing import Final

from homeassistant.helpers.service_info.zeroconf import ZeroconfServiceInfo

# The IP address of the Web HMI, also of the config entry fixture.
HOST: Final[str] = "10.0.0.100"

ZERO_CONF_SERVICE_INFO: Final[ZeroconfServiceInfo] = ZeroconfServiceInfo(
    ip_address=ip_address(HOST),
    ip_addresses=[ip_address(HOST)],
    port=0,
    hostname="ap4400.local.",
    type="_keba-device._tcp.local.",
    name="ap4400._keba-device._tcp.local.'",
    properties={
        "devicename": "AP 440/H-A",
        "serialnumber": "12345678",
    },
)
