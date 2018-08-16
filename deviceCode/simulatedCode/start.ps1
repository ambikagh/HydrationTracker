# requires: Python, PowerShell, Permission to run PS scripts
# permissions for this PS session only:   Set-ExecutionPolicy -ExecutionPolicy Bypass -Scope Process

# exit if cmdlet gives error
$ErrorActionPreference = "Stop"

# Check to see if root CA file exists, download if not
If (!(Test-Path ".\root-CA.crt")) {
    "`nDownloading AWS IoT Root CA certificate from Symantec..."
    Invoke-WebRequest -Uri https://www.symantec.com/content/en/us/enterprise/verisign/roots/VeriSign-Class%203-Public-Primary-Certification-Authority-G5.pem -OutFile root-CA.crt
}

# install AWS Device SDK for NodeJS if not already installed
If (!(Test-Path ".\aws-iot-device-sdk-python")) {
    "`nInstalling AWS SDK..."
    git clone https://github.com/aws/aws-iot-device-sdk-python
    cd aws-iot-device-sdk-python
    python setup.py install
    cd ..
}

"`nRunning pub/sub sample application..."
#python aws-iot-device-sdk-python\samples\basicPubSub\basicPubSub.py -e amkfuekfishrc.iot.us-west-2.amazonaws.com -r root-CA.crt -c ambisurface.cert.pem -k ambisurface.private.key

python aws-iot-device-sdk-python\hydratrack\basicPubSub.py -e amkfuekfishrc.iot.us-west-2.amazonaws.com -r root-CA.crt -c ambisurface.cert.pem -k ambisurface.private.key