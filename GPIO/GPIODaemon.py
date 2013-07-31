import os
import ConfigParser

import socket
import sys
import traceback

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
	secret=''
	setupMap = {}
	eventsMap = {}
	pwmMap = {}
	persistence=False
	serversocket=False
	mnemo=False
	

	def reload(self):
		# Take it easy and send a client command to the running daemon
		# (please remember that resident daemon and service request are two distinct processes!)
		import GPIOClient
		c = GPIOClient.GPIOClient()
		c.sendCommand('system.reload')

	def setup(self):
		self.config = ConfigParser.ConfigParser()
                self.config.read([binpath + '/../etc/GPIO.conf'])

		self.tokenMode=not self.config.get('auth', 'token') in ('0', 'False')
                self.secret=self.config.get('auth', 'secret')
                
                if self.serversocket:
                        self.serversocket.shutdown(socket.SHUT_RDWR)
                        self.serversocket.close()
		else: # First run
			GPIO.setmode(GPIO.BOARD)
	                GPIO.setwarnings(False)
                #create an INET, STREAMing socket
                self.serversocket = socket.socket(
                    socket.AF_INET, socket.SOCK_STREAM)
                #bind the socket to a public host,
                # and the daemon port
		self.serversocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                self.serversocket.bind(('', int(self.config.get('common', 'port')))) 
                #become a server socket, GPIO is ONE, so we accept only 1 connection at a time!
                self.serversocket.listen(1)

		self.mnemo = mnemonic()

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

	def cleanup(self):
		GPIO.cleanup()
                self.setupMap = {}
                self.eventsMap = {}
                self.pwmMap = {}

	def run(self):
		self.setup()

		while 1:
			if not self.persistence:
				#accept connections from outside
				(clientsocket, address) = self.serversocket.accept()
			#now do something with the clientsocket
			a = md5.new()
			if self.tokenMode:
				(auth, input, token) = clientsocket.recv(4096).split('::')
				if self.checkToken(token) == False:
					clientsocket.send('-4')
					continue
				a.update(token)
			else:
				(auth, input) = clientsocket.recv(4096).split('::')
			a.update(self.secret)
			a.update(input)
			if (a.digest() != auth):
				clientsocket.send('-4')
				continue
			if input=='system.quit':
				self.cleanup()
				clientsocket.send('0')
				exit()
			elif input=='system.reload':
				self.setup()
				continue
			elif input=='system.persistence.on':
				self.persistence=True
				clientsocket.send('0')
				continue
			elif input=='system.persistence.off':
                                self.persistence=False
                                clientsocket.send('0')
                                continue
			elif input=='GPIO.cleanup':
				self.cleanup()
				clientsocket.send('0')
                                continue
			try:
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

					# PWM
					elif m.group(1) == 'addPWM':
						if int(params[0]) in self.pwmMap:
							if self.config.get('common', 'debug'):
	                                                        for k in self.pwmMap.keys():
        	                                                        print "%d : %s" % (k, self.pwmMap[k])
                                                        # just existing event!
                                                        clientsocket.send('-1')
                                                        continue
						# All PWM are output
                                                self.autoSetup(int(params[0]), GPIO.OUT)
						self.pwmMap[int(params[0])] = (address[0], GPIO.PWM(int(params[0]), float(params[1])))
						if len(params) == 3:
							self.pwmMap[int(params[0])][1].start(float(params[2]))
						print "dc: %f; %f Hz owner: %s" % (float(params[1]), float(params[2]), address[0])
						clientsocket.send('0')
					elif m.group(1) == 'delPWM':
                                                if int(params[0]) in self.pwmMap and self.pwmMap[int(params[0])][0] == address[0]:
                                                        self.pwmMap[int(params[0])][1].stop()
							del self.pwmMap[int(params[0])]
                                                        clientsocket.send('0')
                                                else:
                                                        clientsocket.send('-1')
					elif m.group(1) == 'startPWM':
                                                if int(params[0]) in self.pwmMap and self.pwmMap[int(params[0])][0] == address[0]:
                                                        self.pwmMap[int(params[0])][1].start(float(params[1]))
                                                        clientsocket.send('0')
                                                else:
                                                        clientsocket.send('-1')
					elif m.group(1) == 'stopPWM':
                                                if int(params[0]) in self.pwmMap and self.pwmMap[int(params[0])][0] == address[0]:
                                                        self.pwmMap[int(params[0])][1].stop()
                                                        clientsocket.send('0')
                                                else:
                                                        clientsocket.send('-1')
					elif m.group(1) == 'dutyCyclePWM':
                                                if int(params[0]) in self.pwmMap and self.pwmMap[int(params[0])][0] == address[0]:
                                                        self.pwmMap[int(params[0])][1].ChangeDutyCycle(float(params[1]))
                                                        clientsocket.send('0')
                                                else:
                                                        clientsocket.send('-1')
					elif m.group(1) == 'freqPWM':
                                                if int(params[0]) in self.pwmMap and self.pwmMap[int(params[0])][0] == address[0]:
                                                        self.pwmMap[int(params[0])][1].ChangeFrequency(float(params[1]))
                                                        clientsocket.send('0')
                                                else:   
                                                        clientsocket.send('-1')

					# Events
					elif m.group(1) == 'addEvent':
						if int(params[0]) in self.eventsMap:
							if self.config.get('common', 'debug'):
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
							del self.eventsMap[int(params[0])]
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
					elif m.group(1) == 'batch':
						for p in params:
							c=re.search('([s\-\+]?)([0-9\.]+)', p)
							if c.group(1) == 's':
								time.sleep(float(c.group(2)))
							else:
								self.autoSetup(int(c.group(2)), GPIO.OUT)
								if c.group(1) == '-':
		                                                	GPIO.output(int(c.group(2)), 0)
								else:
									GPIO.output(int(c.group(2)), 1)
						clientsocket.send('0')
					else:
						clientsocket.send('-1')
					continue
			except:
				if self.config.get('common', 'debug'):
					traceback.print_exc(file=sys.stdout)
				clientsocket.send('-2')
				continue
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
        Daemon.Daemon.manage(daemon)
