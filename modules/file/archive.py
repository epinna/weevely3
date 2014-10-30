from core.vectors import PhpFile
from core.module import Module
from core import messages
from core import modules
from core.loggers import log
import os

class Archive(Module):

    """A tar, gzip, bzip, and zip archives manager."""

    aliases = [ 'tar', 'gzip', 'gunzip', 'bzip2', 'bunzip2', 'zip', 'unzip' ]

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
            ),
            PhpFile(
              payload_path = os.path.join(self.folder, 'php_tar.tpl'),
              name = 'php_tar',
            ),
            PhpFile(
              payload_path = os.path.join(self.folder, 'php_gzip.tpl'),
              name = 'php_gzip',
            ),
            PhpFile(
              payload_path = os.path.join(self.folder, 'php_zip.tpl'),
              name = 'php_zip',
            ),
            PhpFile(
              payload_path = os.path.join(self.folder, 'php_tgz.tpl'),
              name = 'php_tgz',
            )
            ]
        )

        self.supported_types = (
            ('tgz', ( '.tgz', '.tar.gz' )),
            ('tar', ( '.tar' )),
            ('gzip', ( '.gz' )),
            ('zip', ( '.zip' )),
            ('bzip2', ( '.bz2' )),
        )

        self.register_arguments([
          { 'name' : 'action', 'choices' : ( 'extract', 'create' ), 'default' : 'extract', 'help' : 'Action extract|create. Default: extract.' },
          { 'name' : 'rpath', 'help' : 'Remote archive file path' },
          { 'name' : 'rfiles', 'help' : 'Files to add on creation', 'nargs' : '*', 'default' : [ '.' ] },
          { 'name' : '-method', 'choices' : [ t[0] for t in self.supported_types ] },
        ])

    def run(self, args):

        args['templates'] = self.folder

        if not args.get('method'):
            for atype, aexts in self.supported_types:
                if any(args['rpath'].endswith(e) for e in aexts):
                    args['method'] = atype
                    break

        if not args.get('method'):
            log.warn(messages.module_file_archive.archive_type_not_set)
            return

        return self.vectors.get_result(
            name = 'php_%s' % args['method'],
            format_args = args,
        )
