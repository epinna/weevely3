from core.weexceptions import FatalException, ChannelException
from core.loggers import log, dlog
from core import messages
from core import modules
from core import config
from core.module import Status
import utils
from mako import template

try:
    import gnureadline as readline
except ImportError:
    import readline

import cmd
import glob
import os
import shlex
import atexit
import sys

class CmdModules(cmd.Cmd):

    identchars = cmd.Cmd.identchars + ':'
    doc_header = "Modules and commands (type :help <module>):"
    nohelp = "[!] No help on %s"

    def complete(self, text, state):
        """Return the next possible completion for 'text'.

        If a command has not been entered, then complete against command list.
        Otherwise try to call complete_<command> to get list of completions.
        """
        if state == 0:
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
            if self.completion_matches[state].startswith('alias_'):
                if self.session.get('default_shell') == 'shell_php':
                    return self.completion_matches[state][6:]
                else:
                    return ''
            else:
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
        if cmd in (None, ''):
            return self.default(line)
        self.lastcmd = line
        if line == 'EOF' :
            #self.lastcmd = ''
            raise EOFError()
        if cmd:
            # Try running module  command
            try:
                func = getattr(self, 'do_' + cmd.lstrip(':'))
            except AttributeError:
                # If there is no module command, check if we have a PHP shelli
                # And in case try running alias command
                if self.session.get('default_shell') == 'shell_php' or cmd.lstrip(':') == 'cd':
                    try:
                        func = getattr(self, 'do_alias_' + cmd.lstrip(':'))
                    except AttributeError:
                        pass
                    else:
                        return func(arg, cmd)
            else:
                return func(arg, cmd)

        return self.default(line)

    def _print_modules(self):

        data = []
        for module_group, names in modules.loaded_tree.items():
            for module_name in names:
                data.append([ ':%s' % module_name, modules.loaded[module_name].info.get('description', '') ])

        if data: log.info(utils.prettify.tablify(data, table_border = False))

    def _print_command_replacements(self):

        data = []
        for module_name, module in modules.loaded.items():
            if module.aliases:
                data.append([ ', '.join(module.aliases), module_name ])

        if data: log.info(utils.prettify.tablify(data, table_border = False))

    def do_help(self, arg, command):
        """Fixed help."""

        print()

        self._print_modules()

        if self.session['shell_sh']['status'] == Status.RUN: print(); return

        log.info(messages.terminal.help_no_shell)
        self._print_command_replacements()

        print()


class Terminal(CmdModules):

    """Weevely Terminal"""

    def __init__(self, session):

        cmd.Cmd.__init__(self)

        self.session = session
        self.prompt = 'weevely> '

        # Load all available modules
        self._load_modules()

        # Load history file
        self._load_history()

        # Set a nice intro
        self.intro = template.Template(
            messages.terminal.welcome_to_s
        ).render(
            path = self.session.get('path'),
            conn_info = session.get_connection_info(),
            version = messages.version,
            default_shell = self.session.get('default_shell')
        )

    def emptyline(self):
        """Disable repetition of last command."""

        pass

    def precmd(self, line):
        """Before to execute a line commands. Confirm shell availability and get basic system infos """

        dlog.info('>>>> %s' % line)

        # Skip slack check is not a remote command
        if not line or any(
                        line.startswith(cmnd) for cmnd in (
                            ':set',
                            ':unset',
                            ':show',
                            ':help'
                        )
                    ):
            return line

        # Trigger the shell_sh/shell_php probe if
        # 1. We never tried to raise shells (shell_sh = IDLE)
        # 2. The basic intepreter shell_php is not running.
        if (
            self.session['shell_sh']['status'] == Status.IDLE or
            self.session['shell_php']['status'] != Status.RUN
            ):

            # We're implying that no shell is set, so reset default shell
            self.session['default_shell'] = None

            # Force shell_php to idle to avoid to be skipped by shell_sh
            self.session['shell_php']['status'] = Status.IDLE

            # Catch every exception which prevent the shell setup.
            # We imply that at every channel change (proxy, channel name)
            # this piece of code will be executed.
            try:
                self.session['shell_sh']['status'] = modules.loaded['shell_sh'].setup()
            except ChannelException as e:
                log.error(str(e))
                return ''

        # Set default_shell in any case (could have been changed runtime)
        for shell in ('shell_sh', 'shell_php'):

            if self.session[shell]['status'] == Status.RUN:
                self.session['default_shell'] = shell
                break

        # Kill the execution if no shell were loaded
        if not self.session.get('default_shell'):
            log.error(messages.terminal.backdoor_unavailable)
            return ''

        # TODO: do not print this every loop
        # Print an introductory string with php shell
        #if self.session.get('default_shell') == 'shell_php':
        #    log.info(messages.terminal.welcome_no_shell)
        #    self._print_command_replacements()
        #    log.info('\nweevely> %s' % line)

        # Get hostname and whoami if not set
        if not self.session['system_info']['results'].get('hostname'):
            modules.loaded['system_info'].run_argv([ "-info", "hostname"])

        if not self.session['system_info']['results'].get('whoami'):
            modules.loaded['system_info'].run_argv(["-info", "whoami"])

        # Get current working directory if not set
        # Should be OK to repeat this every time if not set.
        if not self.session['file_cd']['results'].get('cwd'):
            self.do_file_cd(".")

        return line

    def postcmd(self, stop, line):

        default_shell = self.session.get('default_shell')

        if not default_shell:
            self.prompt = 'weevely> '
        else:
            if default_shell == 'shell_sh':
                prompt = '$'
            elif default_shell == 'shell_php':
                prompt = 'PHP>'
            else:
                prompt = '?'

            # Build next prompt, last command could have changed the cwd
            self.prompt = '%s %s ' % (self.session.get_connection_info(), prompt)


    def default(self, line):
        """Default command line send."""

        if not line: return

        default_shell = self.session.get('default_shell')

        if not default_shell: return

        result = modules.loaded[default_shell].run_argv([line])

        if not result: return

        # Clean trailing newline if existent to prettify output
        result = result[:-1] if (
                isinstance(result, str) and
                result.endswith('\n')
            ) else result

        log.info(result)

    def do_show(self, line, cmd):
        """Command "show" which prints session variables"""

        self.session.print_to_user(line)

    def do_set(self, line, cmd):
        """Command "set" to set session variables."""

        try:
            args = shlex.split(line)
        except Exception as e:
            import traceback; log.debug(traceback.format_exc())
            log.warning(messages.generic.error_parsing_command_s % str(e))

        # Set the setting
        else:
            if len(args) < 2:
                log.warning(messages.terminal.set_usage)
            elif len(args) >= 2:
                args[1] = ' '.join(args[1:])
                self.session.set(args[0], args[1])

    def do_unset(self, line, cmd):
        """Command "unset" to unset session variables."""

        # Print all settings that startswith args[0]
        if not line:
            log.warning(messages.terminal.unset_usage)

        # Set the setting
        else:
            self.session.unset(line)

    def _load_modules(self):
        """Load all modules assigning corresponding do_* functions."""

        for module_name, module_class in modules.loaded.items():

            # Set module.do_terminal_module() function as terminal
            # self.do_modulegroup_modulename()
            setattr(
                Terminal, 'do_%s' %
                (module_name), module_class.run_cmdline)

            # Set module.do_alias() function as terminal
            # self.do_alias() for every defined `Module.aliases`.
            for alias in module_class.aliases:
                setattr(
                    Terminal, 'do_alias_%s' %
                    (alias), module_class.run_alias)
                setattr(
                    Terminal, 'help_%s' %
                    (alias), module_class.help)

            # Set module.help() function as terminal
            # self.help_modulegroup_modulename()
            setattr(
                Terminal, 'help_%s' %
                (module_name), module_class.help)

    def _load_history(self):
        """Load history file and register dump on exit."""

        # Create a file without truncating it in case it exists.
        open(config.history_path, 'a').close()

        readline.set_history_length(100)
        try:
            readline.read_history_file(config.history_path)
        except IOError:
            pass
        atexit.register(readline.write_history_file,
            config.history_path)
