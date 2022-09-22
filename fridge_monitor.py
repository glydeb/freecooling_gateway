import requests
import time
import os
import sys
import asyncio
from btle_scanner import SensorScanner
from sensors.GoveeSensor import GoveeReading

class IFTTTService:
    def __init__(self, url):
        self.url = url
    
    async def post(self, message, report: GoveeReading):
        temp_C, humidity, battery = report.readings()
        body = '{"value1":{},"value2":{},"value3":{}}"'.format(message, temp_C, battery)
        await requests.post(self.url, params=body)

web_key = os.environ.get('IFTTT_KEY')

# If there's no key present, we can't request to IFTTT
if web_key == None:
    print("IFTTT_KEY environment variable not set!")
    sys.exit(1)


SENSOR_NAME =  "GVH5101_7F32"
EVENT_NAME = "fridge_alert"
IFTTT_URL = "https://maker.ifttt.com/trigger/{}/with/key/{}".format(EVENT_NAME, web_key)

scanner = SensorScanner(30.0)
reporter = IFTTTService(IFTTT_URL)

while True:
    reports = asyncio.run_until_complete(scanner.scan()) 
    # for now, just loop until you find the right reading
    for report in reports:
        if report.name == SENSOR_NAME:
            
            if report.temp_F() > 32.1:
                reporter.post('Fridge too warm!', report)
            
            elif report.battery() < 20:
                reporter.post('Sensor Battery Failing!', report)
            
        # 
    scanner.clear_readings()