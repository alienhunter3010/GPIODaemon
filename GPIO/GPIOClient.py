#!/usr/bin/python
import os

import ConfigParser

import socket
import sys
import md5

class GPIOClient():
	config=False
	authMode=False
	pma=False
	service=False

	def __init__(self):
		self.config = ConfigParser.ConfigParser()
		self.config.read([os.path.dirname(os.path.abspath(__file__)) + '/../etc/GPIO.conf'])

		self.authMode=not self.config.get('auth', 'token') in ('0', 'False')
		if not self.authMode:
			# Poor Man Authenticathion SECRET
                        self.pma=self.config.get('auth', 'pma')

		#create an INET, STREAMing socket
		self.service = socket.socket(
		    socket.AF_INET, socket.SOCK_STREAM)
		#now connect to the GPIO server on custom port
		self.service.connect((self.config.get('client', 'host'), int(self.config.get('common', 'port'))))

	def getToken(self):
        	#create an INET, STREAMing socket
	        a = socket.socket(
        	        socket.AF_INET, socket.SOCK_STREAM)
	        #now connect to the token daemon on custom port
        	a.connect((self.config.get('auth', 'host'), int(self.config.get('auth', 'port'))))

		a.send('get')
		t = a.recv(64)
		return t

	def sendCommand(self, command):
		a = md5.new()
		payload = [command]
		if self.authMode:
			t = self.getToken()
			a.update(t)
			payload.append(t)
		else:
			a.update(self.pma)
		a.update(command)
		payload.insert(0, a.digest())
		self.service.send('::'.join(payload))
		if self.config.get('common', 'debug'):
			print self.service.recv(64)

if __name__ == "__main__":
	o = GPIOClient()
	o.sendCommand(sys.argv[1])
