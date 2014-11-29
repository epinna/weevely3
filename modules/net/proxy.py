from core.loggers import log, dlog
from core import messages
from core.vectors import ModuleExec
from core.module import Module
import BaseHTTPServer
import SocketServer
import socket
import threading

class HTTPProxyRequestHandler(BaseHTTPServer.BaseHTTPRequestHandler):

    def do_request(self):

        if self.command == 'CONNECT' or self.path.startswith('https'):
            log.warn(messages.module_net_proxy.https_not_implemented)
            self.requestline = ''
            self.request_version = ''
            self.command = ''
            self.send_error(
                501,
                messages.module_net_proxy.https_not_implemented
            )
            return

        net_curl_args = [
            self.path,
            '-X',
            self.command,
            '-i'
        ]

        self.headers = dict(
            (k, v) for (k, v) in self.headers.items() if k.lower() not in
            (
                'keep-alive',
                'proxy-connection',
                'connection'
            )
        )

        self.headers['Proxy-Connection'] = 'close'

        for h in self.headers:
            net_curl_args += [ '-H', '%s: %s' % ( h.title(), self.headers[h] ) ]

        if self.command == 'POST':
            content_len = int(self.headers.getheader('content-length', 0))
            net_curl_args += [ '-d', self.rfile.read(content_len) ]

        result, headers, saved = ModuleExec(
            'net_curl',
            net_curl_args
        ).run()

        print '> ' + '\r\n> '.join([ '%s: %s' % (h.title(), self.headers[h]) for h in self.headers ])
        print '< ' + '\r\n< '.join(headers)

        self.wfile.write('\r\n'.join(headers))
        self.end_headers()
        self.wfile.write(result)

    def handle_one_request(self):

        try:
            self.raw_requestline = self.rfile.readline(65537)
            if len(self.raw_requestline) > 65536:
                self.requestline = ''
                self.request_version = ''
                self.command = ''
                self.send_error(414)
                return
            if not self.raw_requestline:
                self.close_connection = 1
                return
            if not self.parse_request():
                # An error code has been sent, just exit
                return

            self.do_request()

            self.wfile.flush() #actually send the response if not already done.
        except socket.timeout, e:
            dlog.warn(request_timed_out_s % str(e))
            self.close_connection = 1
            return

    def log_message(self, format, *args):
        log.debug(
                "%s - - [%s] %s\n" %
                    (self.client_address[0],
                    self.log_date_time_string(),
                    format % args)
                )

class Proxy(Module):

    """Proxy local HTTP traffic through the target."""

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
            { 'name' : '-lport', 'default' : 8080, 'type' : int }
        ])

    def run(self, args):

        server = BaseHTTPServer.HTTPServer(
            ( args['lhost'], args['lport'] ),
            HTTPProxyRequestHandler
        )
        server.serve_forever()
