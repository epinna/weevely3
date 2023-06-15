from core.module import Module, Status
from core.vectors import PhpCode, PythonCode, Os


class Ssh(Module):
    """Execute shell commands through SSH without PTY

  Vector          | Native | Comment
 -----------------|--------|-----------------------------------------
  php             |  No    | SSH2 extension
  py.paramiko     |  No    |
  py.pexpect      |  No    | Rarely installed
  py.subprocess   |  Yes   | Stores clear passwd on disk temporarily

/!\\ When using py.subprocess vector the password is stored in a file at <ASKPASS> /!\\
    As a result the file gets truncated, chmod and then removed. Becareful !
    This file has to be executable, you have to insure it spawns on a partition
    that allows execution (ie. not mounted with `noexec`).

  Examples:
     :shell_ssh root@127.0.0.1 Sup3rPassw0rd id
     :shell_ssh -vector py.subprocess -askpass /executable/path -port 1337 root@secret.server Sup3rPassw0rd id
"""

    def init(self):
        self.register_info(
            {
                'author': [
                    'ZanyMonk'
                ],
                'license': 'GPLv3'
            }
        )

        self.register_vectors(
            [
                PhpCode("""
                    if(function_exists("ssh2_connect")){
                        if($c = ssh2_connect("${host}","${port}")){
                            if(ssh2_auth_password($c,"${user}","${password}")){
                                $s = ssh2_exec($c,"${command}${stderr}");
                                stream_set_blocking($s, true);
                                echo stream_get_contents($s);
                                fclose($s);
                            }else{echo "Authentication failed";}
                        }else{echo "Could not connect.";}
                    }else{echo "ModuleNotFound";}
                    """,
                        name="php",
                        ),
                PythonCode("""
                    import paramiko
                    c = paramiko.SSHClient()
                    c.set_missing_host_key_policy(paramiko.MissingHostKeyPolicy())
                    c.connect("${host}", username="${user}", password="${password}", port=int("${port}"))
                    i, o, e = c.exec_command("${command}${stderr}")
                    i.close()
                    for l in iter(o.readline, ""):
                        print(l,end="")
                    """, "py.paramiko"
                           ),
                PythonCode("""
                    from pexpect import pxssh
                    s = pxssh.pxssh()
                    s.options = dict(StrictHostKeyChecking="no", UserKnownHostsFile="/dev/null")
                    s.login("${host}", "${user}", "${password}", port=int("${port}"))
                    c = "${command}"
                    s.sendline(c)
                    s.prompt()
                    print(s.before[len(c) + 2:].decode("utf-8","replace"), end="")
                    """,
                           name="py.pexpect",
                           target=Os.NIX,
                           ),
                PythonCode("""
                    import os,subprocess as s
                    with open("${askpass}", "w") as f:
                        f.write("echo '${password}'")
                        f.close()
                        os.chmod("${askpass}", 0o755)
                    p = s.Popen([ "ssh","-T","-tt","-oUserKnownHostsFile=/dev/null","-oStrictHostKeyChecking=no",
                                  "-p${port}","${user}@${host}","${command}${stderr}"
                                ],
                                shell=False,
                                stdout=s.PIPE, stderr=s.PIPE, stdin=s.PIPE,
                                env={
                                    "DISPLAY": ":99",
                                    "SSH_ASKPASS": "${askpass}"
                                })
                    o, e = p.communicate()
                    os.unlink("${askpass}")
                    print((o if o else e).decode("utf-8","replace"), end="")
                    """,
                           name="py.subprocess",
                           ),
            ])

        self.register_arguments([
            {'name': 'address', 'help': 'user@host[:port]'},
            {'name': 'password', 'help': 'User\'s password'},
            {'name': 'command', 'help': 'Shell command', 'nargs': '+'},
            {'name': '-askpass', 'default': '/tmp/.p',
             'help': 'SSH_ASKPASS location (/!\\ will be overwritten and removed /!\\)'},
            {'name': '-port', 'default': 0, 'type': int, 'help': 'SSH server port'},
            {'name': '-stderr', 'default': ' 2>&1'},
            {'name': '-vector', 'choices': self.vectors.get_names()},
        ])

    def setup(self):
        """Probe all vectors to find a working system-like function.

        The method run_until is not used due to the check of shell_sh
        enabling for every tested vector.

        Args:
            self.args: The dictionary of arguments

        Returns:
            Status value, must be Status.RUN, Status.FAIL, or Status.IDLE.

        """

        args_check = {
            'host': '127.0.0.1',
            'user': 'root',
            'password': 'root',
            'port': 54321,
            'command': 'whoami',
            'stderr': '',
            'askpass': '/tmp/.p',
        }

        def is_valid(result):
            return (self.session['shell_php']['status'] != Status.RUN or  # Stop if shell_php is not running
                    result and 'ModuleNotFound' not in result)  # Or if the result is correct

        (vector_name,
         result) = self.vectors.find_first_result(
            names=[self.args.get('vector', '')],
            format_args=args_check,
            condition=is_valid
        )

        if self.session['shell_php']['status'] == Status.RUN and result:
            self.session['shell_ssh']['stored_args']['vector'] = vector_name
            if 'vector' not in self.args or not self.args['vector']:
                self.args['vector'] = vector_name
            return Status.RUN
        else:
            return Status.FAIL

    def run(self, **kwargs):
        self.args['user'], self.args['host'], self.args['port'] = self._parse_address(self.args['address'])

        self.args['command'] = ' '.join(self.args['command']).replace('"', '\\"')

        return self.vectors.get_result(
            name=self.args['vector'],
            format_args=self.args
        )

    def _parse_address(self, address):
        user = self.session['system_info']['results'].get('whoami', '')
        host = address

        if '@' in address:
            user, host = address.split('@', 1)

        trailing_port = 22
        port = self.args.get('port')
        if ':' in host:
            host, trailing_port = host.split(':', 1)

        if not port:  #
            port = trailing_port

        return user, host, port
