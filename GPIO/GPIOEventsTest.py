#!/usr/bin/python
import os

import ConfigParser

config = ConfigParser.ConfigParser()
config.read([os.path.dirname(__file__) + '/../etc/GPIO.conf'])

authMode=not config.get('auth', 'token') in ('0', 'False')

import socket
import sys

sys.path.insert(0, os.path.dirname(__file__) + '/../lib')
from myGPIO import mnemonic

import md5

def getToken():
        #create an INET, STREAMing socket
        a = socket.socket(
                socket.AF_INET, socket.SOCK_STREAM)
        #now connect to the token daemon on custom port
        a.connect((config.get('auth', 'host'), int(config.get('auth', 'port'))))

	a.send('get')
	t = a.recv(64)
	return t


#create an INET, STREAMing socket
s = socket.socket(
    socket.AF_INET, socket.SOCK_STREAM)
#now connect to the daemon listening port
s.connect((config.get('client', 'host'), int(config.get('common', 'port'))))

tr = socket.socket(
    socket.AF_INET, socket.SOCK_STREAM)
#now connect to listen on the event trigger port
tr.bind((config.get('client', 'host'), int(config.get('common', 'pushEventPort'))))
tr.listen(1)

debounce = '10'
if 2 in sys.argv:
	debounce=sys.argv[2]
cmd = 'GPIO.addEvent(' + sys.argv[1] + ',' + str(mnemonic.BOTH) + ',' + debounce + ')'
a = md5.new()
if authMode:
	t = getToken()
	a.update(t)
	a.update(cmd)
	s.send(a.digest() + '::' + cmd + '::' + t)
else:
	# Poor Man Authenticathion SECRET
        pma=config.get('auth', 'pma')

	a.update(pma)
	a.update(cmd)
	s.send(a.digest() + '::' + cmd)
print s.recv(16);

while (1):
        (pushsocket, address) = tr.accept()
	if pushsocket.recv(8) == sys.argv[1]:
		print('[SUCCESS] Event detected')
	else:
		print('[ FAIL! ] Error detected')
