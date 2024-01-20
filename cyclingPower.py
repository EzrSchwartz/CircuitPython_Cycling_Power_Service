

import struct
from collections import namedtuple
import _bleio
from adafruit_ble.services import Service
from adafruit_ble.uuid import StandardUUID
from adafruit_ble.characteristics import Characteristic, ComplexCharacteristic
from adafruit_ble.characteristics.int import Uint8Characteristic

prev_Tot_Time = 0
prev_Tot_Power = 0
Tot_power = 0
Tot_time = 0
try:
    from typing import Optional
except ImportError:
    pass

CPMeasurementValues = namedtuple(
    "CPMeasurementValues",
    (
        "hex"
    ),
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
    def power_meter_values(self) -> Optional[CPMeasurementValues]:
        if self._measurement_buf is None:
            self._measurement_buf = bytearray(self.cp_measurement.incoming_packet_length)


    # Clear the buffer
        for i in range(len(self._measurement_buf)):
            self._measurement_buf[i] = 0

        packet_length = self.cp_measurement.readinto(self._measurement_buf)
        if packet_length == 0:
            return None

        hex_data = ''.join('{:02x}'.format(x) for x in self._measurement_buf)
        
        byte_pairs = [hex_data[i:i+4] for i in range(0, len(hex_data), 4)]

    # Printing each 2-byte pair and its corresponding decimal value
        # for i, byte_pair in enumerate(byte_pairs):
        #     decimal_value = int(byte_pair, 16)
        #     if i == 2:
        #         Tot_time == decimal_value
        #         print(Tot_power)
        #     if i == 3:
        #         Tot_power == decimal_value
        #         print(Tot_time)

        # power = ((Tot_power-prev_Tot_Power)*1024)/((Tot_time-prev_Tot_Time)+1)
        # print(power)   

        # for i, byte_pair in enumerate(byte_pairs):
        #     decimal_value = int(byte_pair, 16)
        #     if i == 2:
        #         Tot_time == decimal_value
        #     if i == 3:
        #         Tot_power == decimal_value
        byte_data = bytes.fromhex(hex_data)

        for i in range(0, len(byte_data), 2):
            if i + 2 <= len(byte_data):
                value = struct.unpack_from('<H', byte_data, i)[0]
                print(f"Value at bytes {i}-{i+1}: {value}")



        return hex_data


#2c08(Label) 0000 950a f401 dbf2 fbde 0000 0000 0000 0000

