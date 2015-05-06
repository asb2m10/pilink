#!/usr/bin/python
"""
	PiLink - OSC to midi for the Raspberry Pi
	
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

import os
import sys
import time
import socket
import struct
import threading
import unittest

# change this to use a different midi output device
MIDI_DEV = "/dev/midi1"
# change this to listen to another UPD port
UDP_PORT = 8000

class MidiInSink(threading.Thread) :
	def run(self) :
		while 1 :
			try :
				midiIn = os.open(MIDI_DEV, os.O_RDONLY)
				while 1 :
					os.read(midiIn, 1024);
			except Exception as e :
				print("**> MidiInSink Exception cought: %s" % e)
				if lastError + 5 > time.time() :
					print("Waiting before trying again....")
					time.sleep(5)
				lastError = time.time()
			except BaseException  :
				return 1				
			finally :
				try :
					os.close(midiIn)
				except :
					pass

def oscParser(msg):
	""" parse the osc buffer; from http://www.cs.cmu.edu/~15104/week11/server.py
	"""
	end_of_addr = msg.find('\000')
	if end_of_addr == -1:
		raise EOFError("Unable to find end of message")
	address = msg[ : end_of_addr]
	ret = [address]
	
	# skip past the address
	tsx = end_of_addr # find type string index tsx
	while tsx < len(msg) and msg[tsx] == '\000':
		tsx += 1
		
	if tsx >= len(msg):
		actual_types = ""
	else: # i will be index into msg for parameters
		i = msg.find('\000', tsx)
		if i > tsx:
			# skip the comma
			actual_types = msg[tsx + 1 : i]
		else:
			i = len(msg)
		
	# skip past the type string to the next multiple of 4 bytes:
	while i < len(msg) and i % 4 > 0:
		i += 1
	
	for typechar in actual_types:
		if typechar == 'i':
			if i + 4 <= len(msg):
				intval = struct.unpack('!i', msg[i : i + 4])
				i += 4
				ret.append(intval[0])
		elif typechar == 'f':
			if i + 4 <= len(msg):
				floval = struct.unpack('!f', msg[i : i + 4])
				i += 4
				ret.append(floval[0])
		elif typechar in "sSc":
			i2 = msg.find('\000', i)
			if i2 != -1:
				strval = msg[i : i2]
				i = i2 + 1
				ret.append(strval[0])
		elif typechar == 'd':
			if i + 4 <= len(msg):
				floval = struct.unpack('!d', msg[i : i + 8])
				i += 8
				ret.append(floval[0])

	return ret

def parseHexValue(v) :
	if  v.startswith("0x") or v.startswith("0X") :
		return int(v,16)
	else :
		return int(v,10)

def parseMidiMsg(msg, replaceValue) :
	midiMsg = []
	for i in msg.split() :
		if i.startswith("x(") :
			rng = map(parseHexValue, i[2:-1].split(".."))
			ratio = rng[1] - rng[0]
			midiMsg.append(int(replaceValue * ratio) + rng[0])
		else :
			midiMsg.append(parseHexValue(i))
	return midiMsg

def osc2Midi(msg) :
	oscToken = msg[0].split("/")[1:]
	token = oscToken.pop(0)
	midiMsg = []
	
	# missing link protocol
	if token == 'midi' :
		token = oscToken.pop(0)
		if token == 'z' :
			while len(oscToken) != 0 :
				token = oscToken.pop(0)
				midiMsg.extend(parseMidiMsg(token, msg[1]))
		else :
			midiMsg = parseMidiMsg(token, msg[1])

	# TouchOSC and Reaktor protocol
	elif token.isdigit() :
		chl = int(token)

		if chl >= 0 and chl < 16 :
			token = oscToken.pop()

			# Reaktor vs TouchOSC protocol
			if token.index('_') > 0 :
				token.replace('_', ' ')

			msgToken = token.split()
			action = msgToken.pop()

			### TODO add more OSC actions here
			if action == 'note' :
				midiMsg = [ ( '0x90' + chl ), int(msgToken[0]), int(msgToken[1]) ]
			else :
				print("Unknown OSC action %s" % action)

	return midiMsg

def main() :
	#unittest.main()
	#return;

	midiConn = -1
	networkConn = -1
	lastError = 0
	
	midiInSink = MidiInSink()
	midiInSink.daemon = True
	midiInSink.start()
	
	while 1 :
		try :
			networkConn = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) 
			networkConn.bind(("0.0.0.0", UDP_PORT))
			midiConn = os.open(MIDI_DEV, os.O_WRONLY)
			print "LISTENING UDP PORT %d" % UDP_PORT
			while 1 :
				midiMsg = [] # send empty midi message
				msg = networkConn.recvfrom(4096)[0]
				try :
					oscMsg = oscParser(msg)
					print "==> received %s" % repr(oscMsg)
					midiMsg = osc2Midi(oscMsg)
				except StandardError as e : 
					print("??? Unable to parse message : %s" % e)
				if len(midiMsg) != 0 :
					print "<== sending %s\n" % repr(midiMsg)
					os.write(midiConn, bytearray(midiMsg))
				else :
					print
		except Exception as e :
			print("**> Exception cought: %s" % e)
			if lastError + 5 > time.time() :
				print("Waiting before trying again....")
				time.sleep(5)
			lastError = time.time()
		except BaseException  :
			print("Keyboard / base interrupt received, stopping deamon...")
			return 1
		finally :
			# close stuff we need to 
			try :
				if midiConn != -1 :
					os.close(midiConn)
			except :
				pass
			try :					
				if networkConn != - 1 :
					networkConn.close()
			except :
				pass


# #########################################################################
# ## UNIT TESTS
# #########################################################################

class PiLink(unittest.TestCase) :
	def testOne(self) :
		self.assertEquals(osc2Midi(["/midi/0x90 60 127", 0]), [0x90, 60, 127])
		self.assertEquals(osc2Midi(["/midi/z/0x90 60 127/0x91 0x21 00", 0]), [0x90, 60, 127, 0x91, 0x21, 0])
		self.assertEquals(osc2Midi(["/midi/0xf0 0xb0 0 0 0xb0 0x20 0x00 0xc0 52 0xf7", 0]), [0xf0, 0xb0, 0, 0, 0xb0, 0x20, 0x00, 0xc0, 52, 0xF7])

if __name__ == '__main__' :
	main()

