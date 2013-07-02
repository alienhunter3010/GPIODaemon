#!/usr/bin/python
import os
import socket
import sys
sys.path.insert(0, os.path.dirname(__file__) + '/../lib')

import ConfigParser
config = ConfigParser.ConfigParser()
config.read([os.path.dirname(__file__) + '/../etc/tokens.conf'])

import time
import random

def getFreshSocket():
	#create an INET, STREAMing socket
	s = socket.socket(
		socket.AF_INET, socket.SOCK_STREAM)
	#now connect to the daemon on port 5050
	s.connect((config.get('client', 'host'), int(config.get('common', 'port'))))
	return s

s = getFreshSocket()
s.send('get')
t = s.recv(64)
print t
s.close()

w=random.randint(1, int(config.get('server', 'tokenValiditySecs'))+2)
time.sleep(w)

s = getFreshSocket()
s.send('auth:' + t)
r = s.recv(8)
print "%s after %d secs" % (r, w)
