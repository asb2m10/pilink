PiLink Installation
===================
PiLink is design to be run on a RasberryPi running on Linux. UN*X skills are necessary to be
able to complete the installation.

On the hardware side, you will need:

* RaspberryPi board (with casing & power supply)
* MicroSD card for OS installation
* USB WIFI interface
* USB Midi interface

Install the latest version of [Raspbian](https://www.raspberrypi.org/downloads/) on the MicroSD card. And
confirm you can logon the device using [SSH](https://www.raspberrypi.org/documentation/remote-access/ssh/).

Once this is done, plug your midi device into the Raspberry Pi. This is to confirm that Linux is correctly 
reconized your usb midi interface. You can do a 'ls -l /dev/midi*' to see if a midi interface is available.

Also, note the RasberryPi IP/hostname so you will be able to configure it using the web interface.

PiLink software install
-----------------------
To simplify the installation, PiLink will be installed in the home directory of the 'pi' user. Simply download
the latest version of PiLink to the home directory and unzip-it. This will create the pilink directory
automatically.

```
/home/pi $ unzip pilink-master.zip 
```

Then add the 'execute' right to the main startup script :

```
/home/pi $ chown +x pilink/pilink.sh
```

Before adding this script to the "rc.local" of the Rasberry Pi, it is suggested to run it locally to 
test if everything is working. Used CTRL-C to stop the process once you are done testing.

```
/home/ip $ pilink/pilink.sh
```

You can test the web interface if you point your browser directly to your Pi device 

	http://raspberry pi hostname:8080

Once it is working, you can added it to the OS startup script. Use your favorite editor to modify
/etc/rc.local and add this line at the end :

```
/home/pi/pilink/pilink.sh &
```

And reboot the device to confirm that the startup process worked.

WIFI Access Point
-----------------
To greatly simplify the configuration of PiLink, you can configure you Rasberry Pi to act as
a WIFI access point. This way, you can simply connect your tablet to 'pi' access point and
point to the router IP (should be static) to be able to configure it.

[Follow this for now](http://www.pi-point.co.uk/documentation/)