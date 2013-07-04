import os
import socket
import sys
sys.path.insert(0, os.path.dirname(__file__) + '/../lib')

import ConfigParser
config = ConfigParser.ConfigParser()
config.read([os.path.dirname(__file__) + '/../etc/tokens.conf'])


import Daemon

import uuid
import time
import random

class TokensDaemon(Daemon.Daemon):
	activeTokens = {}
	validity = 1

	def run(self):
		self.validity = int(config.get('server', 'tokenValiditySecs'))

		#create an INET, STREAMing socket
		serversocket = socket.socket(
		    socket.AF_INET, socket.SOCK_STREAM)
		#bind the socket to a public host,
		# and a well-known port
		serversocket.bind(('', int(config.get('common', 'port'))))
		serversocket.listen(5)

		while 1:
			#accept connections from outside
			(clientsocket, address) = serversocket.accept()
			#now do something with the clientsocket
			query = clientsocket.recv(4096)
			if query=='quit':
				exit()
			elif query=='get':
				r=str(uuid.uuid4())
				clientsocket.send(r)
				self.activeTokens[r] = time.time()
				continue
			elif query=='debug':
				if config.get('server', 'debug') == '1':
					print "On stack: %d" % len(self.activeTokens)
				continue
			(cmd, arg) = query.split(':', 2)
			if cmd=='auth':
				if arg in self.activeTokens:
					if time.time() - self.activeTokens[arg] < self.validity:
						clientsocket.send('0')
					else:
						clientsocket.send('2')
					del self.activeTokens[arg]
				else:
					clientsocket.send('1')
					
			else:
				clientsocket.send('-1')
			if random.randint(0,9) == 0:
				for k in self.activeTokens.keys():
					if time.time() - self.activeTokens[k] > self.validity:
						del self.activeTokens[k]

if __name__ == "__main__":
        daemon = TokensDaemon('/tmp/tokens.pid')
	Daemon.Daemon.manage(daemon)
	"""
        if len(sys.argv) == 2:
                if 'start' == sys.argv[1]:
                        daemon.start()
                elif 'stop' == sys.argv[1]:
                        daemon.stop()
                elif 'restart' == sys.argv[1]:
                        daemon.restart()
                else:
                        print "Unknown command"
                        sys.exit(2)
                sys.exit(0)
        else:
                print "usage: %s start|stop|restart" % sys.argv[0]
                sys.exit(2)
	"""
