from core.vector import PhpCmd
from core.module import Module
from core import messages
from core.loggers import log
import random


class Cd(Module):

    """Change current working directory."""

    def init(self):

        self._register_info(
            {
                'author': [
                    'Emilio Pinna'
                ],
                'license': 'GPLv3'
            }
        )

        self._register_arguments(
            # Declare mandatory arguments
            mandatory = [
                'dir'
            ])

    def run(self, args):

        chdir = '' if args['dir'] == '.' else "@chdir('%s')&&" % args['dir']
        folder = PhpCmd("""${chdir}print(@getcwd());""", "chdir").run({ 'chdir' : chdir })

        if folder:
            # Store cwd used by other modules
            self._store_result('cwd', folder)
        else:
            log.warning(
                messages.module_file_cd.failed_directory_change_to_s %
                (args['dir']))
