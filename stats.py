"""
    pilink - OSC to midi for the Raspberry Pi
    
    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at
    
         http://www.apache.org/licenses/LICENSE-2.0
    
    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.

"""

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