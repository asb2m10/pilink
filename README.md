PiLink - OSC to midi for the Raspberry Pi
=========================================

PiLink is a simple python script that enable to route OSC messages to midi. It has been designed to be run headless on a Raspberry Pi to avoid to setup a computer between a device that sends OSC messages (like a iPad running TouchOSC) and a midi instrument.

PiLink tries to mimick some of the functionalities of the "defunc" Missing Link device.

You can configure the device by using : http:pi_ip_address:8080

Prerequisites
-------------
* Raspberry Pi with WIFI connection (note the WIFI IP of your Pi)
* Compatible midi devices that works with Linux (the vast majority of midi interface; eg. the Roland GR-55 is plug and play)
* Source applications from [TouchOSC](http://hexler.net/software/touchosc) or [Lemur](https://liine.net/en/products/lemur)

Installation
------------
* Download source from github (see [Download ZIP] button on the right)
* Copy the zip (PiLink-master.zip) to /home/pi on the Pi
* Unzip the content ```~ $ unzip PiLink-master.zip```
* Set the script to executable: ```~ $ chmod +a+x /home/pi/PiLink-master/pilink.sh```
* Run the script in console to test if it works : ```~ $ /home/pi/PiLink-master/pilink.sh``` before putting it in the startup scripts
* In /etc/rc.local, add this line ```/home/pi/PiLink-master/pilink.sh &``` to start PiLink at startup

TODO
----
* More stats and logging
* Make a WIFI access point configuration out of the box for PiLink

