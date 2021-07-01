import struct

def decode_temp(packet_value: int) -> float:
    """Decode potential negative temperatures."""
    # https://github.com/Thrilleratplay/GoveeWatcher/issues/2

    if packet_value & 0x800000: 
        return float((packet_value ^ 0x800000) / -10000)
    return float(packet_value / 10000)

def decode_temp_and_humidity(hex_string: str) -> tuple:
    """Extract temp and humidity from 6 hex digits"""
    print("in decode temp and humidity")
    value = int(hex_string, 16) 
    humidity = float((value % 1000) / 10.0) # rh % is the last 3 digits divided by 10
    temp_C = decode_temp(value)
    print(temp_C, humidity)
    return (temp_C, humidity)

class GoveeSensor:
    # Takes a discovered device from bleak BleakScanner.discover()
    def __init__(self, device):
        self.name = device.name
        self.address = device.address
        self.data = device.metadata['manufacturer_data'][1]

    def type(self):
        return self.name[3:7]

    def readings(self):
        if self.type() == "5101":
            return self.decode_5101()
        # support for more sensor types will be added here

    def decode_5101(self):
        print("in decode 5101")
        print(self.data.hex())
        print(list(self.data))
        temp_C, humidity = decode_temp_and_humidity(self.data.hex()[4:10])
        battery = list(self.data)[5] # battery % is last byte converted to integer
        return (temp_C, humidity, battery)
 
