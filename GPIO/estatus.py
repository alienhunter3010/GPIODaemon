#!/usr/bin/python
import os

import ConfigParser

import socket
import sys
import md5
import re
import time

binpath=os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, binpath + '/../lib')

import GPIOClient
from myGPIO import mnemonic

class estatus(GPIOClient.GPIOClient):
	delay=0 
        success = [0, '0', '']
        i=1
        successOutput=False
        failOutput=False
        successValue = True
        failValue=True
	GPIO=False

	def setup(self):
		self.GPIO=mnemonic()

		self.successOutput=self.GPIO.GPIO25
		self.failOutput=self.GPIO.GPIO24

		i = 1
		while i < len(sys.argv):
		        option = sys.argv[i]
		        i+=1
		        if option == '-d':
                		self.delay=int(sys.argv[i])
		        elif option == '-s':
		                self.success.put(sys.argv[i])
		        elif option == '-S':
                		self.success = [sys.argv[i]]
		        elif option == '-so':
                		m = re.search('^([+-]?)(.*)$', sys.argv[i])
		                if m.group(1) == '-':
                		        self.successValue=False
		                self.successOutput = getattr(self.GPIO, m.group(2))
		        elif option == '-fo':
                		m = re.search('^([+-]?)(.*)$', sys.argv[i])
		                if m.group(1) == '-':
                		        self.failValue=False
		                self.failOutput = getattr(self.GPIO, m.group(2))
		        else:
                		continue
	        	i+=1

	def run(self):
		self.sendCommand("system.persistence.on")
		self.sendCommand("GPIO.setup(%d, %d)" % (self.successOutput, self.GPIO.OUT))
		self.sendCommand("GPIO.setup(%d, %d)" % (self.failOutput, self.GPIO.OUT))

		self.sendCommand('GPIO.output(%d, %d)' % (self.successOutput, not self.successValue))
		self.sendCommand('GPIO.output(%d, %d)' % (self.failOutput, not self.failValue))

		blink = False
		if sys.stdin.read().rstrip() in self.success:
		        self.sendCommand('GPIO.output(%d, %d)' % (self.successOutput, self.successValue))
		else:
		        self.sendCommand('GPIO.output(%d, %d)' % (self.failOutput, self.failValue))
		        blink = True
		time.sleep(0.5)
		self.sendCommand('GPIO.output(%d, %d)' % (self.successOutput, not self.successValue))
		self.sendCommand('GPIO.output(%d, %d)' % (self.failOutput, not self.failValue))

		if self.delay:
		        if blink:
		                for j in range(self.delay):
		                        time.sleep(0.5)
                		        self.sendCommand('GPIO.output(%d, %d)' % (self.failOutput, self.failValue))
		                        time.sleep(0.5)
                		        self.sendCommand('GPIO.output(%d, %d)' % (self.failOutput, not self.failValue))
		        else:
        		        time.sleep(self.delay)
		self.sendCommand("system.persistence.off")

o = estatus()
o.setup()
o.run()
