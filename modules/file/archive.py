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

        self.supported_types = {
            'tar' : [ '.tar' ],
            'gzip' : [ '.gz', '.tgz' ],
            'zip' : [ '.zip' ],
            'bzip' : [ '.bz2' ],
        }

        self.register_arguments([
          { 'name' : 'action', 'choices' : ( 'extract', 'create' ), 'default' : 'extract', 'help' : 'Action extract|create. Default: extract.' },
          { 'name' : 'rpath_archive', 'help' : 'Remote archive file path' },
          { 'name' : 'rpath_files', 'help' : 'Files to add on creation', 'nargs' : '*' },
          { 'name' : '-archive-type', 'choices' : self.supported_types.keys() },
          { 'name' : '-overwrite', 'action' : 'store_true', 'default' : False, 'help' : 'Overwrite on extraction' },
        ])

    def run(self, args):

        if not args.get('archive_type'):
            for atype, aexts in self.supported_types.items():
                if any(args['rpath_archive'].endswith(e) for e in aexts):
                    args['archive_type'] = atype
                    break

        if not args.get('archive_type'):
            log.warn(messages.module_file_archive.archive_type_not_set)
            return

        return PhpFile(os.path.join(self.folder, 'archive.tpl')).run(args)
