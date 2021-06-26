from bluepy.btle import *
import time, datetime
from ThunderboardSensor import ThunderboardSensor
from GoveeSensor import GoveeSensor


# DEBUG=0 turns off messages, the higher the number the more messages are printed to the screen
DEBUG = 5

class SensorScanner:
    """BLE scanner for temp/humidity sensors"""
    def __init__(self):
        self.sensors = {
            'Thunderboards': [],
            'Govee': []
        }

    def scan(self):
        """Scan for sensors and return results sorted by type"""
        scanner = Scanner()         # initialize BLE
        devices = scanner.scan(4)   # scan for BLE devices for 4 seconds

        for dev in devices:
            scanData = dev.getScanData()
            for (adtype, desc, value) in scanData:
                if desc == 'Complete Local Name':
                    if 'Thunder Sense #' in value:              # if the device is a TB2, then add it to tbsense
                        self.sensors['Thunderboards'].append(ThunderboardSensor(dev))
                    elif 'GVH5' in value:
                        scanData = dev.getScanData()
                        connection = Peripheral(dev)
                        self.sensors['Govee'].append(GoveeSensor(scanData, connection))

    def scanGovee(self):
        for device in self.sensors['Govee']:
            device.refreshReadings()

    def scanThunderboard(self):
        for device in self.sensors['Thunderboards']:

            try:

                #for key in tb.sensor.keys():
                for key in ('firmware', 'temperature','humidity','ambientLight','battery'): # TODO change this to a list of sensors passed in from the command line
                    if key == 'temperature':
                            data['temperature'] = tb.readTemperature()
                            text += 'Temperature:\t{} C\n'.format(data['temperature'])

                    elif key == 'humidity':
                        data['humidity'] = tb.readHumidity()
                        text += 'Humidity:\t{} %RH\n'.format(data['humidity'])

                    elif key == 'ambientLight':
                        data['ambientLight'] = tb.readAmbientLight()
                        text += 'Ambient Light:\t{} Lux\n'.format(data['ambientLight'])

                    elif key == 'uvIndex':
                        data['uvIndex'] = tb.readUvIndex()
                        text += 'UV Index:\t{}\n'.format(data['uvIndex'])

                    elif key == 'co2' and tb.coinCell == False:
                        data['co2'] = tb.readCo2()
                        text += 'eCO2:\t\t{}\n'.format(data['co2'])

                    elif key == 'voc' and tb.coinCell == False:
                        data['voc'] = tb.readVoc()
                        text += 'tVOC:\t\t{}\n'.format(data['voc'])

                    elif key == 'sound':
                        print ("before sound")
                        try:
                            data['sound'] = tb.readSound()
                        except:
                            print ("failed readsound")
                        print ("after sound")
                        text += 'Sound Level:\t{}\n'.format(data['sound'])

                    elif key == 'pressure':
                        data['pressure'] = tb.readPressure()
                        text += 'Pressure:\t{}\n'.format(data['pressure'])

                    elif key == 'battery':
                        data['battery'] = tb.readBattery()
                        text += 'Battery:\t{}\n'.format(data['battery'])

                    elif key == 'firmware':
                        data['firmware'] = tb.readFirmware()
                        text += 'Firmware:\t{}\n'.format(data['firmware'])

            except:
                print ("Failed to get sensor data")
                return
            
            print(text)
            tb.csvfile.write("{}, {},{},{},{}\n".format(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), data['temperature'],data['humidity'],data['ambientLight'],data['battery']))

            thunderboards[devId].ble_service.disconnect() # disconnect from the TB2 so it will go back to sleep and save battery power
        return

if __name__ == '__main__':
    ''' Program execution begins here '''

    sensor_scanner = SensorScanner()

    sensor_scanner.scan()

    while True:                                 # this program runs forever (hopefully)
        govee_count = len(sensor_scanner.sensors['Govee']) 
        if govee_count == 0:
            sensor_scanner.scan()
            print ("\b."),            # print out .s which makes it easy to visialize the time between samples
        else:
            print("{} Govee H5101 found - begin scanning".format(govee_count))
            sensor_scanner.scanGovee()

            time.sleep(1)          # wait for this TB board to sleep before looking for the others
