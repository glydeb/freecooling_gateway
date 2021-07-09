from __future__ import print_function
from sensors.GoveeSensor import GoveeReading

import sys
import socket
import time, datetime
import asyncio
import bcolors
from btle_scanner import SensorScanner

class Publisher:
    def __init__(self, address, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.address = address
        self.port = port
        self.device_name = ''

    async def process(self, reading: GoveeReading):
        if self.current_device_name != reading.device_name:
            await self.switch_devices(self.device_name, reading.name)
        message = self.format_event(reading)

        print('Send data: {} '.format(message))
        response = await self.send(message, True)
        return response

    async def send(self, message, log=True):
        """ returns message received """
        if log:
            print('sending: "{}"'.format(message), file=sys.stderr)

        self.socket.sendto(message.encode('utf8'), self.address)

        # Receive response
        if log:
            print('waiting for response', file=sys.stderr)

        response, _ = await self.socket.recvfrom(4096)

        if log:
            print('received: "{}"'.format(response), file=sys.stderr)

        return response

    def format_event(self, sensor: GoveeReading):
        temp_C, humidity, battery = sensor.readings()
        sys.stdout.write(
            '\r >>' + bcolors.CGREEN + bcolors.BOLD +
            'Temp: {}, Hum: {}'.format(temp_C, humidity) + bcolors.ENDC + ' <<')
        sys.stdout.flush()

        data = f'temperature={temp_C}, humidity={humidity}'
        return f'{{ "device" : "{sensor.name}", "action":"event", "data" : "{data}" }}'

    def format_other(self, sensor: GoveeReading, action):
        return f'{{ "device" : "{sensor.name}", "action":"{action}" }}'

    async def switch_devices(self, old, new):
        if self.device_name != '':
            detach_message = self.format_other(old, 'detach')
            await self.send(detach_message)
        attach_message = self.format_other(new, 'attach')
        await self.send(attach_message)

async def main():
    ADDR = '192.168.0.109'
    PORT = 10000

    # Create the publisher
    publisher = Publisher(ADDR, PORT)

    # create scanner
    btle = SensorScanner(30.0) # scan for 30 seconds at a time
    
    try:
        while True:
            if len(btle.readings) > 0:
                reports = btle.clear_readings()
                for reading in reports:
                    publisher.process(reading)

            await btle.scan()

    finally:
        print('closing socket', file=sys.stderr)
        publisher.socket.close()

if __name__ == "__main__":
    asyncio.run(main())
