from core.weexceptions import FatalException
from core.loggers import log
from core import messages
from core import modules
import readline
import cmd
import glob
import os
import shlex
import pprint


class Terminal(cmd.Cmd):

    """ Weevely terminal. """

    def __init__(self, session):

        self.session = session
        self.prompt = 'weevely> '
        self._load_modules()

        log.debug(pprint.pformat(dict(session)))

        cmd.Cmd.__init__(self)

    def emptyline(self):
        """ Disable repetition of last command. """

        pass

    def precmd(self, line):
        """ Before to execute a line commands. Confirm shell availability and get basic system infos. """

        # Probe shell_sh if is never tried
        if not self.session['shell_sh']['enabled']:
            self.session['shell_sh']['enabled'] = modules.loaded['shell_sh'].check()

        # Probe shell_php if shell_sh failed
        if not self.session['shell_sh']['enabled']:
            self.session['shell_php']['enabled'] = modules.loaded['shell_php'].check()

        # Check results to set the default shell
        for shell in ('shell_sh', 'shell_php'):
            if self.session[shell]['enabled']:
             self.session['default_shell'] = shell
             break
             
        if not self.session.get('default_shell'):
            raise FatalException(messages.terminal.backdoor_unavailable)

        # Get current working directory if not set
        if not self.session['file_cd']['results'].get('cwd'):
            self.do_file_cd(".")

        # Get hostname and whoami if not set
        if not self.session['system_info']['results'].get('hostname'):
            self.run_system_info(["--info=hostname"])

        if not self.session['system_info']['results'].get('whoami'):
            self.run_system_info(["--info=whoami"])

        return line

    def postcmd(self, stop, line):

        # Build next prompt, last command could have changed the cwd
        self.prompt = '{user}@{host}:{path} {prompt} '.format(
            user=self.session['system_info']['results'].get(
                'whoami', ''), host=self.session['system_info']['results'].get(
                'hostname', ''), path=self.session['file_cd']['results'].get(
                'cwd', '.'), prompt='PHP>' if (
                    self.session['default_shell'] == 'shell_php') else '$')

        return stop

    def default(self, line):
        """ Direct command line send. """

        if not line: return

        result = modules.loaded[self.session['default_shell']].run_argv([line])

        if not result:
            log.info(result)

    def do_cd(self, line):
        """ Command "cd" replacement """

        self.do_file_cd(line)

    def do_ls(self, line):
        """ Command "ls" replacement, if shell_sh is not loaded """

        if self.session['default_shell'] == 'shell_sh':
            self.default('ls %s' % line)
        else:
            self.do_file_ls(line)

    def _load_modules(self):
        """ Load all modules assigning corresponding do_* functions. """

        for module_name, module_class in modules.loaded.items():

            # Set module.do_terminal_module() function as terminal
            # self.do_modulegroup_modulename()
            class_do = getattr(module_class, 'run_cmdline')
            setattr(
                Terminal, 'do_%s' %
                (module_name), class_do)
