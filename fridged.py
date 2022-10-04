import os
import sys
import asyncio
from fridge_monitor import FridgeWatcher
from ifttt_service import IFTTTService

SENSOR_NAME =  "GVH5101_334C"
EVENT_NAME = "fridge_alert"
MAX_TEMP_F = 20.0
MIN_BATTERY = 25

# initialize web service
def ifttt():
    web_key = os.environ.get('IFTTT_KEY')
    # If there's no key present, we can't request to IFTTT
    if web_key == None:
        print("IFTTT_KEY environment variable not set!")
        sys.exit(1)
    return IFTTTService(EVENT_NAME, web_key)


async def main():
    notifier = ifttt()

    # initialize Fridge watcher
    watcher = FridgeWatcher(sensor=SENSOR_NAME, temp_limit=MAX_TEMP_F, batt_limit=MIN_BATTERY)

    # Discover fridge
    initial_readings = await watcher.discover()

    try:
        # Notify of monitoring start/initial status
        notifier.post(f'{SENSOR_NAME} monitoring established', initial_readings)

        # Monitoring loop
        while True:
            alert, readings = await watcher.monitor()
            if alert != "":
                notifier.post(alert, readings)
    finally:
        # Fault handling
        notifier.post(f'{SENSOR_NAME} monitoring disabled')

if __name__ == "__main__":
    asyncio.run(main())