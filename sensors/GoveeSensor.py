from shutil import register_unpack_format


def decode_temp(combined_value: int) -> float:
    """Decode potential negative temperatures and integrated ."""
    # https://github.com/Thrilleratplay/GoveeWatcher/issues/2

    if combined_value & 0x800000: 
        return float(remove_humidity_from(combined_value ^ 0x800000) / -10000.0)
    return float(remove_humidity_from(combined_value) / 10000.0)

def remove_humidity_from(combined_value: int) -> int:
    return combined_value - (combined_value % 1000)

def decode_temp_and_humidity(hex_string: str) -> tuple:
    """Extract temp and humidity from 6 hex digits"""
    value = int(hex_string, 16) 
    humidity = float((value % 1000) / 10.0) # rh % is the last 3 digits divided by 10
    temp_C = decode_temp(value)
    return (temp_C, humidity)

class GoveeReading:
    # Takes a discovered device from bleak BleakScanner.discover()
    def __init__(self, device, advertisement):
        self.name = device.name
        self.address = device.address
        self.data = advertisement.manufacturer_data[1]

    def model(self):
        return self.name[3:7]

    def readings(self):
        if self.model() == "5101":
            return self.decode_5101()
        # support for more sensor types will be added here
    def battery(self):
        return list(self.data)[5]

    def temp_F(self):
        temp_C, humidity = decode_temp_and_humidity(self.data.hex()[4:10])   
        return (temp_C * 9/5) + 32 

    def decode_5101(self):
        temp_C, humidity = decode_temp_and_humidity(self.data.hex()[4:10])
        battery = list(self.data)[5] # battery % is last byte converted to integer
        return (temp_C, humidity, battery)
 
