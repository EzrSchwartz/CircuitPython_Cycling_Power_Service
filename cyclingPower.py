# # SPDX-FileCopyrightText: 2020 Dan Halbert for Adafruit Industries
# #
# # SPDX-License-Identifier: MIT

# """
# `adafruit_ble_cycling_speed_and_cadence`
# ================================================================================

# BLE Cycling Speed and Cadence Service


# * Author(s): Dan Halbert for Adafruit Industries

# The Cycling Speed and Cadence Service is specified here:
# https://www.bluetooth.com/wp-content/uploads/Sitecore-Media-Library/Gatt/Xml/Services/org.bluetooth.service.cycling_speed_and_cadence.xml

# Implementation Notes
# --------------------

# **Hardware:**

# * Adafruit CircuitPython firmware for the supported boards:
#   https://github.com/adafruit/circuitpython/releases
# * Adafruit's BLE library: https://github.com/adafruit/Adafruit_CircuitPython_BLE
# """
# import struct
# from collections import namedtuple

# import _bleio
# from adafruit_ble.services import Service
# from adafruit_ble.uuid import StandardUUID
# from adafruit_ble.characteristics import Characteristic, ComplexCharacteristic
# from adafruit_ble.characteristics.int import Uint8Characteristic

# try:
#     from typing import Optional
# except ImportError:
#     pass

# __version__ = "0.0.0+auto.0"
# __repo__ = "https://github.com/adafruit/Adafruit_CircuitPython_BLE_Cycling_Speed_and_Cadence.git"

# # CSCMeasurementValues = namedtuple(
# #     "CSCMeasurementValues",
# #     (
# #         "cumulative_wheel_revolutions",
# #         "last_wheel_event_time",
# #         "cumulative_crank_revolutions",
# #         "last_crank_event_time",
# #     ),
# # )
# # """Namedtuple for measurement values.

# # .. :attribute:: cumulative_wheel_revolutions:

# #         Cumulative wheel revolutions (int).

# # .. :attribute:: last_wheel_event_time:

# #         Time (int), units in 1024ths of a second, when last wheel event was measured.
# #         This is a monotonically increasing clock value, not an interval.

# # .. :attribute:: cumulative_crank_revolutions:

# #         Cumulative crank revolutions (int).

# # .. :attribute:: last_crank_event_time:

# #         Time (int), units in 1024ths of a second, when last crank event was measured.
# #         This is a monotonically increasing clock value, not an interval.

# # For example::

# #     wheel_revs = svc.csc_measurement_values.cumulative_wheel_revolutions
# # """
# PowerMeasurementValues = namedtuple(
#     "PowerMeasurementValues",
#     (
#         "instantaneous_power",
#         "average_power",
#         "pedal_power_balance",
#         "maximum_power",
#     ),
# )
# """Namedtuple for power measurement values.

# .. :attribute:: instantaneous_power:

#         Instantaneous power output in watts (int).

# .. :attribute:: average_power:

#         Average power output in watts over a specific time or distance (int).

# .. :attribute:: pedal_power_balance:

#         Balance of power output between left and right pedals, represented as a percentage (float).
#         A value of 50.0 indicates equal power distribution.

# .. :attribute:: maximum_power:

#         Maximum power output in watts recorded (int).

# For example::

#     current_power = svc.power_measurement_values.instantaneous_power
# """

# class _CPMeasurement(ComplexCharacteristic):
#     """Notify-only characteristic of power and torque data."""

#     uuid = StandardUUID(0x2A63)

#     def __init__(self) -> None:
#         super().__init__(properties=Characteristic.NOTIFY)

#     def bind(self, service: "CyclingPowerService") -> _bleio.PacketBuffer:
#         """Bind to a CyclingPowerService."""
#         bound_characteristic = super().bind(service)
#         bound_characteristic.set_cccd(notify=True)
#         # Use a PacketBuffer that can store one packet to receive the CP data.
#         return _bleio.PacketBuffer(bound_characteristic, buffer_size=1)


# class CyclingPowerService(Service):
#     """Service for reading from a Cycling Speed and Cadence sensor."""

#     # 0x180D is the standard HRM 16-bit, on top of standard base UUID
#     uuid = StandardUUID(0x1818)


#     # Mandatory.
#     csc_measurement = _CPMeasurement()

#     # csc_feature = Uint8Characteristic(
#     #     uuid=StandardUUID(0x2A5C), properties=Characteristic.READ
#     # )
#     # sensor_location = Uint8Characteristic(
#     #     uuid=StandardUUID(0x2A5D), properties=Characteristic.READ
#     # )

#     # sc_control_point = Characteristic(
#     #     uuid=StandardUUID(0x2A39), properties=Characteristic.WRITE
#     # )

#     _SENSOR_LOCATIONS = (
#         "Other",
#         "Top of shoe",
#         "In shoe",
#         "Hip",
#         "Front Wheel",
#         "Left Crank",
#         "Right Crank",
#         "Left Pedal",
#         "Right Pedal",
#         "Front Hub",
#         "Rear Dropout",
#         "Chainstay",
#         "Rear Wheel",
#         "Rear Hub",
#         "Chest",
#         "Spider",
#         "Chain Ring",
#     )

#     def __init__(
#         self, service: Optional["CyclingPowerService"] = None
#     ) -> None:
#         super().__init__(service=service)
#         # Defer creating buffer until we're definitely connected.
#         self._measurement_buf = None
#         self._power_buf = None  # Initialize the power buffer here
#         self.power_measurement = None
#         self.incoming_packet_length = None

#     @property

#     def measurement_values(self) -> Optional[PowerMeasurementValues]:
#         """All the power measurement values, returned as a PowerMeasurementValues namedtuple.

#         Return ``None`` if no packet has been read yet.
#         """
#         if self.power_measurement is None:
#         # Handle the case where power_measurement is not initialized
#         # You might raise an error, initialize it, or return None
#             return None

#         if self._power_buf is None:
#         # Ensure you have the correct attribute or method to get the packet length
#         # Replace 'incoming_packet_length' with the correct one
#             self._power_buf = bytearray(self.power_measurement.incoming_packet_length)

#         buf = self._power_buf
#         packet_length = self.power_measurement.readinto(buf)
#         if packet_length == 0:
#             return None

#         flags = buf[0]
#         next_byte = 1 
#     # uint8: flags
#     #  bit 0 = 1: Instantaneous Power Data is present
#     #  bit 1 = 1: Average Power Data is present
#     #  bit 2 = 1: Pedal Power Balance Data is present
#     #  bit 3 = 1: Maximum Power Data is present
#     #
#     # The next field is present only if bit 0 above is 1:
#     #   uint16: Instantaneous Power
#     #
#     # The next field is present only if bit 1 above is 1:
#     #   uint16: Average Power
#     #
#     # The next field is present only if bit 2 above is 1:
#     #   uint8: Pedal Power Balance (percentage)
#     #
#     # The next field is present only if bit 3 above is 1:
#     #   uint16: Maximum Power


#         if flags & 0x1:
#             instantaneous_power = struct.unpack_from("<H", buf, next_byte)[0]
#             next_byte += 2
#         else:
#             instantaneous_power = None

#         if flags & 0x2:
#            average_power = struct.unpack_from("<H", buf, next_byte)[0]
#            next_byte += 2
#         else:
#            average_power = None

#         if flags & 0x4:
#             pedal_power_balance = struct.unpack_from("<B", buf, next_byte)[0]
#             next_byte += 1
#         else:
#             pedal_power_balance = None

#         if flags & 0x8:
#             maximum_power = struct.unpack_from("<H", buf, next_byte)[0]
#         else:
#             maximum_power = None

#         return PowerMeasurementValues(instantaneous_power, average_power, pedal_power_balance, maximum_power)

#     # def measurement_values(self) -> Optional[PowerMeasurementValues]:
#     #     """All the measurement values, returned as a PowerMeasurementValues
#     #     namedtuple.

#     #     Return ``None`` if no packet has been read yet.
#     #     """
#     #     # uint8: flags
#     #     #  bit 0 = 1: Wheel Revolution Data is present
#     #     #  bit 1 = 1: Crank Revolution Data is present
#     #     #
#     #     # The next two fields are present only if bit 0 above is 1:
#     #     #   uint32: Cumulative Wheel Revolutions
#     #     #   uint16: Last Wheel Event Time, in 1024ths of a second
#     #     #
#     #     # The next two fields are present only if bit 10 above is 1:
#     #     #   uint16: Cumulative Crank Revolutions
#     #     #   uint16: Last Crank Event Time, in 1024ths of a second
#     #     #

#     #     if self._measurement_buf is None:
#     #         self._measurement_buf = bytearray(
#     #             self.csc_measurement.incoming_packet_length  # pylint: disable=no-member
#     #         )
#     #     buf = self._measurement_buf
#     #     packet_length = self.csc_measurement.readinto(buf)  # pylint: disable=no-member
#     #     if packet_length == 0:
#     #         return None
#     #     flags = buf[0]
#     #     next_byte = 1

#     #     if flags & 0x1:
#     #         wheel_revs = struct.unpack_from("<L", buf, next_byte)[0]
#     #         wheel_time = struct.unpack_from("<H", buf, next_byte + 4)[0]
#     #         next_byte += 6
#     #     else:
#     #         wheel_revs = wheel_time = None

#     #     if flags & 0x2:
#     #         # Note that wheel revs is uint32 and and crank revs is uint16.
#     #         crank_revs = struct.unpack_from("<H", buf, next_byte)[0]
#     #         crank_time = struct.unpack_from("<H", buf, next_byte + 2)[0]
#     #     else:
#     #         crank_revs = crank_time = None

#     #     return CSCMeasurementValues(wheel_revs, wheel_time, crank_revs, crank_time)

#     @property
#     def location(self) -> str:
#         """The location of the sensor on the cycle, as a string.

#         Possible values are:
#         "Other", "Top of shoe", "In shoe", "Hip",
#         "Front Wheel", "Left Crank", "Right Crank",
#         "Left Pedal", "Right Pedal", "Front Hub",
#         "Rear Dropout", "Chainstay", "Rear Wheel",
#         "Rear Hub", "Chest", "Spider", "Chain Ring")
#         "Other", "Chest", "Wrist", "Finger", "Hand", "Ear Lobe", "Foot",
#         and "InvalidLocation" (if value returned does not match the specification).
#         """

#         try:
#             return self._SENSOR_LOCATIONS[self.sensor_location]
#         except IndexError:
#             return "InvalidLocation"


# #    def set_cumulative_wheel_revolutions(self, value):
# #        self._control_point_request(self.pack("<BLBB", 1, value, 0, )



import struct
import time
import _bleio
from adafruit_ble import BLERadio
from adafruit_ble.services import Service
from adafruit_ble.characteristics import Characteristic
from adafruit_ble.characteristics.int import Uint16Characteristic
from adafruit_ble.uuid import StandardUUID

import struct
import time
import _bleio
from adafruit_ble import BLERadio
from adafruit_ble.services import Service
from adafruit_ble.characteristics import Characteristic
from adafruit_ble.uuid import StandardUUID

class PowerMeasurementValues:
    def __init__(self, instantaneous_power, pedal_power_balance=None, accumulated_power=None):
        self.instantaneous_power = instantaneous_power
        self.pedal_power_balance = pedal_power_balance
        self.accumulated_power = accumulated_power

class CyclingPowerService(Service):
    uuid = StandardUUID(0x1818)  # Cycling Power Service UUID
    cycling_power_measurement = Characteristic(uuid=StandardUUID(0x2A63))

    def __init__(self, service=None):
        super().__init__(service=service)

    def measurement_values(self):
        try:
            time.sleep(0.1)  # Allow for BLE synchronization
            measurement_data = self.cycling_power_measurement.read()
            if not measurement_data:
                print("No data received from the power meter.")
                return None

            # Assuming the data format is as per your provided data packet structure
            # This unpacking logic needs to be adjusted based on actual data format from the power meter
            instantaneous_power = struct.unpack_from("<H", measurement_data, 0)[0]
            pedal_power_balance = struct.unpack_from("<H", measurement_data, 2)[0]
            accumulated_power = struct.unpack_from("<H", measurement_data, 4)[0]

            # Convert pedal_power_balance and accumulated_power appropriately if they are not direct readings

            return PowerMeasurementValues(instantaneous_power, pedal_power_balance, accumulated_power)

        except _bleio.BluetoothError as e:
            print("BluetoothError occurred:", e)
            return None
        except Exception as e:
            print("Unexpected error:", e)
            return None


# # Usage
# ble = BLERadio()
# while True:
#     for device in ble.start_scan():
#         if CyclingPowerService in device:
#             power_meter = device[CyclingPowerService]
#             while device.connected:
#                 power_values = power_meter.measurement_values()
#                 if power_values:
#                     print("Instantaneous Power:", power_values.instantaneous_power)
#                     # Print other values as needed
#             break
#     ble.stop_scan()


