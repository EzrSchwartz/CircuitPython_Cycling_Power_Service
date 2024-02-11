# SPDX-FileCopyrightText: 2017 Scott Shawcroft, written for Adafruit Industries
# SPDX-FileCopyrightText: Copyright (c) 2024 Ezra Schwartz
#
# SPDX-License-Identifier: Unlicense

from adafruit_ble import BLERadio
from adafruit_ble.advertising import Advertisement
from cycling_power_service import CyclingPowerService


# This function will return the power meter object after connecting
# requires you to feed it the name of the power meter which you want to connect to
def PowerConnectAndReturn(device_name):
    ble = BLERadio()
    print(f"Scanning for {device_name}")
    for advertisement in ble.start_scan(Advertisement, timeout=5):
        if advertisement.complete_name == device_name:
            print(f"Found {device_name}, trying to connect...")
            power_sensor = ble.connect(advertisement)
            print("Connected.")
            return power_sensor
    print("No Sensor Found")
    return None


# Function to return the power value after being fed the power sensor object
def ReturnPower(power_sensor):
    power_service = power_sensor[CyclingPowerService]
    power = power_service.power_Value
    return power


# Will print the current power recorded by the device name
print(ReturnPower(PowerConnectAndReturn("Replace with name of your power meter")))
