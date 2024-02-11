# SPDX-FileCopyrightText: 2017 Scott Shawcroft, written for Adafruit Industries
# SPDX-FileCopyrightText: Copyright (c) 2024 Ezra Schwartz
# pylint: disable=implicit-str-concat
# pylint: disable=missing-function-docstring
# pylint: disable=invalid-name
# pylint: disable=consider-using-enumerate
# pylint: disable=no-else-return
# pylint: disable=inconsistent-return-statements
# pylint: disable=missing-function-docstring
#
# SPDX-License-Identifier: MIT
"""
`cycling_power_service`
================================================================================

Cycling Power data is a library to help people use cycing power meters in their circuitpython code.
This library allows users to extract power data from a power meter and read the data.
The librarys goal is to make it more acessable to create projects involving power meters by
streamlining the process of extracting the data from a power meter's bluetooth packet.


* Author(s): Ezra Schwartz

Implementation Notes
--------------------

**Hardware:**

Adafruit ItsyBitsy nRF52840 Express - Bluetooth LE <https://www.adafruit.com/product/4481>

**Software and Dependencies:**

* Adafruit CircuitPython firmware for the supported boards:
  https://circuitpython.org/downloads



# * Adafruit's Bus Device library: https://github.com/adafruit/Adafruit_CircuitPython_BusDevice
# * Adafruit's Register library: https://github.com/adafruit/Adafruit_CircuitPython_Register
"""

# imports
import struct
from collections import namedtuple
import _bleio
from adafruit_ble.services import Service
from adafruit_ble.uuid import StandardUUID
from adafruit_ble.characteristics import Characteristic, ComplexCharacteristic

try:
    from typing import Optional
except ImportError:
    pass


__version__ = "0.0.0-auto.0"
__repo__ = "https://github.com/EzrSchwartz/CircuitPython_Cycling_Power_Service.git"


CPMeasurementValues = namedtuple(
    "CPMeasurementValues",
    ("value" "ByteArray"),
)


class _CPMeasurement(ComplexCharacteristic):
    """Notify-only characteristic of power data."""

    uuid = StandardUUID(0x2A63)

    def __init__(self) -> None:
        super().__init__(properties=Characteristic.NOTIFY)

    def bind(self, service: "CyclingPowerService") -> _bleio.PacketBuffer:
        """Bind to a CyclingPowerService."""
        bound_characteristic = super().bind(service)
        bound_characteristic.set_cccd(notify=True)
        # Use a PacketBuffer to receive the CPS data
        return _bleio.PacketBuffer(bound_characteristic, buffer_size=1)


class CyclingPowerService(Service):
    """Service for reading from a Cycling Power sensor."""

    uuid = StandardUUID(0x1818)

    cp_measurement = _CPMeasurement()

    def __init__(self, service: Optional["CyclingPowerService"] = None) -> None:
        super().__init__(service=service)
        self._measurement_buf = None

    @property
    def power_Value(self) -> Optional[CPMeasurementValues]:  # returns the power value
        if self._measurement_buf is None:
            self._measurement_buf = bytearray(
                self.cp_measurement.incoming_packet_length
            )

        # Clear the buffer
        for i in range(len(self._measurement_buf)):
            self._measurement_buf[i] = 0

        packet_length = self.cp_measurement.readinto(self._measurement_buf)
        if packet_length > 0:
            # find the byte pair for power and return it
            for i in range(0, len(self._measurement_buf), 2):
                if i + 2 <= len(self._measurement_buf):
                    if i == 2:
                        value = struct.unpack_from("<H", self._measurement_buf, i)[0]
                        return value
                    else:
                        continue

    @property
    def byte_array(
        self,
    ) -> Optional[CPMeasurementValues]:  # returns the raw Byte Array from the packet
        # Clear the buffer

        if self._measurement_buf is None:
            self._measurement_buf = bytearray(
                self.cp_measurement.incoming_packet_length
            )

        ByteArray = "".join("{:02x}".format(x) for x in self._measurement_buf)

        return ByteArray
