#!/usr/bin/python2

import BaseHTTPServer
from BaseHTTPServer import BaseHTTPRequestHandler
from SimpleHTTPServer import SimpleHTTPRequestHandler
import sys
import base64
import json
import cgi
import valuercfg

key = ""

class ValuerCfgHandler(BaseHTTPRequestHandler):
    def _set_headers(self, content_type="text/html"):
        self.send_response(200)
        self.send_header('Content-type', content_type)
        self.end_headers()

    def do_GET(self):
        self._set_headers()
        with open("index.htm", "r") as f:
            self.wfile.write(f.read())

    def do_HEAD(self):
        self._set_headers()

    def do_POST(self):
        self._set_headers("application/json")

        ctype, pdict = cgi.parse_header(self.headers.getheader('content-type'))
        if ctype == 'multipart/form-data':
            postvars = cgi.parse_multipart(self.rfile, pdict)
        elif ctype == 'application/x-www-form-urlencoded':
            length = int(self.headers.getheader('content-length'))
            postvars = cgi.parse_qs(self.rfile.read(length), keep_blank_values=1)
        else:
            postvars = {}

        sample_tests = list(zip(postvars.get("sampleTests[]", []), postvars.get("samplePoints[]", []), postvars.get("sampleDependencies[]", [])))
        online_tests = list(zip(postvars.get("onlineTests[]", []), postvars.get("onlinePoints[]", []), postvars.get("onlineDependencies[]", [])))
        offline_tests = list(zip(postvars.get("offlineTests[]", []), postvars.get("offlinePoints[]", []), postvars.get("offlineDependencies[]", [])))

        valuercfg_content, servecfg_content, err = valuercfg.generate_tests(sample_tests, online_tests, offline_tests)

        self.wfile.write(json.JSONEncoder().encode({
            "valuercfg": valuercfg_content,
            "servecfg": servecfg_content,
            "err": err
        }))


class AuthHandler(ValuerCfgHandler):
    ''' Main class to present webpages and authentication. '''
    def do_HEAD(self):
        print "send header"
        self.send_response(200)
        self.send_header('Content-type', 'application/html')
        self.end_headers()

    def do_AUTHHEAD(self):
        print "send header"
        self.send_response(401)
        self.send_header('WWW-Authenticate', 'Basic realm=\"Test\"')
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def do_GET(self):
        global key
        ''' Present frontpage with user authentication. '''
        if self.headers.getheader('Authorization') == None:
            self.do_AUTHHEAD()
            self.wfile.write('no auth header received')
            pass
        elif self.headers.getheader('Authorization') == 'Basic '+key:
            ValuerCfgHandler.do_GET(self)
            pass
        else:
            self.do_AUTHHEAD()
            self.wfile.write(self.headers.getheader('Authorization'))
            self.wfile.write('not authenticated')

            pass


def test(HandlerClass = AuthHandler,
         ServerClass = BaseHTTPServer.HTTPServer): 
    BaseHTTPServer.test(HandlerClass, ServerClass)

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print "usage main.py [port] [username:password]"
        sys.exit()
    key = base64.b64encode(sys.argv[2])
    test()
