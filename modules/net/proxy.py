from core.loggers import log, dlog
from core import messages
from core.vectors import ModuleExec
from core.module import Module
import BaseHTTPServer
import SocketServer
import socket
import threading

class MultiThreadedHTTPServer(SocketServer.ThreadingMixIn, BaseHTTPServer.BaseHTTPRequestHandler):
    pass

class HTTPProxyRequestHandler(MultiThreadedHTTPServer):

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

        for h in self.headers:
            if h.title() in ('Keep-Alive', 'Proxy-Connection', 'Connection'):
                continue
            net_curl_args += [ '-H', '%s: %s' % ( h.title(), self.headers[h] ) ]

        net_curl_args += [ '-H', 'Proxy-Connection: close' ]

        if self.command == 'POST':
            content_len = int(self.headers.getheader('content-length', 0))
            net_curl_args += [ '-d', self.rfile.read(content_len) ]

        result, headers, saved = ModuleExec(
            'net_curl',
            net_curl_args
        ).run()

        dlog.debug('> ' + '\r\n> '.join([ '%s: %s' % (h.title(), self.headers[h]) for h in self.headers ]))
        dlog.debug('< ' + '\r\n< '.join(headers))

        self.wfile.write('\r\n'.join(headers))
        self.wfile.write('\r\n\r\n')
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
            dlog.warn(messages.module_net_proxy.request_timed_out_s % str(e))
            self.close_connection = 1
            return

    def log_message(self, format, *args):
        log.debug(
                "%s - - [%s] %s\n" %
                    (self.client_address[0],
                    self.log_date_time_string(),
                    format % self.args)
                )

class Proxy(Module):

    """Proxify local HTTP traffic passing through the target."""

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

        server = BaseHTTPServer.HTTPServer(
            ( self.args['lhost'], self.args['lport'] ),
            HTTPProxyRequestHandler
        )

        log.warn(messages.module_net_proxy.proxy_set_address_s_i % ( self.args['lhost'], self.args['lport'] ))

        if self.args['no_background']:
            log.warn(messages.module_net_proxy.proxy_started_foreground)
            server.serve_forever()
        else:
            log.warn(messages.module_net_proxy.proxy_started_background)
            server_thread = threading.Thread(target=server.serve_forever)
            server_thread.daemon = True
            server_thread.start()
