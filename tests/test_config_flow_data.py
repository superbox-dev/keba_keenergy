# Copyright 2025-2026 Michael Hacker
# SPDX-License-Identifier: Apache-2.0

"""Test data for `test_config_flow.py`."""

from ipaddress import ip_address
from typing import Final

from homeassistant.helpers.service_info.zeroconf import ZeroconfServiceInfo

ZERO_CONF_SERVICE_INFO: Final[ZeroconfServiceInfo] = ZeroconfServiceInfo(
    ip_address=ip_address("10.0.0.100"),
    ip_addresses=[ip_address("10.0.0.100")],
    port=0,
    hostname="ap4400.local.",
    type="_keba-device._tcp.local.",
    name="ap4400._keba-device._tcp.local.'",
    properties={
        "devicename": "AP 440/H-A",
        "serialnumber": "12345678",
    },
)
