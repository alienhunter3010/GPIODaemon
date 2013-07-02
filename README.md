GPIO Daemon for Raspberry Pi
============================
Written in python

Intro
-----
To work with GPIO (General Purpose Input Output) of Raspberry Pi you need to be root.
This is good for resource and security management but may be an issue depending on WHAT
you are developing and HOW MUCH your Raspberry Pi is vulnerable (for example on Internet with a public IP)

So I wrote a Daemon that keep the access to GPIO protected, but make you able to control it from a process without full privileges.

This code is provided with example client code written in python too. By the way the Daemon use a TCP/IP socket,
so you are free to write your client using different languages.

Actually the software is released on version 0.1. Wiki docs is on the way.

Requirement
-----------
The system works using RPi.GPIO module. If you haven't installed yet you can launch (on Raspbian):

      sudo apt-get install python-rpi.gpio

There are a lot of python modules used, but they are pretty standard and probably you have them all ready to use, yet.

Installing
----------
Just fork the code on your home or in a better path (your choice).

If you download the .tgz file just unpack it on your home or in a better path.

Any path or command on this doc assume that the current directory is the base path of the project.

WARNING
-------
GPIODaemon does not protect your Hardware. If you are using GPIO interface probably you have build your own custom electronic digital circuit, following a tutorial or from scratch.
GPIODaemon do not preserve in any way your components or your Raspberry Pi from design errors (as short circuit). USE IT AT YOUR OWN RISK.

Remember that Python and Linux kernel does not grant real time applications and so GPIODaemon.

Quick Start
-----------
Out-of-the-box setup files are written to be ready-to-go.

You can just launch GPIODaemon as root:

      sudo python GPIO/GPIODaemon.py start

And submit a simple raw command using GPIOClient (according to the structure of your project):

      python GPIO/GPIOClient.py "GPIO.output(18,1)"

Previous command setup as output the 18th pin of the GPIO (formelly known as GPIO24) and put it UP.

Recommended
-----------
Please refear to the project Wiki, on GitHub, to learn how to setup and use GPIODaemon.

https://github.com/alienhunter3010/GPIODaemon/wiki

You also need to know how to use RPi.GPIO.

https://code.google.com/p/raspberry-gpio-python/

The Author
----------
I'm an hard core coder. But I have not so much experience using python (this is my first published python project).
So, at this time, my code may be rude. If you have suggestion to make a better code you are welcome!
