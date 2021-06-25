import struct

def getLocalName(scandata):
    return scandata[1] == 'Complete Local Name'

class GoveeSensor:

    def __init__(self, scanData, connection):
        self.properties = dict()
        self.name = filter(getLocalName, scanData)[1]
        self.connection = connection # A bluepy Peripheral object

    def refreshReadings(self):
        properties = self.connection.getCharacteristics()
        print(list(properties))


