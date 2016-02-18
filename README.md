PiLink - OSC to midi for the Raspberry Pi
=========================================

PiLink is a simple python script that enable to route OSC messages to midi. It has been designed to be run headless on a Raspberry Pi to avoid to setup a computer between a device that sends OSC messages (like a iPad running TouchOSC) and a midi instrument.

PiLink tries to mimick some of the functionalities of the "defunc" Missing Link device.

You can configure the device by using : http://`pi_ip_address`:8080

Prerequisites
-------------
* Linux/UNIX experience for installing
* Raspberry Pi with WIFI connection (note the WIFI IP of your Pi)
* Compatible midi devices that works with Linux (the vast majority of midi interface; eg. the Roland GR-55 is plug and play)
* Source applications from [TouchOSC](http://hexler.net/software/touchosc) or [Lemur](https://liine.net/en/products/lemur)

Installation
------------
* see [INSTALL.md](docs/INSTALL.md) for installation procedure.

TODO
----
* More stats and logging
* Make a WIFI access point configuration out of the box for PiLink

