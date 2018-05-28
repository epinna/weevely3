from core.vectors import ShellCmd
from core.module import Module, Status
from core.loggers import log
from core.vectors import Os
from core import messages
from core import modules
import re


class Su(Module):

    """Execute commands with su."""

    aliases = [ 'ifconfig' ]

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
                """expect -c 'spawn su -c "${command}" "${user}"; expect -re "assword"; send "${ passwd }\r\n"; expect eof;'""",
                name = "sh_expect",
                postprocess = lambda x: re.findall('Password: (?:\r\n)?([\s\S]+)', x)[0] if 'Password: ' in x else ''
            ),
            ShellCmd("""python -c 'import pexpect as p,sys;c=p.spawn("su ${user} -c ${command}");c.expect(".*assword:");c.sendline("${ passwd }");i=c.expect([p.EOF,p.TIMEOUT]);sys.stdout.write(c.before[3:] if i!=p.TIMEOUT else "")'""", "pyexpect")
            ]
        )

        self.register_arguments([
          { 'name' : 'passwd', 'help' : 'User\'s password' },
          { 'name' : 'command', 'help' : 'Shell command', 'nargs' : '+' },
          { 'name' : '-user', 'help' : 'User to run the command with', 'default' : 'root' },
          { 'name' : '-stderr_redirection', 'default' : ' 2>&1' },
          { 'name' : '-vector-sh', 'choices' : ( 'system', 'passthru', 'shell_exec', 'exec', 'popen', 'proc_open', 'perl_system', 'pcntl' ) },
          { 'name' : '-vector', 'choices' : self.vectors.get_names() }
        ])

    def setup(self):
        """Probe all vectors to find a working su command.

        The method run_until is not used due to the check of shell_sh
        enabling for every tested vector.

        Args:
            self.args: The dictionary of arguments

        Returns:
            Status value, must be Status.RUN, Status.FAIL, or Status.IDLE.

        """

        args_check = {
           'user' : self.args['user'],
           'passwd' : self.args['passwd'],
           'command' : 'whoami'
        }

        (vector_name,
         result) = self.vectors.find_first_result(
          names = [ self.args.get('vector', '') ],
            format_args = args_check,
            condition = lambda result: (
                # Stop if shell_sh is in FAIL state
                self.session['shell_sh']['status'] == Status.FAIL or
                # Or if the result is correct
                self.session['shell_sh']['status'] == Status.RUN and result and result.rstrip() == self.args['user']
                )
            )

        if self.session['shell_sh']['status'] == Status.RUN and result and result.rstrip() == self.args['user']:
            self.session['shell_su']['stored_args']['vector'] = vector_name
            return Status.RUN
        else:
            log.warn(messages.module_shell_su.error_su_executing)
            return Status.IDLE

    def run(self):

        # Join the command list and

        # Escape the single quotes. This does not protect from \' but
        # avoid to break the query for an unscaped quote.

        self.args['command'] = ' '.join(self.args['command']).replace("'", "\\'")

        format_args = {
           'user' : self.args['user'],
           'passwd' : self.args['passwd'],
           'command' : self.args['command']
        }

        if self.args.get('vector_sh'):
            format_args['vector'] = self.args['vector_sh']

        if self.args.get('stderr_redirection'):
            format_args['stderr_redirection'] = self.args['stderr_redirection']

        return self.vectors.get_result(
         name = self.args['vector'],
         format_args = format_args
        )
