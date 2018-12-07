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

from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import mimetypes
import urlparse
import os
import json
import inspect

import config
import stats
import pilink

import glob

class Service :
    def config(self, data, handler) :
        ret = {}
        if handler.command == "GET" :
            for i in dir(config) :
                if not i.startswith("__") :
                    ret[i] = eval("config.%s" % i)
            ret['mididev_lst'] = glob.glob("/dev/midi*")
            ret['mididev_lst'].extend(glob.glob("/dev/sound/midi*"))
            ret['mididev_lst'].extend(glob.glob("/dev/snd/midi*"))
            ret['clientip'] = handler.client_address[0]
        else :
            config.sendhost = data['sendhost']
            config.sendport = data['sendport']
            config.receiveport = data['receiveport']
            config.mididev = data['mididev']
            pilink.saveConfig()
            ret['return'] = "OKOK"
        return ret;


    def shutdown(self, data, handler) :
        pilink.deamonize(pilink.shutdown)
        return { "good" : "bye sir" }

    def reboot(self, data, handler) :
        pilink.deamonize(pilink.reboot)
        return { "be right" : "back" }

    def logs(self, data, handler) :
        return stats.getStats();

    ### =====================================================================
    def call(self, name, data, handler) :
        calle = getattr(self, name)
        return calle(data, handler);

    def isService(self, uri) :
        return hasattr(self.__class__, uri) and callable(getattr(self.__class__, uri))


class ConfigHTTPHandler(BaseHTTPRequestHandler):
    def writeContent(self, content) :
        self.send_response(200)         
        self.send_header('Content-type','text-html')
        self.end_headers()
        self.wfile.write(content)

    def do_GET(self) :
        if self.path == '/' :
            target = "index.html"
        else :
            target = self.path

        baseuri = target[1:].split("?")
        if service.isService(baseuri[0]) :
            if len(baseuri) > 1 :
                cfg = urlparse.parse_qs(baseuri[1])
            else :
                cfg = {}
            out = service.call(baseuri[0], cfg, self)
            self.writeContent(json.dumps(out));
            return;

        mime = mimetypes.guess_type(target)[0]

        fullpath = "web/%s" % target

        if not os.path.isfile(fullpath) :
            self.send_error(404, 'file not found %s' % fullpath)
            return

        f = open(fullpath, "r")
        content = f.read()
        f.close()

        self.send_response(200)         
        self.send_header('Content-type',mime)
        self.end_headers()
        self.wfile.write(content)

    def do_POST(self) :
        content_len = int(self.headers.getheader('content-length', 0))
        post_body = self.rfile.read(content_len)
        ret = service.call(self.path[1:], json.loads(post_body), self)
        
        self.send_response(200);
        self.send_header('Content-type', 'application/javascript')
        self.end_headers()
        self.wfile.write(json.dumps(ret))

def start() :
    httpd = HTTPServer(('0.0.0.0', 8080), ConfigHTTPHandler)
    httpd.serve_forever()

service = Service()
mimetypes.init()

if __name__ == "__main__" :
    start()

    """
        if self.path.startswith("/config?") :
            cfg = urlparse.parse_qs(self.path[8:])
            config.sendhost = cfg['sendhost'][0]
            config.sendport = int(cfg['sendport'][0])
            config.receiveport = int(cfg['receiveport'][0])
            config.mididev = cfg['mididev'][0]
            pilink.saveConfig()
            self.writeContent(configDoneHtml);
            pilink.deamonize(pilink.reboot)
            return;
    """
