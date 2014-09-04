from core.vectors import Os, Vector
from core.module import Module
from core import messages
from core.loggers import log
import random


class Cd(Module):

    """Change current working directory.

    Usage:
      file_cd <dir>

    """

    def initialize(self):

        self._register_infos(
            {
                'name': 'Change directory',
                'description': __doc__,
                'author': [
                    'Emilio Pinna'
                ],
                'license': 'GPLv3'
            }
        )

        self._register_arguments(
            # Declare mandatory arguments
            arguments=[
                'dir'
            ])

    def run(self, args):
        
        folder = Vector("""@chdir("${args['dir']}") && print(getcwd());""", "chdir").run({ 'args' : args })

        if folder:
            # Store cwd used by other modules
            self._store_result('cwd', dir)
        else:
            log.warning(
                messages.module_file_cd.failed_directory_change_to_s %
                (args['dir']))
