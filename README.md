# Free Cooling Gateway

A python app to use a raspberry pi with bluetooth as a gateway to Google IoT Core for the Govee H5101 Temp & Humidity sensor

Uses bleak to scan for the GVH5101 - credit to the code of https://github.com/Thrilleratplay/GoveeWatcher and https://github.com/tsaitsai/govee_bluetooth_gateway for help with the scanning and publishing, as well as the tutorial for GCS Iot Core/Pubsub.

Still in the development stages; my latest achievement is successfully getting data from my two devices from my laptop running Ubuntu.  Next step is transferring it over to the pi and seeing if it works from there, as well.