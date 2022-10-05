import requests
from sensors.GoveeSensor import GoveeReading

class IFTTTService:
    def __init__(self, event: str, key: str):
        self.url = "https://maker.ifttt.com/trigger/{}/with/key/{}".format(event, key)

    def post(self, message: str, report: GoveeReading = None):
        temp_text, batt_text = "n/a", "n/a" # default values
        if report != None:
            temp_text = f'{report.temp_F():.1f} deg F'
            batt_text = f'{report.battery()}%'
        body = {"value1": message,"value2": temp_text, "value3": batt_text}
        return requests.post(self.url, params=body)