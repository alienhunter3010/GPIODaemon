import sys
sys.path.insert(0, '../lib')

import time
import myGPIO
import RPi.GPIO as GPIO

print "GPIO.PUD_UP %d" % GPIO.PUD_UP
print "GPIO.PUD_DOWN %d" % GPIO.PUD_DOWN
o = myGPIO.mnemonic()

myRed=getattr(o, 'GPIO24')
myGreen=o.GPIO25
myBlue=o.GPIO8

GPIO.setup(myRed, GPIO.OUT)
GPIO.setup(myGreen, GPIO.OUT)
GPIO.setup(myBlue, GPIO.OUT)

GPIO.output(myRed, False)
GPIO.output(myGreen, True)
GPIO.output(myBlue, True)

for i in range(1,6):
	time.sleep(1)
	GPIO.output(myRed, (i % 2))
time.sleep(1)
GPIO.output(myBlue, False)
time.sleep(2)
GPIO.output(myBlue, True)
GPIO.output(myGreen, False)
time.sleep(2)
GPIO.output(myGreen, True)
