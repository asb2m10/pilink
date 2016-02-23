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

activity = { 'midiin': 0, 'oscin' : 0, 'midiout' : 0 }
messages = [ "pilink started." ]

def midiin(msg) :
	activity['midiin'] = activity['midiin'] + 1
	log("==> midiin: " + msg)

def midiout(msg) :
	activity['midiout'] = activity['midiout'] + 1
	log("<== midiout " + msg)

def oscin(msg) :
	activity['oscin'] = activity['oscin'] + 1
	log("==> osc " + msg)

def error(msg) :
	if len(messages) > 1024 :
		messages.pop(0)
	messages.append("ERROR: " + str(msg))

def log(msg) :
	print msg
	if len(messages) > 1024 :
		messages.pop(0)
	messages.append(msg)

def getStats() :
	ret = {}
	ret['messages'] = messages[::-1]
	ret['activity'] = activity
	return ret
