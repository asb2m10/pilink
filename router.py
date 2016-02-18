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

import os
import sys
import time
import socket
import struct
import traceback
import unittest
import Queue

import config
import stats

outq = Queue.Queue()

def parseHexValue(v) :
    if  v.startswith("0x") or v.startswith("0X") :
        return int(v,16)
    else :
        return int(v,10)

def oscParser(msg, parsedMsg):
    """ parse the osc buffer; from http://www.cs.cmu.edu/~15104/week11/server.py

    """

    end_of_addr = msg.find('\000')
    if end_of_addr == -1:
        raise EOFError("Unable to find end of message")
    address = msg[ : end_of_addr]

    # Since the RaspberryPi doesn't have any time synchro, bundle 
    # time frames are not yet processed.    
    if address == "#bundle" :
        msgSize = struct.unpack('!i', msg[16 : 20])[0]
        oscParser(msg[20:20+msgSize], parsedMsg)
        return

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

    parsedMsg.append(ret)

def parseMidiMsg(msg, replaceValues) :
    midiMsg = []
    msg = msg.replace(',', ' ')     # touchosc sends ' ' ; lemur sends ','
    for i in msg.split() :
        first = i[0].lower()
        if first in "xyz" :
            replacePos = ord(first) - ord('x')
            if len(i) > 1 and i[1] == "(" :
                rng = map(parseHexValue, i[2:-1].split(".."))
                ratio = rng[1] - rng[0]
                midiMsg.append(int(replaceValues[replacePos] * ratio) + rng[0])
            else :
                midiMsg.append(int(replaceValues[replacePos] * 127))
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
                midiMsg.extend(parseMidiMsg(token, msg[1:]))
        else :
            midiMsg = parseMidiMsg(token, msg[1:])

    # TouchOSC and Reaktor protocol
    elif token.isdigit() :
        chl = int(token)

        if chl >= 0 and chl < 16 :
            if len(oscToken) == 0 :
                return midiMsg
            else :
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

# #########################################################################

def oscInput() :
    networkConn = -1
    lastError = 0

    while 1 :
        try :
            networkConn = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) 
            networkConn.bind(("0.0.0.0", config.receiveport))
            print("LISTENING UDP PORT %d" % config.receiveport)
            while 1 :
                midiMsg = [] # send empty midi message
                msg = networkConn.recvfrom(4096)[0]
                try :
                    parsedMsg = []
                    oscParser(msg, parsedMsg)

                    print("==> received %s" % repr(parsedMsg))

                    for i in parsedMsg :
                        midiMsg.extend(osc2Midi(i))
                    stats.addoscin()
                except Exception as e :
                    stats.error(e)
                    exc_type, exc_value, exc_traceback = sys.exc_info()
                    print(repr(traceback.format_exception(exc_type, exc_value, exc_traceback)))
                if len(midiMsg) != 0 :
                    outq.put_nowait(midiMsg)
        except Exception as e :
            stats.error(e)
            print("**> Exception cought: %s" % e)
            if lastError + 5 > time.time() :
                print("Waiting before trying again....")
                time.sleep(5)
            lastError = time.time()
        except BaseException  :
            print("Keyboard / base interrupt received, stopping deamon...")
            return 1
        finally :
            try :                   
                if networkConn != - 1 :
                    networkConn.close()
            except :
                pass

def midiInput() :
    lastError = 0

    while 1 :
        try :
            midiIn = os.open(config.mididev, os.O_RDONLY)
            sysexBuffer = []
            while 1 :
                midiMsg = os.read(midiIn, 1024);
                toSend = []
                for i in midiMsg :
                    i = ord(i)
                    if len(sysexBuffer) > 0 :
                        sysexBuffer.append(i)
                        if i == 0xF7 :
                            toSend.extend(sysexBuffer)
                            stats.addsysex()
                            sysexBuffer = []
                    elif i == 0xF0 :
                        sysexBuffer.append(i)
                    else :
                        toSend.append(i)

                if len(toSend) == 0 :
                    continue

                outq.put_nowait(toSend)

                if config.sendport != 0 :
                    oscMsg = "/midi/"
                    for i in toSend :
                        oscMsg = oscMsg + "%x " % i

                    # OSC string must be filled with nulls, multiples of 4
                    footer = len(oscMsg) % 4
                    if footer == 0 :
                        footer = 4

                    oscMsg = oscMsg + ("\0" * footer)

                    networkConn = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                    networkConn.sendto(oscMsg, (config.sendhost, config.sendport))

                stats.addmidiin()
        except Exception as e :
            stats.error(e)
            print("**> Midi Input Exception cought: %s" % e)
            if lastError + 4 > time.time() :
                print("Waiting before trying again....")
                time.sleep(4)
            lastError = time.time()
        except BaseException  :
            return 1                
        finally :
            try :
                os.close(midiIn)
            except :
                pass

def midiOutput() :
    mididev = config.mididev
    midiConn = -1
    lastError = 0

    while True :
        try :
            midiConn = os.open(config.mididev, os.O_WRONLY)
            while 1 :
                midiMsg = outq.get(True)
                display = ""
                for i in midiMsg :
                    display = display + "0x%x " % i
                print("<== sending midi %s" % display)
                os.write(midiConn, bytearray(midiMsg))                  
        except Exception as e :
            stats.error(e)
            print("**> Midi Output Exception cought: %s" % e)
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

# #########################################################################
# ## UNIT TESTS
# #########################################################################

class PiLink(unittest.TestCase) :
    def testOne(self) :
        self.assertEquals(osc2Midi(["/midi/0x90 60 127", 0]), [0x90, 60, 127])
        self.assertEquals(osc2Midi(["/midi/z/0x90 60 127/0x91 0x21 00", 0]), [0x90, 60, 127, 0x91, 0x21, 0])
        self.assertEquals(osc2Midi(["/midi/0xf0 0xb0 0 0 0xb0 0x20 0x00 0xc0 52 0xf7", 0]), [0xf0, 0xb0, 0, 0, 0xb0, 0x20, 0x00, 0xc0, 52, 0xF7])

if __name__ == "__main__" :
    unittest.main()

