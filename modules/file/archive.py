from core.vectors import PhpFile, ModuleExec
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
          { 'name' : 'rfiles', 'help' : 'Files to add on creation', 'nargs' : '+' },
          { 'name' : '-method', 'choices' : [ t[0] for t in self.supported_types ] },
        ])

    def run(self, args):

        # If method is not set, find it from the rpath extension
        if not args.get('method'):
            for atype, aexts in self.supported_types:
                if args['action'] == 'extract' and any(args['rpath'].endswith(e) for e in aexts):
                    args['method'] = atype
                    break
                if args['action'] == 'create' and any(args['rfiles'][0].endswith(e) for e in aexts):
                    args['method'] = atype
                    break

        # With no available method, exits
        if not args.get('method'):
            log.warn(messages.module_file_archive.archive_type_not_set)
            return

        # Check if rpath is readable
        if not ModuleExec("file_check", [ args['rpath'], 'readable' ]).run():
            log.warn(messages.module_file_archive.remote_path_check_failed)
            return

        if args['action'] == 'extract':

            rfile_0_folder = ModuleExec("file_check", [ args['rfiles'][0], 'dir' ]).run()

            # Extracting gzip, bzip, and bzip2, rfiles[0] hasn't to be a folder
            if (args['method'] in ('gzip', 'bzip', 'bzip2') and rfile_0_folder):
                log.warn(messages.module_file_archive.error_extracting_s_file_needed % args['method'])
                return

            # Extracting tar and tgz, rfiles[0] has to be a folder
            if (args['method'] in ('tar', 'tgz') and not rfile_0_folder):
                log.warn(messages.module_file_archive.error_extracting_s_folder_needed % args['method'])
                return

        return self.vectors.get_result(
            name = 'php_%s' % args['method'],
            format_args = args,
        )
