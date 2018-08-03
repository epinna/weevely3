from core.loggers import log, dlog
from core import messages
from core.vectors import ModuleExec
from core.module import Module
from core.config import base_path
from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler
from tempfile import gettempdir
from SocketServer import ThreadingMixIn
from urlparse import urlparse, urlunparse, ParseResult
from StringIO import StringIO
from httplib import HTTPResponse
import threading
import re
import os
import sys
import socket
import ssl
import select
import httplib
import urlparse
import threading
import gzip
import zlib
import time
import json
import re
from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler
from SocketServer import ThreadingMixIn
from cStringIO import StringIO
from subprocess import Popen, PIPE
from HTMLParser import HTMLParser
from tempfile import mkdtemp

temp_certdir = mkdtemp()

class FakeSocket():
    def __init__(self, response_str):
        self._file = StringIO(response_str)
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

        with self.lock:
            if not os.path.isfile(certpath):
                epoch = "%d" % (time.time() * 1000)
                p1 = Popen(["openssl", "req", "-new", "-key", self.certkey, "-subj", "/CN=%s" % hostname], stdout=PIPE)
                p2 = Popen(["openssl", "x509", "-req", "-days", "3650", "-CA", self.cacert, "-CAkey", self.cakey, "-set_serial", epoch, "-out", certpath], stdin=p1.stdout, stderr=PIPE)
                p2.communicate()

        self.wfile.write("%s %d %s\r\n" % (self.protocol_version, 200, 'Connection Established'))
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
        req_body = self.rfile.read(content_length) if content_length else None

        if req.path[0] == '/':
            if isinstance(self.connection, ssl.SSLSocket):
                req.path = "https://%s%s" % (req.headers['Host'], req.path)
            else:
                req.path = "http://%s%s" % (req.headers['Host'], req.path)

        req_body_modified = self.request_handler(req, req_body)
        if req_body_modified is False:
            self.send_error(403)
            return
        elif req_body_modified is not None:
            req_body = req_body_modified
            req.headers['Content-length'] = str(len(req_body))

        u = urlparse.urlsplit(req.path)
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
                
            net_curl_args += [ '-H', '%s: %s' % ( h.title(), self.headers[h] ) ]

        if self.command == 'POST':
            content_len = int(self.headers.getheader('content-length', 0))
            net_curl_args += [ '-d', req_body ]

        result, headers, saved = ModuleExec(
            'net_curl',
            net_curl_args
        ).run()
        
        if not headers:
            log.debug('Error no headers')
            self.send_error(502)
            return
            
        log.debug('> ' + '\r\n> '.join([ '%s: %s' % (h.title(), self.headers[h]) for h in self.headers ]))
        log.debug('< ' + '\r\n< '.join(headers))

        http_response_str = '\r\n'.join(headers) + '\r\n\r\n' + result
        source = FakeSocket(http_response_str)
        res = HTTPResponse(source)
        res.begin()

        version_table = {10: 'HTTP/1.0', 11: 'HTTP/1.1'}
        setattr(res, 'headers', res.msg)
        setattr(res, 'response_version', version_table[res.version])
                
        # support streaming
        if not 'Content-Length' in res.headers and 'no-store' in res.headers.get('Cache-Control', ''):
            self.response_handler(req, req_body, res, '')
            setattr(res, 'headers', self.filter_headers(res.headers))
            self.relay_streaming(res)
            return

        try:
            res_body = res.read()
        except Exception as e:
            log.debug(e)
            self.send_error(500)
            return

        content_encoding = res.headers.get('Content-Encoding', 'identity')
        res_body_plain = self.decode_content_body(res_body, content_encoding)

        res_body_modified = self.response_handler(req, req_body, res, res_body_plain)
        if res_body_modified is False:
            self.send_error(403)
            return
        elif res_body_modified is not None:
            res_body_plain = res_body_modified
            res_body = self.encode_content_body(res_body_plain, content_encoding)
            res.headers['Content-Length'] = str(len(res_body))

        setattr(res, 'headers', self.filter_headers(res.headers))

        self.wfile.write("%s %d %s\r\n" % (self.protocol_version, res.status, res.reason))
        for line in res.headers.headers:
            self.wfile.write(line)
        self.end_headers()
        self.wfile.write(res_body)
        self.wfile.flush()
        
    def relay_streaming(self, res):
        self.wfile.write("%s %d %s\r\n" % (self.protocol_version, res.status, res.reason))
        for line in res.headers.headers:
            self.wfile.write(line)
        self.end_headers()
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

        # accept only supported encodings
        if 'Accept-Encoding' in headers:
            ae = headers['Accept-Encoding']
            filtered_encodings = [x for x in re.split(r',\s*', ae) if x in ('identity', 'gzip', 'x-gzip', 'deflate')]
            headers['Accept-Encoding'] = ', '.join(filtered_encodings)

        return headers

    def encode_content_body(self, text, encoding):
        if encoding == 'identity':
            data = text
        elif encoding in ('gzip', 'x-gzip'):
            io = StringIO()
            with gzip.GzipFile(fileobj=io, mode='wb') as f:
                f.write(text)
            data = io.getvalue()
        elif encoding == 'deflate':
            data = zlib.compress(text)
        else:
            raise Exception("Unknown Content-Encoding: %s" % encoding)
        return data

    def decode_content_body(self, data, encoding):
        if encoding == 'identity':
            text = data
        elif encoding in ('gzip', 'x-gzip'):
            io = StringIO(data)
            with gzip.GzipFile(fileobj=io) as f:
                text = f.read()
        elif encoding == 'deflate':
            try:
                text = zlib.decompress(data)
            except zlib.error:
                text = zlib.decompress(data, -zlib.MAX_WBITS)
        else:
            raise Exception("Unknown Content-Encoding: %s" % encoding)
            
        return text

    def send_cacert(self):
        with open(self.cacert, 'rb') as f:
            data = f.read()

        self.wfile.write("%s %d %s\r\n" % (self.protocol_version, 200, 'OK'))
        self.send_header('Content-Type', 'application/x-x509-ca-cert')
        self.send_header('Content-Length', len(data))
        self.send_header('Connection', 'close')
        self.end_headers()
        self.wfile.write(data)

    def request_handler(self, req, req_body):
        pass

    def response_handler(self, req, req_body, res, res_body):
        pass


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

        log.warn(messages.module_net_proxy.proxy_starting_s_i % ( self.args['lhost'], self.args['lport'] ))
        log.warn(messages.module_net_proxy.proxy_set_proxy)

        initialize_certificates()

        if self.args['no_background']:
            log.warn(messages.module_net_proxy.proxy_started_foreground)
            run_proxy2(
                hostname = self.args['lhost'],
                port = self.args['lport']
            )
        else:
            log.warn(messages.module_net_proxy.proxy_started_background)
            server_thread = threading.Thread(target=run_proxy2, kwargs = {
                'hostname': self.args['lhost'],
                'port': self.args['lport']
            })
            server_thread.daemon = True
            server_thread.start()
