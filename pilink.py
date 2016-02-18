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
import threading
import time

import router
import web
import config

def startup() :
    #deamonize(router.midiOutput)
    #deamonize(router.midiInput)
    deamonize(router.oscInput)
    web.start()

def saveConfig() :
    config_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.py")

    with open(config_file, "w") as f :
        f.write("# this file was automatically generated\n\n")
        f.write("sendhost = '%s'\n" % config.sendhost)
        f.write("sendport = %d\n" % config.sendport)
        f.write("receiveport = %d\n" % config.receiveport)
        f.write("mididev = '%s'\n" % config.mididev)
        f.write("\n")

def shutdown() :
    time.sleep(1)
    os._exit(0)

def reboot() :
    time.sleep(1)    
    os._exit(100)

def deamonize(callable) :
    t = threading.Thread(target=callable)
    t.daemon = True
    t.start()

if __name__ == "__main__" :
    startup()
