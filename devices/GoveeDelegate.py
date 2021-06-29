import asyncio
from bleak import *
import time, datetime
from struct import unpack_from

class GoveeDelegate:

    def handleDiscovery(self, dev, isNewDev, isNewData):
        # Govee devices (it appears) have MAC addresses that begin with the following string
        if (dev.addr[:8]=="a4:c1:38" and isNewData):          
            
            # returns a list, of which the [2] item of the [3] tuple is manufacturing data
            adv_list = dev.getScanData()
            print(adv_list)
            adv_manuf_data = adv_list[3][2]
            print("manuf data = ", adv_manuf_data)

            #this is the location of the encoded temp/humidity and battery data
            temp_hum_data = adv_manuf_data[6:12]
            battery = adv_manuf_data[12:14]
            
            #convert to integer
            if temp_hum_data == '': return
            val = (int(temp_hum_data, 16))

            #decode tip from eharris: https://github.com/Thrilleratplay/GoveeWatcher/issues/2
            is_negative = False
            temp_C = 500
            humidity = 500
            if (val & 0x800000):
                is_negative = True
                val = val ^ 0x800000
            try:
                humidity = (val % 1000) / 10
                temp_C = int(val / 1000) / 10
                if (is_negative):
                    temp_C = 0 - temp_C
            except:
                print("issues with integer conversion")
            print(temp_C)

            try:
                battery_percent = int(battery) / 64 * 100
            except:
                battery_percent = 200
            battery_percent = round(battery_percent)

            temp_F = round((temp_C*9/5)+32, 1)

            try:
                hum_percent = ((int(temp_hum_data, 16)) % 1000) / 10
            except:
                hum_percent = 200
            hum_percent = round(hum_percent)
            signal = dev.rssi
            print("temp: {} degF, rh: {}%, battery: {}%, device: {}".format(temp_F, hum_percent, battery_percent, dev.addr[12:17]))

async def run():
    devices = await BleakScanner.discover()
    for d in devices:
        print(d, d.address, type(d.address))
        if d.address[:8]=="A4:C1:38":
            print(d.metadata)
            mfg_data = d.metadata['manufacturer_data'][1]
            temp_C, humidity, battery = decode_5101(mfg_data)
            print("temp: {} degC, rh: {}%, battery: {}%".format(temp_C, humidity, battery))

def decode_5101(bytestring):
    useful_data = list(bytestring)[2:] # convert to integers and drop first 2 terms
    battery = useful_data[3]
    temp_and_humid_hexstr = "".join(map(myhex, useful_data[0:3])) # TODO: account for case where first term is two hex digits
    t_and_h_int = int(temp_and_humid_hexstr, 16)
    temp_C = t_and_h_int / 10000.0 
    humidity = (t_and_h_int % 1000) / 10.0
    return (temp_C, humidity, battery)


def myhex(decimal_integer):
    return hex(decimal_integer).replace('0x', '')

loop = asyncio.get_event_loop()
loop.run_until_complete(run())