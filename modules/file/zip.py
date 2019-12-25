from core.vectors import PhpFile, ModuleExec
from core.module import Module
from core import messages
from core import modules
from core.loggers import log
import os

class Zip(Module):

    """Compress or expand zip files."""

    aliases = [ 'zip', 'unzip' ]

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
              payload_path = os.path.join(self.folder, 'php_zip.tpl'),
              name = 'php_zip',
            )
            ]
        )

        self.register_arguments([
          { 'name' : 'rzip', 'help' : 'Remote ZIP file' },
          { 'name' : 'rfiles', 'help' : 'Remote files to compress. If decompressing, set destination folder.', 'nargs' : '+' },
          { 'name' : '--decompress', 'action' : 'store_true', 'default' : False, 'help' : 'Simulate unzip' },
        ])

    def run(self):

        # The correct execution returns something only on errors
        result_err = self.vectors.get_result(
            name = 'php_zip',
            format_args = self.args,
        )

        if result_err:
            log.warning(result_err)
            return

        return True
