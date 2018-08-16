Source code used for reading sensor values can be found in folloing repository
https://github.com/acaird/raspi-scale

NOTE: Above source code is broken and contains lot of redundant code. 
I had to debug and fix the code to make it work

Instructions to use the code edited by us:
1. Copy all the files in device_code directory and place it in the folder that contains 
your certificate files, public and private key files. 
2. Sensor.py contains the AWS IoT client main functionality
3. Scaledity.py contains the readSensorValue logic. If you want to change the logic 
to process sensor values, please do so in this file.
4. scaleConfig.py contains all the configuration setting for the sensor values
5. scale-raw.py can be used to test the initial setup of the force sensor