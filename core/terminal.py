import string
from urllib.parse import urlparse

from mako import template
from prompt_toolkit import PromptSession, HTML
from prompt_toolkit import print_formatted_text
from prompt_toolkit.completion import Completer, Completion
from prompt_toolkit.history import FileHistory
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.key_binding.bindings import named_commands
from prompt_toolkit.output import ColorDepth
from prompt_toolkit.styles import Style

from core import messages, modules, config
from core.loggers import log
from core.module import Status
from core.weexceptions import ChannelException

IDENTCHARS = string.ascii_letters + string.digits + '_'


class CustomCompleter(Completer):
    terminal = dict()

    def __init__(self, terminal):
        self.terminal = terminal

    def get_completions(self, document, complete_event):
        for attr in dir(self.terminal):
            module = ''
            alias = False
            if attr.startswith('do_alias_'):
                module = ':'+attr[9:]
                alias = True
            elif attr.startswith('do_'):
                module = ':'+attr[3:]

            classname = ('alias' if alias else 'module')
            if module and module.startswith(document.text):
                yield Completion(module,
                                 start_position=-document.cursor_position,
                                 style=f'class:completion-menu.completion.{classname}',
                                 selected_style=f'class:completion-menu.completion.current.{classname}',
                                 )


class Terminal:
    session = dict()
    kb = KeyBindings()
    style = Style.from_dict({
        'bottom-toolbar': 'noreverse',
        'bottom-toolbar.text': 'bg:#ff0000',
        'rprompt': 'bg:#ff0066 #000000',
        'username': '#999999 bold',
        'at': '#00aa00',
        'colon': '#ffffff',
        'pound': '#00aa00',
        'host': '#ff00ff',
        'path': 'ansicyan',
        'mode': '#ff0000',
        'gutter': '#999999',
        'label': '#00aa00 bold',
        'value': '#33ff66',

        'completion-menu': 'bg:#96d0f7 #000000',
        'completion-menu.completion.current': 'bg:#0077ff #000000',
        'completion-menu.completion.alias': 'bg:#1a9cf2',
    })

    def __init__(self, session):
        self.session = session
        self.prompt_session = PromptSession(history=FileHistory(config.history_path))
        self.completer = CustomCompleter(self)

        self._load_modules()
        self._print_intro()

    def cmdloop(self):
        while True:
            try:
                line = self.prompt_session.prompt(self.get_prompt_message,
                                                  color_depth=ColorDepth.TRUE_COLOR,
                                                  complete_while_typing=True,
                                                  reserve_space_for_menu=10,
                                                  completer=self.completer,
                                                  key_bindings=self.kb,
                                                  style=self.style,
                                                  )
                line = self.precmd(line)
                self.onecmd(line)
            except KeyboardInterrupt:
                # Quit when pressing Ctrl-C while prompt is empty
                if len(self.prompt_session.default_buffer.text) == 0:
                    raise EOFError

    def precmd(self, line):
        self.init_default_shell()
        return line

    def onecmd(self, line):
        if not line:
            return

        cmd, args, line = self.parseline(line)

        try:
            func = getattr(self, 'do_' + cmd.lstrip(':'))
            return func(args, cmd)
        except AttributeError:
            return self.default(line)

    def default(self, line):
        if not line:
            return

        default_shell = self.session.get('default_shell')

        if not default_shell:
            return

        result = modules.loaded[default_shell].run_argv([line])

        if not result:
            return

        # Clean trailing newline if existent to prettify output
        result = result[:-1] if (
                isinstance(result, str) and
                result.endswith('\n')
        ) else result

        print(result)

    def parseline(self, line):
        """Parse the line into a command name and a string containing
        the arguments.  Returns a tuple containing (command, args, line).
        'command' and 'args' may be None if the line couldn't be parsed.
        """
        line = line.strip()

        if line and line[0] == ':':
            line = line[1:]

        if not line:
            return None, None, line
        elif line[0] == '?':
            line = 'help ' + line[1:]
        elif line[0] == '!':
            if hasattr(self, 'do_shell'):
                line = 'shell ' + line[1:]
            else:
                return None, None, line
        i, n = 0, len(line)
        while i < n and line[i] in IDENTCHARS: i = i + 1
        cmd, arg = line[:i], line[i:].strip()
        return cmd, arg, line

    def init_default_shell(self):
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
        # if self.session.get('default_shell') == 'shell_php':
        #    log.info(messages.terminal.welcome_no_shell)
        #    self._print_command_replacements()
        #    log.info('\nweevely> %s' % line)

        # Get hostname and whoami if not set
        if not self.session['system_info']['results'].get('hostname'):
            modules.loaded['system_info'].run_argv(["-info", "hostname"])

        if not self.session['system_info']['results'].get('whoami'):
            modules.loaded['system_info'].run_argv(["-info", "whoami"])

        # Get current working directory if not set
        # Should be OK to repeat this every time if not set.
        if not self.session['file_cd']['results'].get('cwd'):
            self.do_file_cd(".")

    def get_prompt_message(self):
        shell = self.session.get('default_shell')
        pound = '?'
        if not shell:
            pound = 'weevely>'
        elif shell == 'shell_sh':
            pound = '$'
        elif shell == 'shell_php':
            pound = 'PHP>'

        info = self.session.get_connection_info()

        if not shell or len(info.get('user')) == 0:
            return [
                ('class:pound', pound),
                ('class:space', ' '),
            ]

        msg = []

        msg.extend([
            ('class:username', info.get('user')),
            ('class:at', '@'),
            ('class:host', info.get('host')),
            ('class:colon', ':'),
            ('class:path', info.get('path')),
            ('class:space', ' '),
            ('class:pound', pound),
            ('class:space', ' '),
        ])

        return msg

    def do_show(self, line, cmd):
        """Command "show" which prints session variables"""

        self.session.print_to_user(line)

    def do_set(self, line, cmd):
        """Command "set" to set session variables."""

        try:
            args = shlex.split(line)
        except Exception as e:
            import traceback;
            log.debug(traceback.format_exc())
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
            setattr(Terminal, 'do_%s' % (module_name), module_class.run_cmdline)

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

    def _print_intro(self):
        info = self.session.get_connection_info()

        hostname = info.get('host')
        if not hostname:
            urlparsed = urlparse(info.get('url'))
            if urlparsed and urlparsed.netloc:
                hostname = urlparsed.netloc
            else:
                hostname = 'undefined host'

        print_formatted_text(HTML(template.Template(
            messages.terminal.welcome_to_s
        ).render(
            path=self.session.get('path'),
            version=messages.version,
            default_shell=self.session.get('default_shell'),
            url=info.get('url'),
            user=info.get('user'),
            hostname=hostname,
            conn_path=info.get('path'),
        )), style=self.style)

    @staticmethod
    @kb.add('enter')
    def _enter_key(event) -> None:
        buff = event.current_buffer
        if buff.complete_state:
            named_commands.complete(event)
            buff.insert_text(' ')
        else:
            named_commands.accept_line(event)
