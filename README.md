# Free Cooling Gateway

A python app to use a raspberry pi with bluetooth as a gateway to Google IoT Core for the Govee H5101 Temp & Humidity sensor

Uses bleak to scan for the GVH5101 - credit to the code of https://github.com/Thrilleratplay/GoveeWatcher and https://github.com/tsaitsai/govee_bluetooth_gateway for help with the scanning and publishing, as well as the tutorial for GCS Iot Core/Pubsub.

## Program flow

Google cloud services pub/sub has a minimum message size of 1000 bytes, so it makes sense to aggregate readings. I've chosen five minutes as the minimum time between publishes; that should be enough granularity to both respond to changing conditions in a timely manner, but not flood the system with too much activity.

1. scan every 30 seconds for 15 seconds
2. aggregate results by device
3. at the end of 5 minutes:
    a. pause scanning
    b. load aggregated results
    c. clear aggregated results
    d. resume scanning
    e. connect to GCS
    f. publish aggregated results through IoT core to PubSub