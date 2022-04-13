
import asyncio
from tkinter import W
from GoveeSensor import GoveeReading
from bleak import *
import time

class SensorScanner:
    def __init__(self, delay: float):
        self.delay = delay
        self.readings = dict()
        self.scanner = BleakScanner()
        self.scanner.register_detection_callback(self.detection_callback)

    async def scan(self):
        await self.scanner.start()
        await asyncio.sleep(self.delay)
        await self.scanner.stop()
        return self.readings

    async def detection_callback(self, device, advertisement_data):
        print('detected')
        if device.name[:7] == "GVH5101":
            self.readings[device.address] = GoveeReading(device, advertisement_data)

    def clear_readings(self):
        extracted = list(self.readings.values())
        self.readings = dict()
        return extracted

async def scan():
    scanner = SensorScanner(30.0)
    while True:
        sensor_readings = await scanner.scan()
        # print and clear readings
        print(sensor_readings)
        scanner.clear_readings()
        # for reading in sensor_readings:
        #     temp_C, humidity, battery 
        # ("sensor: {}, temp: {} degC, rh: {}%, battery: {}%".format(sensor.name, temp_C, humidity, battery))

# can be run standalone
if __name__ == "__main__":
    asyncio.run(scan())