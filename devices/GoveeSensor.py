import struct

def getLocalName(scandata):
    for (adtype, desc, value) in scandata:
         if (desc == 'Complete Local Name'):
            return value

class GoveeSensor:

    def __init__(self, scanData, connection):
        self.properties = dict()
        self.name = getLocalName(scanData)
        self.connection = connection # A bluepy Peripheral object

    def refreshReadings(self):
        properties = self.connection.getCharacteristics()

        for property in properties:
            if property.supportsRead():
                print("uuid: {}, value: {}".format(property['uuid'], property.read()))


