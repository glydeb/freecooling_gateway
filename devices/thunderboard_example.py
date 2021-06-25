from bluepy.btle import *
import struct
from time import sleep

class Thunderboard:

   def __init__(self, dev):
      self.dev  = dev
      self.char = dict()
      self.name = ''
      self.session = ''
      self.coinCell = False

      # Get device name and characteristics

      scanData = dev.getScanData()

      for (adtype, desc, value) in scanData:
         if (desc == 'Complete Local Name'):
            self.name = value

      ble_service = Peripheral()
      ble_service.connect(dev.addr, dev.addrType)
      characteristics = ble_service.getCharacteristics()

      for k in characteristics:
         if k.uuid == '2a6e':
            self.char['temperature'] = k
            
         elif k.uuid == '2a6f':
            self.char['humidity'] = k
            
         elif k.uuid == '2a76':
            self.char['uvIndex'] = k
            
         elif k.uuid == '2a6d':
            self.char['pressure'] = k
            
         elif k.uuid == 'c8546913-bfd9-45eb-8dde-9f8754f4a32e':
            self.char['ambientLight'] = k

         elif k.uuid == 'c8546913-bf02-45eb-8dde-9f8754f4a32e':
            self.char['sound'] = k

         elif k.uuid == 'efd658ae-c401-ef33-76e7-91b00019103b':
            self.char['co2'] = k

         elif k.uuid == 'efd658ae-c402-ef33-76e7-91b00019103b':
            self.char['voc'] = k

         elif k.uuid == 'ec61a454-ed01-a5e8-b8f9-de9ec026ec51':
            self.char['power_source_type'] = k

   
   def readTemperature(self):
      value = self.char['temperature'].read()
      value = struct.unpack('<H', value)
      value = value[0] / 100
      return value

   def readHumidity(self):
      value = self.char['humidity'].read()
      value = struct.unpack('<H', value)
      value = value[0] / 100
      return value

   def readAmbientLight(self):
      value = self.char['ambientLight'].read()
      value = struct.unpack('<L', value)
      value = value[0] / 100
      return value

   def readUvIndex(self):
      value = self.char['uvIndex'].read()
      value = ord(value)
      return value

   def readCo2(self):
      value = self.char['co2'].read()
      value = struct.unpack('<h', value)
      value = value[0]
      return value

   def readVoc(self):
      value = self.char['voc'].read()
      value = struct.unpack('<h', value)
      value = value[0]
      return value

   def readSound(self):
      value = self.char['sound'].read()
      value = struct.unpack('<h', value)
      value = value[0] / 100
      return value

   def readPressure(self):
      value = self.char['pressure'].read()
      value = struct.unpack('<L', value)
      value = value[0] / 1000
      return value

 

 

thundercloud.py handles the connection to the Firebase database. getSession() generates a new session ID and is called once for every new Thunderboard Sense connection. putEnvironmentData() inserts the data and updates the timestamps:

 

 

from firebase import firebase
import uuid
import time

class Thundercloud:

   def __init__(self):

      self.addr     = 'https://'-- Firebase Database Name --'.firebaseio.com/'
      self.firebase = firebase.FirebaseApplication(self.addr, None)

   def getSession(self, deviceId):

      timestamp = int(time.time() * 1000)
      guid = str(uuid.uuid1())

      url = 'thunderboard/{}/sessions'.format(deviceId)
      self.firebase.put(url, timestamp, guid)

      
      d = {
            "startTime" : timestamp,
            "endTime" : timestamp,
            "shortURL": '',
            "contactInfo" : {
                 "fullName":"First and last name",
                 "phoneNumber":"12345678",
                 "emailAddress":"name@example.com",
                 "title":"",
                 "deviceName": 'Thunderboard #{}'.format(deviceId)
             },
             "temperatureUnits" : 0,
             "measurementUnits" : 0,
         }

      url = 'sessions'
      self.firebase.put(url, guid, d)

      return guid

   def putEnvironmentData(self, guid, data):

      timestamp = int(time.time() * 1000)
      url = 'sessions/{}/environment/data'.format(guid)
      self.firebase.put(url, timestamp, data)

      url = 'sessions/{}'.format(guid)
      self.firebase.put(url, 'endTime', timestamp)

 
 

from bluepy.btle import *
import struct
from time import sleep
from tbsense import Thunderboard
from thundercloud import Thundercloud
import threading

def getThunderboards():
    scanner = Scanner(0)
    devices = scanner.scan(3)
    tbsense = dict()
    for dev in devices:
        scanData = dev.getScanData()
        for (adtype, desc, value) in scanData:
            if desc == 'Complete Local Name':
                if 'Thunder Sense #' in value:
                    deviceId = int(value.split('#')[-1])
                    tbsense[deviceId] = Thunderboard(dev)

    return tbsense

def sensorLoop(fb, tb, devId):

    session = fb.getSession(devId)
    tb.session = session
    
    value = tb.char['power_source_type'].read()
    if ord(value) == 0x04:
        tb.coinCell = True

    while True:

        text = ''

        text += '\n' + tb.name + '\n'
        data = dict()

        try:

            for key in tb.char.keys():
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
                    data['sound'] = tb.readSound()
                    text += 'Sound Level:\t{}\n'.format(data['sound'])

                elif key == 'pressure':
                    data['pressure'] = tb.readPressure()
                    text += 'Pressure:\t{}\n'.format(data['pressure'])

        except:
            return

        print(text)
        fb.putEnvironmentData(session, data)
        sleep(1)


def dataLoop(fb, thunderboards):
    threads = []
    for devId, tb in thunderboards.items():
        t = threading.Thread(target=sensorLoop, args=(fb, tb, devId))
        threads.append(t)
        print('Starting thread {} for {}'.format(t, devId))
        t.start()


if __name__ == '__main__':
    
    fb = Thundercloud()

    while True:
        thunderboards = getThunderboards()
        if len(thunderboards) == 0:
            print("No Thunderboard Sense devices found!")
        else:
            dataLoop(fb, thunderboards)
