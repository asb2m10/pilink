from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import urlparse

import config
import stats
import pilink

class ConfigHTTPHandler(BaseHTTPRequestHandler):
    def writeContent(self, content) :
        self.send_response(200)         
        self.send_header('Content-type','text-html')
        self.end_headers()
        self.wfile.write(content)

    def do_GET(self) :
        if self.path == '/' :
            self.writeContent(indexHtml % (stats.getStats(), config.sendhost, config.sendport, config.receiveport, config.mididev))
            return;

        if self.path.startswith("/shutdown") :
            self.writeContent("bye")
            pilink.deamonize(pilink.shutdown)
            return

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

        self.send_error(404, 'file not found')

def start() :
    httpd = HTTPServer(('0.0.0.0', 8080), ConfigHTTPHandler)
    httpd.serve_forever()

indexHtml = """<html>
<title>PiLink</title>
<body>
<h1>PiLink</h1><p>%s</p>
<form action="config">
OSC Send IP : <input type="text" name="sendhost" value="%s"><br>
OSC Send Port : <input type="text" name="sendport" value="%s"><br>
OSC Receive Port : <input type="text" name="receiveport" value="%s"><br>
Midi Device : <input type="text" name="mididev" value="%s">
<br><br>
<input type="submit" value="configure"></form><form action="shutdown"><input type="submit" value="shutdown"></form>
</body>

</html>"""

configDoneHtml = """<html>
<title>PiLink</title>
<script>var minutes, seconds, count, counter, timer;
count = 10; //seconds
counter = setInterval(timer, 500);

function timer() {
    'use strict';
    count = count - 1;
    //seconds = checklength(count);
    if (count < 0) {
        clearInterval(counter);
        return;
    }
    document.getElementById("timer").innerHTML = 'Auto refresh in ' + count + ' ';
    if (count === 0) {
        location.assign("/")
    }
}
</script>
<body><h3>Configuration done... rebooting.</h3>
<p><i><span id="timer">Auto refresh</span></i><br><br>
<a href="/">Refresh</a></body></html>
"""

if __name__ == "__main__" :
    start()