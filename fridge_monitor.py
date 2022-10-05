import time
import asyncio
from btle_scanner import SensorScanner
from sensors.GoveeSensor import GoveeReading

class DeviceNotFoundError(Exception):
    pass

class FridgeWatcher:
    def __init__(self, sensor: str, temp_limit: float=20.0, batt_limit: int=30):
        self.sensor = sensor
        self.temp = temp_limit
        self.batt = batt_limit
        self.scanner = SensorScanner(60.0)
        self.delay = 300
        self.last_alert_day = time.gmtime(time.time())[2] # day of month
    
    def reset_last_alert(self):
        self.last_alert_day = time.gmtime(time.time())[2] # day of month

    # set delay until next scan
    def set_delay(self, report, alerted=False):
        if alerted:
            # scale up to daily alerts if not corrected
            self.delay = max([self.delay * 4, 3600 * 24])
        else:
            # TODO: scale to safety margin from setpoints
            self.delay = 300

    async def discover(self, retries: int=3):
        reports = await self.scanner.scan()
        # for now, just loop until you find the right reading
        for report in reports.values():
            if report.name == self.sensor:
                self.set_delay(report)
                self.reset_last_alert()
                return report
        if retries == 0:
            print("device not found - exiting")
            raise DeviceNotFoundError
        else:
            print("device not found - looking again")
            self.discover(retries - 1)

    async def monitor(self, retries: int=2):
        await asyncio.sleep(self.delay)
        reports = await self.scanner.scan()
        status = self.health_check(reports)
        return status

    def our_sensor_report(self, reports: dict):
        our_report = None
        for report in reports.values():
            if report.name == self.sensor:
                our_report = report
        return our_report

    def health_check(self, reports: dict):
        healthy = True
        readings = self.our_sensor_report(reports)
        if readings == None:
            print("Sending loss of contact")
            alert = f'Lost contact with {self.sensor}'
            healthy = False

        elif readings.temp_F() > 32.1:
            print("sending temp alarm")
            alert = 'High temp alert!'
            healthy = False

        elif readings.battery() < 50:
            print("sending battery alarm")
            alert = 'Sensor Battery Failing!'
            healthy = False

        if healthy:
            alert = ""
        self.set_delay(readings, healthy)
        self.scanner.clear_readings()
        return alert, readings