from core.weexceptions import FatalException
from core.loggers import log
from core import messages
from core import modules
from core import config
import readline
import cmd
import glob
import os
import shlex
import atexit

class CmdModules(cmd.Cmd):

    identchars = cmd.Cmd.identchars + ':'

    def complete(self, text, state):
        """Return the next possible completion for 'text'.

        If a command has not been entered, then complete against command list.
        Otherwise try to call complete_<command> to get list of completions.
        """
        if state == 0:
            import readline
            origline = readline.get_line_buffer()

            # Offer completion just for commands that starts
            # with the trigger :
            if origline and not origline.startswith(':'):
                return None

            line = origline.lstrip().lstrip(':')

            stripped = len(origline) - len(line)
            begidx = readline.get_begidx() - stripped
            endidx = readline.get_endidx() - stripped
            if begidx>0:
                cmd, args, foo = self.parseline(line)
                if cmd == '':
                    compfunc = self.completedefault
                else:
                    try:
                        compfunc = getattr(self, 'complete_' + cmd)
                    except AttributeError:
                        compfunc = self.completedefault
            else:
                compfunc = self.completenames
            self.completion_matches = compfunc(text, line, begidx, endidx)
        try:
            return self.completion_matches[state]
        except IndexError:
            return None

    def onecmd(self, line):
        """Interpret the argument as though it had been typed in response
        to the prompt.

        This may be overridden, but should not normally need to be;
        see the precmd() and postcmd() methods for useful execution hooks.
        The return value is a flag indicating whether interpretation of
        commands by the interpreter should stop.

        """
        cmd, arg, line = self.parseline(line)
        if not line:
            return self.emptyline()
        if cmd is None:
            return self.default(line)
        self.lastcmd = line
        if line == 'EOF' :
            #self.lastcmd = ''
            raise EOFError()
        if cmd == '':
            return self.default(line)
        if cmd.startswith(':'):
            try:
                func = getattr(self, 'do_' + cmd[1:])
            except AttributeError:
                return self.default(line)
            return func(arg)
        else:
            return self.default(line)

class Terminal(CmdModules):

    """ Weevely Terminal """

    def __init__(self, session):

        cmd.Cmd.__init__(self)

        self.session = session
        self.prompt = 'weevely> '

        # Load all available modules
        self._load_modules()

        # Load history file
        self._load_history()

    def emptyline(self):
        """ Disable repetition of last command. """

        pass

    def precmd(self, line):
        """ Before to execute a line commands. Confirm shell availability and get basic system infos. """

        # Setup shell_sh if is never tried
        if not self.session['shell_sh']['enabled']:
            self.session['shell_sh']['enabled'] = modules.loaded['shell_sh'].setup()

        # Check results to set the default shell
        for shell in ('shell_sh', 'shell_php'):
            if self.session[shell]['enabled']:
                self.session['default_shell'] = shell
                break

        # Check if some shell is loaded
        if not self.session.get('default_shell'):
            log.error(messages.terminal.backdoor_unavailable)
            return ''

        # Get current working directory if not set
        if not self.session['file_cd']['results'].get('cwd'):
            self.do_file_cd(".")

        # Get hostname and whoami if not set
        if not self.session['system_info']['results'].get('hostname'):
            modules.loaded['system_info'].run_argv(["--info=hostname"])

        if not self.session['system_info']['results'].get('whoami'):
            modules.loaded['system_info'].run_argv(["--info=whoami"])

        return line

    def postcmd(self, stop, line):

        default_shell = self.session.get('default_shell')

        if not default_shell:
            self.prompt = 'weevely> '
        else:
            if default_shell == 'shell_sh':
                prompt = '$'
            elif default_shell == 'shell_ph':
                prompt = 'PHP>'
            else:
                prompt = '?'

            # Build next prompt, last command could have changed the cwd
            self.prompt = '{user}@{host}:{path} {prompt} '.format(
             user=self.session['system_info']['results'].get('whoami', ''),
             host = self.session['system_info']['results'].get('hostname', ''),
             path = self.session['file_cd']['results'].get('cwd', '.'),
             prompt = prompt)

        #return stop

    def default(self, line):
        """ Direct command line send. """

        if not line: return

        result = modules.loaded[self.session['default_shell']].run_argv([line])

        if not result: return

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

    def do_set(self, line):
        """ Command "set" to set session variables """

        args = shlex.split(line)

        # Print all settings that startswith args[0]
        if len(args) < 2:
            self._set_print(args[0] if args else '')

        # Set the setting
        else:
            if len(args) > 2:
                args[1] = ' '.join(args[1:])

            self._set_value(args[0], args[1])

    def _set_print(self, module_filter = ''):

        global_filters = [ 'log' ]

        for mod_name, mod_value in self.session.items():

            if isinstance(mod_value, dict):
                mod_args = mod_value.get('stored_args')

                # Is a module, print all the storable stored_arguments
                for argument, arg_value in mod_args.items():
                    if not module_filter or ("%s.%s" % (mod_name, argument)).startswith(module_filter):
                        log.info("%s.%s = '%s'" % (mod_name, argument, arg_value))
            else:
                # If is not a module, just print if matches with global_filters
                if not module_filter or any(f for f in global_filters if f == mod_name):
                    log.info("%s = '%s'" % (mod_name, mod_value))

    def _set_value(self, module_argument, value):

        if module_argument.count('.') == 1:
            module_name, arg_name = module_argument.split('.')
            self.session[module_name]['stored_args'][arg_name] = value
            log.info("%s.%s = '%s'" % (module_name, arg_name, value))
        else:
            module_name = module_argument
            self.session[module_name] = value
            log.info("%s = '%s'" % (module_name, value))

    def _load_modules(self):
        """ Load all modules assigning corresponding do_* functions. """

        for module_name, module_class in modules.loaded.items():

            # Set module.do_terminal_module() function as terminal
            # self.do_modulegroup_modulename()
            class_do = getattr(module_class, 'run_cmdline')
            setattr(
                Terminal, 'do_%s' %
                (module_name), class_do)

    def _load_history(self):
        """ Load history file and register dump on exit """

        # Create a file without truncating it in case it exists.
        open(config.history_path, 'a').close()

        readline.set_history_length(100)
        readline.read_history_file(config.history_path)
        atexit.register(readline.write_history_file,
            config.history_path)
