from bluepy.btle import *
import time, datetime

class GoveeDelegate(DefaultDelegate):
    def __init__(self):
        DefaultDelegate.__init__(self)

    def handleDiscovery(self, dev, isNewDev, isNewData):
        # Govee devices (it appears) have MAC addresses that begin with the following string
        if dev.addr[:8]=="a4:c1:38":          
            
            # returns a list, of which the [2] item of the [3] tuple is manufacturing data
            adv_list = dev.getScanData()
            print(adv_list)
            adv_manuf_data = adv_list[3][2]
            print(adv_manuf_data)
            
            #print("manuf data = ", adv_manuf_data)

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

scanner = Scanner().withDelegate(GoveeDelegate())

while True:
    scanner.scan(5.0)