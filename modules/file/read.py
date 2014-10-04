from core.vectors import PhpCmd, ShellCmd, ModuleCmd, Os
from core.module import Module
from core import modules
import tempfile

class Read(Module):

    """Read remote file from the remote filesystem."""

    def init(self):

        self.register_info(
            {
                'author': [
                    'Emilio Pinna'
                ],
                'license': 'GPLv3'
            }
        )

        self.register_arguments([
          { 'name' : 'rpath', 'help' : 'Remote file path' },
          { 'name' : '-vector', 'choices' : modules.loaded['file_download'].vectors.get_names() }
        ])

    def run(self, args):

        # Get a temporary file name
        temp_file = tempfile.NamedTemporaryFile()
        args['lpath'] = temp_file.name

        # Run file_download
        result = ModuleCmd(
                    'file_download',
                    [ args.get('rpath'), '${lpath}' ],
                    name = 'file_download'
                ).run(args)

        # Delete temp file
        temp_file.close()

        return result
