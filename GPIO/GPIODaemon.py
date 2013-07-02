import os
import ConfigParser

import socket
import sys

binpath=os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, binpath + '/../lib')

from myGPIO import mnemonic
import RPi.GPIO as GPIO
import Daemon

import re
import md5
import time

class GPIODaemon(Daemon.Daemon):
	config=False
	tokenMode=True
	pma=''
	setupMap = {}
	eventsMap = {}
	persistence=False

	def init(self):
		self.config = ConfigParser.ConfigParser()
                self.config.read([binpath + '/../etc/GPIO.conf'])

	def checkToken(self, token):
		#create an INET, STREAMing socket
	        s = socket.socket(
        	        socket.AF_INET, socket.SOCK_STREAM)
	        #now connect to the daemon on custom port
	        s.connect((self.config.get('auth', 'host'), int(self.config.get('auth', 'port'))))

		s.send('auth:' + token)
		if s.recv(8) == '0':
			return True
		return False

	def eventTrigger(self, channel):
		if channel in self.eventsMap:
			pushsocket = socket.socket(
	                    socket.AF_INET, socket.SOCK_STREAM)
        	        #connect the socket to the event's owner host,
	                pushsocket.connect((self.eventsMap[int(channel)], int(self.config.get('common', 'pushEventPort')) ))
			#TODO: auth stuff
			pushsocket.send(str(channel))
		else:
			#error
			print 'Error Triggering event, eventMap entry does not exists!?'

	def run(self):
		self.tokenMode=not self.config.get('auth', 'token') in ('0', 'False')
		if not self.tokenMode:
		        # Poor Man Secret (copy it on your client script, too!)
		        self.pma=self.config.get('auth', 'pma')

		o=mnemonic()

		#create an INET, STREAMing socket
		serversocket = socket.socket(
		    socket.AF_INET, socket.SOCK_STREAM)
		#bind the socket to a public host,
		# and the daemon port
		serversocket.bind(('', int(self.config.get('common', 'port'))))
		#become a server socket, GPIO is ONE, so we accept only 1 connection at a time!
		serversocket.listen(1)

		while 1:
			if not self.persistence:
				#accept connections from outside
				(clientsocket, address) = serversocket.accept()
			#now do something with the clientsocket
			(auth, input, token) = clientsocket.recv(4096).split('::')
			a = md5.new()
			if self.tokenMode:
				if self.checkToken(token) == False:
					clientsocket.send('-4')
					continue
				a.update(token)
			else:
				a.update(self.pma)
			a.update(input)
			if (a.digest() != auth):
				clientsocket.send('-4')
				continue
			if input=='system.quit':
				exit()
			elif input=='system.persistence.on':
				self.persistence=True
				clientsocket.send('0')
				continue
			elif input=='system.persistence.off':
                                self.persistence=False
                                clientsocket.send('0')
                                continue
			#try:
			if True:
				m = re.search('^GPIO\.([a-zA-Z]+)\(([^\)]+)\)$', input)
				if m is not None:
					params=m.group(2).split(',')
					# Basic commands
					if m.group(1) == 'setup':
						if len(params) == 3:
							GPIO.setup(int(params[0]), int(params[1]), pull_up_down=int(params[2]))
						else:
							GPIO.setup(int(params[0]), int(params[1]))
						clientsocket.send('0')
					elif m.group(1) == 'output':
						self.autoSetup(int(params[0]), GPIO.OUT)
						GPIO.output(int(params[0]), int(params[1]))
						clientsocket.send('0')
					elif m.group(1) == 'input':
						self.autoSetup(int(params[0]), GPIO.IN)
						clientsocket.send(str(GPIO.input(int(params[0]))))

					# Events
					elif m.group(1) == 'addEvent':
						if int(params[0]) in self.eventsMap:
							for k in self.eventsMap.keys():
								print "%d : %s" % (k, self.eventsMap[k])
							# just existing event!
							clientsocket.send('-1')
							continue 
						# All events are input events
						self.autoSetup(int(params[0]), GPIO.IN)
						if len(params) == 3:
							GPIO.add_event_detect(int(params[0]), int(params[1]), bouncetime=int(params[2]), callback=self.eventTrigger)
						else:
							GPIO.add_event_detect(int(params[0]), int(params[1]), callback=self.ventTrigger)
						self.eventsMap[int(params[0])] = address[0] # The Event is OWNED by the request client!
						clientsocket.send('0')
					elif m.group(1) == 'delEvent':
						if int(params[0]) in self.eventsMap and self.eventsMap[int(params[0])] == address[0]:
							GPIO.remove_event_detect(int(params[0]))
							clientsocket.send('0')
						else:
							clientsocket.send('-1')

					# Enhanced commands
					elif m.group(1) == 'blink':
						try:
				                        pid = os.fork()
				                        if pid > 0:
								clientsocket.send('0')
                                				# parent stuff finished, listen again
				                                continue
							self.enableAtExit=False
							self.blink(params)
							exit()
				                except OSError, e:
							# not forked blink, main process listen STOPS until it ends
							clientsocket.send('1')
							self.blink(params)
					else:
						clientsocket.send('-1')
					continue
			#except:
			#	clientsocket.send('-2')
			#	continue
			clientsocket.send('-1')

	def blink(self, params):
		self.autoSetup(int(params[1]), GPIO.OUT)
		active = 1;
		if len(params) == 3:
			active = int(params[2])
		for i in range(0, int(params[0])):
                	GPIO.output(int(params[1]), active)
			time.sleep(0.5)
			GPIO.output(int(params[1]), not active)
			time.sleep(0.5)

	def autoSetup(self, port, type):
		if port in self.setupMap:
			if self.setupMap[port] == type:
				return
		GPIO.setup(port, type)
		self.setupMap[port] = type
		

if __name__ == "__main__":
	daemon = GPIODaemon('/tmp/gpiod.pid')
	daemon.init()
        Daemon.Daemon.manage(daemon)
