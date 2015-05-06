PiLink - OSC to midi for the Raspberry Pi
=========================================

PiLink is a simple python script that enable to route OSC messages to midi. It has been designed to be run headless on a Raspberry Pi to avoid to setup a computer between a device that send OSC messages (like a iPad running TouchOSC) and a midi instrument.

PiLink tries to mimick some of the functionalities of the "defunc" Missing Link device.

Upon startup, the script will wait until /dev/midi1 is available. To stop the script simply send CTRL-C. If it is running at startup, simply kill it via SSH.

Installation
------------

* Copy the script to /home/pi
* Set the script to executable: ```$ chmod +a+x /home/pi/pilink.py```
* In /etc/rc.local, add this line ```/home/pi/pilink.py```

Configuration
-------------
Most of the configuration is done directly in the script :

* MIDI_DEV : change this to the configured midi device (usally /dev/midi1)
* UDP_PORT : the port that pilink listen for OSC messages

	
	
