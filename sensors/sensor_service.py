# Copyright 2018 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from __future__ import print_function

import struct
import random
import sys
import socket
import time, datetime
from btle_scanner import SensorScanner

from colors import bcolors

ADDR = '192.168.0.109'
PORT = 10000
# Create a UDP socket
client_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

server_address = (ADDR, PORT)

device_id = sys.argv[1]
if not device_id:
    sys.exit('The device id must be specified.')

print('Bringing up device {}'.format(device_id))


def SendCommand(sock, message, log=True):
    """ returns message received """
    if log:
        print('sending: "{}"'.format(message), file=sys.stderr)

    sock.sendto(message.encode('utf8'), server_address)

    # Receive response
    if log:
        print('waiting for response', file=sys.stderr)

    response, _ = sock.recvfrom(4096)

    if log:
        print('received: "{}"'.format(response), file=sys.stderr)

    return response


print('Bring up device 1')


def MakeMessage(device_id, action, data=''):
    if data:
        return '{{ "device" : "{}", "action":"{}", "data" : "{}" }}'.format(
            device_id, action, data)
    else:
        return '{{ "device" : "{}", "action":"{}" }}'.format(device_id, action)

def getThunderboards():
    ''' Scan for TB sense boards for a few seconds and return all that are found'''
    scanner = Scanner()         # initialize BLE
    devices = scanner.scan(1.1)   # scan for BLE devices for this many seconds
    tbsense = dict()
    for device in devices:
        scanData = devices.getScanData()
        for (adtype, desc, value) in scanData:
            if desc == 'Complete Local Name':
                if 'Thunder Sense #' in value:              # if the device is a TB sense, then add it to tbsense
                    deviceId = int(value.split('#')[-1])
                    tbsense[deviceId] = Thunderboard.Thunderboard(device)

    return tbsense

def scanSensors(thunderboards):

    for devId, tb in thunderboards.items():

        try:
            value = tb.sensor['power_source_type'].read()   # TODO why do we need to know this? are some sensors only enabled when powered via USB?
        except:
            print("scanSensor disconnected")
            return

        if ord(value) == 0x04:
            tb.coinCell = True

        tb.filename="TB"
        tb.filename+=tb.dev.addr.replace(":","_")
        tb.filename+=".csv"
        print("filename={}".format(tb.filename))
        if not os.path.isfile(tb.filename):
            tb.csvfile=open(tb.filename, 'w+',1) 
            tb.csvfile.write("Date Time,Temperature C, Humidity, Lux, Battery, Comment\n")
        else:
            tb.csvfile=open(tb.filename, 'a+',1) 

     
        text = ''
        text += '\n' + tb.name + '\n'
        data = dict()                   # the sensor data is stored in this dictionary

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
                    print("before sound")
                    try:
                        data['sound'] = tb.readSound()
                    except:
                        print("failed readsound")
                    print("after sound")
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
            print("Failed to get sensor data")
            return
        
        print(text)
        tb.csvfile.write("{}, {},{},{},{}\n".format(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), data['temperature'],data['humidity'],data['ambientLight'],data['battery']))

        thunderboards[devId].ble_service.disconnect() # disconnect from the TB2 so it will go back to sleep and save battery power
        # if we have a Thingspeak channel setup, send the data to the respective channel
        if tb.filename in ThingSpeakKeys:
            Post2Thingspeak(ThingSpeakKeys[tb.filename], data['temperature'],data['humidity'],data['ambientLight'],data['battery'])
        else:
            print("failed to find Thingspeak key {}".format(tb.filename))
    return

def RunAction(action):
    message = MakeMessage(device_id, action)
    if not message:
        return
    print('Send data: {} '.format(message))
    event_response = SendCommand(client_sock, message)
    print('Response {}'.format(event_response))


try:
    random.seed()
    RunAction('detach')
    RunAction('attach')

    while True:
        h = 46.0
        t = 74.8

        h = "{:.3f}".format(h)
        t = "{:.3f}".format(t)
        sys.stdout.write(
            '\r >>' + bcolors.CGREEN + bcolors.BOLD +
            'Temp: {}, Hum: {}'.format(t, h) + bcolors.ENDC + ' <<')
        sys.stdout.flush()

        message = MakeMessage(
            device_id, 'event', 'temperature={}, humidity={}'.format(t, h))

        msg_response = SendCommand(client_sock, message, True)
        print('Response {}'.format(msg_response))
        time.sleep(2)


finally:
    print('closing socket', file=sys.stderr)
    client_sock.close()
