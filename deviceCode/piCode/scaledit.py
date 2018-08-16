#!/usr/bin/env python
from daemonify import Daemon
import datetime
import yaml
import shelve
import logging
import scaleConfig
import argparse
import sys


'''
This is mostly from:
https://learn.adafruit.com/
   reading-a-analog-in-and-controlling-audio-volume-with-the-raspberry-pi/
   script

(git://gist.github.com/3151375.git)

With some modifications by me that should have been other
commits, but weren't, so sorry, you'll have to diff it yourself
if you want to see what changed.

I have no idea what the license is on the original, so I have no
idea what the license on this is.  Personally, I don't care, but
Adafruit might.
'''
last_read = 0
class Scale(Daemon):

	def start(self):
		print("in child..")
		super

        # read SPI data from MCP3008 chip, 8 possible adc's (0 thru 7)
        def readadc(self,adcnum, clockpin, mosipin, misopin, cspin):
                if ((adcnum > 7) or (adcnum < 0)):
                        return -1
                GPIO.output(cspin, True)

                GPIO.output(clockpin, False)  # start clock low
                GPIO.output(cspin, False)     # bring CS low

                commandout = adcnum
                commandout |= 0x18  # start bit + single-ended bit
                commandout <<= 3    # we only need to send 5 bits here
                for i in range(5):
                        if (commandout & 0x80):
                                GPIO.output(mosipin, True)
                        else:
                                GPIO.output(mosipin, False)
                        commandout <<= 1
                        GPIO.output(clockpin, True)
                        GPIO.output(clockpin, False)

                adcout = 0
                # read in one empty bit, one null bit and 10 ADC bits
                for i in range(12):
                        GPIO.output(clockpin, True)
                        GPIO.output(clockpin, False)
                        adcout <<= 1
                        if (GPIO.input(misopin)):
                                adcout |= 0x1

                GPIO.output(cspin, True)

                adcout >>= 1       # first bit is 'null' so drop it
               # print(adcout)
		return adcout

        def initialize(self):
                configFile = './scaleConfig.yaml'

                parser = argparse.ArgumentParser()
##                parser.add_argument ("-d", "--debug", type=int, choices=[0,1],
##                                     nargs='?', const=1,
##                                     help="turn debugging on (1) or off (0); this overrides"+
##                                     "the value in the configuration file ")
##                parser.add_argument("-c","--config", action="store", dest="configFile",
##                                    help="specify a configuration file")

                #args = parser.parse_args()
                args = argparse.Namespace()


                loggingconfigFile = configFile

                cfg = scaleConfig.readConfig(configFile)
                DEBUG = cfg['raspberryPiConfig']['debug']

                if DEBUG:
                        logging.basicConfig(level=logging.DEBUG,format='%(asctime)s %(message)s')
                else:
                        logging.basicConfig(filename="scale.log",level=logging.DEBUG,
                                            format='%(asctime)s %(message)s')

                logging.debug("Initializing.")

                if not cfg['raspberryPiConfig']['alertChannels']:
                        cfg['raspberryPiConfig']['alertChannels'] = ''
                if not cfg['raspberryPiConfig']['updateChannels']:
                        cfg['raspberryPiConfig']['updateChannels'] = ''

                import time
                import os
                import RPi.GPIO as GPIO

                global GPIO
                GPIO.setmode(GPIO.BCM)
                GPIO.setwarnings(False) # to stop the "This channel is already in use" warning

                # change these as desired - they're the pins connected from the
                # SPI port on the ADC to the Cobbler
                # ADCPort    Cobbler
                # -------- ----------
                args.SPICLK    =    cfg['raspberryPiConfig']['ADCtoCobbler']['SPICLK']
                args.SPIMISO   =    cfg['raspberryPiConfig']['ADCtoCobbler']['SPIMISO']
                args.SPIMOSI   =    cfg['raspberryPiConfig']['ADCtoCobbler']['SPIMOSI']
                args.SPICS     =    cfg['raspberryPiConfig']['ADCtoCobbler']['SPICS']
                # Diagram of ADC (MCP3008) is at:
                #   https://learn.adafruit.com/
                #     reading-a-analog-in-and-controlling-audio-volume-with-the-raspberry-pi/
                #     connecting-the-cobbler-to-a-mcp3008

                # set up the SPI interface pins
                GPIO.setup(args.SPIMOSI, GPIO.OUT)
                GPIO.setup(args.SPIMISO, GPIO.IN)
                GPIO.setup(args.SPICLK, GPIO.OUT)
                GPIO.setup(args.SPICS, GPIO.OUT)

                # FSR connected to adc #0
                args.fsr_adc = cfg['raspberryPiConfig']['adcPortWithFSR']

                # to keep from being jittery we'll only change when the FSR has moved
                # more than this many 'counts'
                args.tolerance = cfg['raspberryPiConfig']['tolerance']

                # not ideal, but at least it's just in one place now
                args.logString = '{0} {1}\tfsr: {2:4d}\tlast_value: {3:4d}\tchange: {4:4d}\tbeans: {5}'

                oTime = cfg['raspberryPiConfig']['updateTime']

                while cfg['raspberryPiConfig']['updateTime'] % cfg['raspberryPiConfig']['checkTime']:
                        cfg['raspberryPiConfig']['updateTime'] += 1

                if oTime != cfg['raspberryPiConfig']['updateTime']:
                        logging.debug ("\"updateTime\" changed from %s to %s so it would divide evenly by \"checkTime\".",
                                       oTime, cfg['raspberryPiConfig']['updateTime'])

                # This totally isn't a clock, it's a counter.  But we use it sort of
                # like a clock.
                args.scaleClock = 0

                # Python shelves let us keep some state between runs; in this case, we
                # are keeping the state of the alerts we have generated, so we don't
                # re-send emails or tweets if one has already been sent for a given
                # state
                args.alertState = shelve.open("scaleState.db", writeback=True)
                for alert in cfg['raspberryPiConfig']['alertChannels']:
                        if alert not in args.alertState:
                                args.alertState[alert] = 0

                logging.debug ("Ready.")
                #print("initialize_eding")
                return args,cfg

        def mainLoop(self,args,cfg,value):

                global last_read
                import time
    		flag = True
                while True:

                        # read the analog pin
                        fsr = self.readadc(args.fsr_adc, args.SPICLK, args.SPIMOSI, args.SPIMISO, args.SPICS)
                        # how much has it changed since the last read?
                        fsr_change = (fsr - last_read)

      			if fsr_change == 0 and flag == False:
			        beans = int((fsr/1024.)*100)
			        logging.debug(args.logString.format(currentTime, "CHANGE",fsr, last_read,fsr_change, beans))
				flag = True
				return fsr
			        if value == 0:
					print("fsr = {0}".format(fsr))
                                        return fsr
                                else:
					print("fsr = {0}, value = {1}".format(fsr, value))
                                        value = fsr - value
                                        value = (value / 30) * 2
					print("value after change = {0}".format(value))
                                        return value
  
         
    # print(fsr_change)
                        currentTime = str(datetime.datetime.now()).split('.')[0]

                        if fsr_change > cfg['raspberryPiConfig']['maxChange'] and ( abs(fsr_change) > args.tolerance ):
                                last_read = fsr
                                beans = int((fsr/1024.)*100)
                                logging.debug (args.logString.format(currentTime, "CHANGE",
                                                                     fsr, last_read,
                                                                     fsr_change, beans))
			        flag = False

                        # if args.scaleClock % cfg['raspberryPiConfig']['updateTime'] == 0:
                                # last_read = fsr
                                # beans = int((fsr/1024.)*100)
                                # logging.debug (args.logString.format(currentTime, "UPDATE",
                                                                     # fsr, last_read,
                                                                     # fsr_change, beans))

                        args.scaleClock += cfg['raspberryPiConfig']['checkTime']

                        time.sleep(cfg['raspberryPiConfig']['checkTime'])
        def run(self):
                args,cfg = self.initialize()
                self.mainLoop(args,cfg)

def readSensorValue(value):

  #sys.path.insert(0, '/home/pi/Documents/hydra-track/aws-iot-device-sdk-python/samples/basicPubSub')
  #import basicPubSub

        #import scalePlotly
        #import scaleTwitter
        #import scaleEmail
        #import scaleAlerts


        pidfile = "/tmp/scale.pid"
        myS = Scale(pidfile)

        myS.start()

        args,cfg = myS.initialize()
        return myS.mainLoop(args,cfg,value)
