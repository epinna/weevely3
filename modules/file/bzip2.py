from core.vectors import PhpFile, ModuleExec
from core.module import Module
from core import messages
from core import modules
from core.loggers import log
import os

class Bzip2(Module):

    """Compress or expand bzip2 files."""

    aliases = [ 'bzip2', 'bunzip2' ]

    def init(self):

        self.register_info(
            {
                'author': [
                    'Emilio Pinna'
                ],
                'license': 'GPLv3'
            }
        )

        self.register_vectors(
            [
            PhpFile(
              payload_path = os.path.join(self.folder, 'php_bzip2.tpl'),
              name = 'php_bzip2',
            )
            ]
        )

        self.register_arguments([
          { 'name' : 'rpaths', 'help' : 'Remote file paths', 'nargs' : '+' },
          { 'name' : '--decompress', 'action' : 'store_true', 'default' : False, 'help' : 'Simulate gunzip' },
          { 'name' : '--keep', 'action' : 'store_true', 'default' : False, 'help' : 'Keep (don\'t delete) input files' },
        ])

    def run(self):

        # The correct execution returns something only on errors
        result_err = self.vectors.get_result(
            name = 'php_bzip2',
            format_args = self.args,
        )

        if result_err:
            log.warning(result_err)
            return

        return True
