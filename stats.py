sysex = 0
midiin = 0
oscin = 0
lasterror = ""
log = ""

def addsysex() :
	global sysex
	sysex += 1

def addmidiin() :
	global midiin 
	midiin += 1

def addoscin() :
	global oscin
	oscin += 1

def log(msg) :
	global log
	log = msg

def error(msg) :
	global lasterror
	lasterror = msg
	
def getStats() :
	return "midi %d osc %d sysex %d error %s" % (midiin, oscin, sysex, lasterror)