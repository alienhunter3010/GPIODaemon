import os

class mnemonic():

	SDA0=3
	GPIO0=3
	SCL1=5
	GPIO1=5
	GPIO7=7
	TXD=8
	GPIO14=8
	RXD=10
	GPIO15=10
	GPIO17=11
	GPIO18=12
	GPIO21=13
	GPIO22=15
	GPIO23=16
	GPIO24=18
	MOSI=19
	SPI_MOSI=19
	GPIO10=19
	MISO=21
	SPI_MISO=21
	GPIO9=21
	GPIO25=22
	SCLK=23
	SPI_SCLK=23
	GPIO11=23
	GPIO8=24
	GPIO7=26

	# You can't access to GPIO constants if you are not root (currently).
	# So we redefine them here, and you can use them as mnemonic.XXX
	IN=1
	OUT=0
	PUD_UP=2
	PUD_DOWN=1
	RISING=1
	FALLING=2
	BOTH=3

	def __init__(self):
		if os.getuid() == 0:
		        import RPi.GPIO as GPIO
			GPIO.setmode(GPIO.BOARD)
			GPIO.setwarnings(False)
		#else act as constants repository only
