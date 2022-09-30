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

    def post(self, message, report: GoveeReading):
        temp_C, humidity, battery = report.readings()
        body = {"value1": message,"value2": f'{report.temp_F():.1f} deg F', "value3": f'{battery}%'}
        requests.post(self.url, params=body)

web_key = os.environ.get('IFTTT_KEY')

# If there's no key present, we can't request to IFTTT
if web_key == None:
    print("IFTTT_KEY environment variable not set!")
    sys.exit(1)


SENSOR_NAME =  "GVH5101_3574"
EVENT_NAME = "fridge_alert"
IFTTT_URL = "https://maker.ifttt.com/trigger/{}/with/key/{}".format(EVENT_NAME, web_key)
STARTUP_PARAMS={"value1":"monitoring starting","value2":"none yet","value3":"none yet"}

scanner = SensorScanner(30.0)
# startup report
requests.post(IFTTT_URL, params = STARTUP_PARAMS)
reporter = IFTTTService(IFTTT_URL)


while True:
    reports = asyncio.run(scanner.scan())
    # for now, just loop until you find the right reading
    for report in reports.values():
        if report.name == SENSOR_NAME:
           print("reporting for temp:{}, battery:{}%".format(report.temp_F(), report.battery()))

           if report.temp_F() > 32.1:
               print("sending temp alarm")
               reporter.post('Fridge too warm!', report)

           elif report.battery() < 50:
               print("sending battery alarm")
               reporter.post('Sensor Battery Failing!', report)

    scanner.clear_readings()