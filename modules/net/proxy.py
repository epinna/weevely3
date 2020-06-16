from core.loggers import log, dlog
from core import messages
from core.vectors import ModuleExec
from core.module import Module
from core.config import base_path
from http.server import HTTPServer, BaseHTTPRequestHandler
from tempfile import gettempdir
from socketserver import ThreadingMixIn
from urllib.parse import urlparse, urlunparse, ParseResult
from io import StringIO
from http.client import HTTPResponse
import threading
import re
import os
import sys
import socket
import ssl
import select
import http.client
import urllib.parse
import threading
import time
import json
import re
from http.server import HTTPServer, BaseHTTPRequestHandler
from socketserver import ThreadingMixIn
from io import BytesIO
from subprocess import Popen, PIPE
from html.parser import HTMLParser
from tempfile import mkdtemp

re_valid_ip = re.compile("^(([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.){3}([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])$")
re_valid_hostname  = re.compile("^(([a-zA-Z0-9\-]+)\.)*([A-Za-z]|[A-Za-z][A-Za-z0-9\-]*[A-Za-z0-9])$")

temp_certdir = mkdtemp()

lock = threading.Lock()

class FakeSocket():
    def __init__(self, response_str):
        self._file = BytesIO(response_str)
    def makefile(self, *args, **kwargs):
        return self._file

# Create path for the CA certificates and keys
cert_folder = os.path.join(base_path, 'certs')
try:
    os.makedirs(cert_folder)
except:
    pass

def get_cert_path(path):
    return os.path.join(cert_folder, path)

def initialize_certificates():

    cakey_path = get_cert_path("ca.key")
    cacrt_path = get_cert_path("ca.crt")
    certkey_path = get_cert_path("cert.key")
    
    if not os.path.isfile(cakey_path) or not os.path.isfile(cacrt_path) or not os.path.isfile(certkey_path):
        # openssl genrsa -out ca.key 2048
        p1 = Popen(["openssl", "genrsa", "-out", cakey_path, "2048" ])
        p1.communicate()
        p1.wait()
    
        # openssl req -new -x509 -days 3650 -key ca.key -out ca.crt -subj "/CN=proxy2 CA"
        p2 = Popen(["openssl", "req", "-new", "-x509", "-days", "3650", "-key",
        cakey_path, "-out", cacrt_path, "-subj", "/CN=proxy2 CA" ])
        p2.communicate()
        p2.wait()
        
        # openssl genrsa -out cert.key 2048
        p3 = Popen(["openssl", "genrsa", "-out", certkey_path, "2048" ])
        p3.communicate()
        p3.wait()
        
#
# Most of the Proxy part has been taken from https://github.com/inaz2/proxy2
#

class ThreadingHTTPServer(ThreadingMixIn, HTTPServer):
    address_family = socket.AF_INET
    daemon_threads = True

    def handle_error(self, request, client_address):
        # surpress socket/ssl related errors
        cls, e = sys.exc_info()[:2]
        if cls is socket.error or cls is ssl.SSLError:
            pass
        else:
            return HTTPServer.handle_error(self, request, client_address)


class ProxyRequestHandler(BaseHTTPRequestHandler):
    cakey = get_cert_path('ca.key')
    cacert = get_cert_path('ca.crt')
    certkey = get_cert_path('cert.key')
    certdir = temp_certdir
    timeout = 5
    lock = threading.Lock()

    def __init__(self, *args, **kwargs):
        self.tls = threading.local()
        self.tls.conns = {}

        BaseHTTPRequestHandler.__init__(self, *args, **kwargs)

    def log_error(self, format, *args):
        # surpress "Request timed out: timeout('timed out',)"
        if isinstance(args[0], socket.timeout):
            return

    def do_CONNECT(self):
        self.connect_intercept()

    def connect_intercept(self):
        hostname = self.path.split(':')[0]
        certname = "%s.crt" % (hostname)
        certpath = os.path.join(self.certdir, certname)

        if not (re_valid_ip.match(hostname) or re_valid_hostname.match(hostname)):
            log.warning("CN name '%s' is not valid, using 'www.weevely.com'" % (hostname))
            hostname = 'www.weevely.com'

        with self.lock:
            if not os.path.isfile(certpath):
                epoch = "%d" % (time.time() * 1000)
                p1 = Popen(["openssl", "req", "-new", "-key", self.certkey, "-subj", "/CN=%s" % hostname], stdout=PIPE)
                p2 = Popen(["openssl", "x509", "-req", "-days", "3650", "-CA", self.cacert, "-CAkey", self.cakey, "-set_serial", epoch, "-out", certpath], stdin=p1.stdout, stderr=PIPE)
                p2.communicate()

        self.send_response_only(200, 'Connection Established')
        self.end_headers()

        try:
            self.connection = ssl.wrap_socket(self.connection, keyfile=self.certkey, certfile=certpath, server_side=True)
            self.rfile = self.connection.makefile("rb", self.rbufsize)
            self.wfile = self.connection.makefile("wb", self.wbufsize)
        except Exception as e:
            log.debug(e)
            raise

        conntype = self.headers.get('Proxy-Connection', '')
        if self.protocol_version == "HTTP/1.1" and conntype.lower() != 'close':
            self.close_connection = 0
        else:
            self.close_connection = 1

    def connect_relay(self):
        address = self.path.split(':', 1)
        address[1] = int(address[1]) or 443
        try:
            s = socket.create_connection(address, timeout=self.timeout)
        except Exception as e:
            self.send_error(502)
            return
        self.send_response(200, 'Connection Established')
        self.end_headers()

        conns = [self.connection, s]
        self.close_connection = 0
        while not self.close_connection:
            rlist, wlist, xlist = select.select(conns, [], conns, self.timeout)
            if xlist or not rlist:
                break
            for r in rlist:
                other = conns[1] if r is conns[0] else conns[0]
                data = r.recv(8192)
                if not data:
                    self.close_connection = 1
                    break
                other.sendall(data)

    def do_GET(self):
        
        if self.path == 'http://weevely/':
            self.send_cacert()
            return

        req = self
        content_length = int(req.headers.get('Content-Length', 0))
        req_body = self.rfile.read(content_length) if content_length else ''

        if req.path[0] == '/':
            if isinstance(self.connection, ssl.SSLSocket):
                req.path = "https://%s%s" % (req.headers['Host'], req.path)
            else:
                req.path = "http://%s%s" % (req.headers['Host'], req.path)

        req.headers['Content-length'] = str(len(req_body))

        u = urllib.parse.urlsplit(req.path)
        scheme, netloc, path = u.scheme, u.netloc, (u.path + '?' + u.query if u.query else u.path)
        assert scheme in ('http', 'https')
        if netloc:
            req.headers['Host'] = netloc
        setattr(req, 'headers', self.filter_headers(req.headers))
        
        net_curl_args = [
            '-X',
            self.command,
            '-i'
        ]

        net_curl_args.append(self.path)
        
        for h in req.headers:
                
            if h.title().lower() == 'host':
                host = self.headers[h]
            else:
                net_curl_args += [ '-H', '%s: %s' % ( h.title(), self.headers[h] ) ]

        if self.command == 'POST':
            content_len = int(self.headers.get('content-length', 0))
            net_curl_args += [ '-d', req_body ]

        lock.acquire()
        try:
            result, headers, saved = ModuleExec(
                'net_curl',
                net_curl_args
            ).run()
        finally:
            lock.release()
            
        if not headers:
            log.debug('Error no headers')
            self.send_error(502)
            return

        log.debug(
                '> ' + '\r\n> '.join(
                    [ '%s: %s' % (
                        h.title(), 
                        self.headers[h]
                        ) for h in self.headers 
                        ]
                    )
                )
        log.debug('< ' + '\r\n< '.join([ h.decode('utf-8', 'replace') for h in headers ]))

        http_response_str = b'\r\n'.join(headers) + b'\r\n\r\n' + result
        source = FakeSocket(http_response_str)
        res = HTTPResponse(source)
        res.begin()

        version_table = {10: 'HTTP/1.0', 11: 'HTTP/1.1'}
        setattr(res, 'headers', res.msg)
        setattr(res, 'response_version', version_table[res.version])
                
        # support streaming
        if not 'Content-Length' in res.headers and 'no-store' in res.headers.get('Cache-Control', ''):
            setattr(res, 'headers', self.filter_headers(res.headers))
            self.relay_streaming(res)
            return

        try:
            res_body = res.read()
        except Exception as e:
            log.debug(e)
            self.send_error(500)
            return

        setattr(res, 'headers', self.filter_headers(res.headers))

        respstring = "%s %d %s\r\n" % (self.protocol_version, res.status, res.reason)
        self.wfile.write(respstring.encode('utf-8'))
        self.wfile.write(res.headers.as_bytes())
        self.wfile.write(res_body)
        self.wfile.flush()
        
    def relay_streaming(self, res):

        respstring = "%s %d %s\r\n" % (self.protocol_version, res.status, res.reason)
        self.wfile.write(respstring.encode('utf-8'))
        self.wfile.write(res.headers.as_bytes() + b"\r\n")

        try:
            while True:
                chunk = res.read(8192)
                if not chunk:
                    break
                self.wfile.write(chunk)
            self.wfile.flush()
        except socket.error:
            # connection closed by client
            pass

    do_HEAD = do_GET
    do_POST = do_GET
    do_PUT = do_GET
    do_DELETE = do_GET
    do_OPTIONS = do_GET

    def filter_headers(self, headers):
        # http://tools.ietf.org/html/rfc2616#section-13.5.1
        hop_by_hop = ('connection', 'keep-alive', 'proxy-authenticate', 'proxy-authorization', 'te', 'trailers', 'transfer-encoding', 'upgrade')
        for k in hop_by_hop:
            del headers[k]

        return headers

    def send_cacert(self):
        with open(self.cacert, 'rb') as f:
            data = f.read()

        respstring = "%s %d %s\r\n" % (self.protocol_version, 200, 'OK')
        self.wfile.write(respstring.encode('utf-8'))
        self.send_header('Content-Type', 'application/x-x509-ca-cert')
        self.send_header('Content-Length', len(data))
        self.send_header('Connection', 'close')
        self.end_headers()
        self.wfile.write(data)


def run_proxy2(HandlerClass=ProxyRequestHandler, ServerClass=ThreadingHTTPServer, protocol="HTTP/1.1", hostname='127.0.0.1', port = '8080'):
    server_address = (hostname, port)

    HandlerClass.protocol_version = protocol
    httpd = ServerClass(server_address, HandlerClass)

    sa = httpd.socket.getsockname()
    httpd.serve_forever()


class Proxy(Module):

    """Run local proxy to pivot HTTP/HTTPS browsing through the target."""

    def init(self):

        self.register_info(
            {
                'author': [
                    'Emilio Pinna'
                ],
                'license': 'GPLv3'
            }
        )

        self.register_arguments([
            { 'name' : '-lhost', 'default' : '127.0.0.1' },
            { 'name' : '-lport', 'default' : 8080, 'type' : int },
            { 'name' : '-no-background', 'action' : 'store_true', 'default' : False, 'help' : 'Run foreground' }
        ])

    def run(self):

        log.warning(messages.module_net_proxy.proxy_starting_s_i % ( self.args['lhost'], self.args['lport'] ))
        log.warning(messages.module_net_proxy.proxy_set_proxy)

        initialize_certificates()

        if self.args['no_background']:
            log.warning(messages.module_net_proxy.proxy_started_foreground)
            run_proxy2(
                hostname = self.args['lhost'],
                port = self.args['lport']
            )
        else:
            log.warning(messages.module_net_proxy.proxy_started_background)
            server_thread = threading.Thread(target=run_proxy2, kwargs = {
                'hostname': self.args['lhost'],
                'port': self.args['lport']
            })
            server_thread.daemon = True
            server_thread.start()
