from core.vectors import PhpFile, ModuleExec
from core.module import Module
from core import messages
from core import modules
from core.loggers import log
import os

class Tar(Module):

    """Compress or expand tar archives."""

    aliases = [ 'tar' ]

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
              payload_path = os.path.join(self.folder, 'php_tar.tpl'),
              name = 'php_tar',
            )
            ]
        )

        self.register_arguments([
          { 'name' : 'rtar', 'help' : 'Remote Tar file' },
          { 'name' : 'rfiles', 'help' : 'Remote files to compress. If decompressing, set destination folder.', 'nargs' : '+' },
          { 'name' : '--decompress', 'action' : 'store_true', 'default' : False, 'help' : 'Simulate tar -x' },
          { 'name' : '-z', 'action' : 'store_true', 'default' : False, 'help' : 'Simulate tar -xz for gzip compressed archives' },
          { 'name' : '-j', 'action' : 'store_true', 'default' : False, 'help' : 'Simulate tar -xj for bzip2 compressed archives' },
        ])

    def run(self):

        if self.args.get('z'):
            ModuleExec('file_gzip', [ '--keep', '--decompress', self.args['rtar'] ]).run()
            self.args['rtar'] = '.'.join(self.args['rtar'].split('.')[:-1])
        elif self.args.get('j'):
            ModuleExec('file_bzip2', [ '--keep', '--decompress', self.args['rtar'] ]).run()
            self.args['rtar'] = '.'.join(self.args['rtar'].split('.')[:-1])

        # The correct execution returns something only on errors
        result_err = self.vectors.get_result(
            name = 'php_tar',
            format_args = self.args,
        )

        if result_err:
            log.warn(result_err)
            return

        return True
