import asyncio
from GoveeSensor import GoveeSensor
from bleak import *

async def scan():
    devices = await BleakScanner.discover()
    for potential_sensor in devices:
        if potential_sensor.name[:7] == "GVH5101":
            sensor = GoveeSensor(potential_sensor)
            temp_C, humidity, battery = sensor.readings()
            print("sensor: {}, temp: {} degC, rh: {}%, battery: {}%".format(sensor.name, temp_C, humidity, battery))

loop = asyncio.get_event_loop()
while True:
    loop.run_until_complete(scan())