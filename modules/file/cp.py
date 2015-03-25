from core.vectors import PhpCode, ShellCmd, ModuleExec, Os
from core.module import Module
from core import modules

class Cp(Module):

    """Copy single file."""

    aliases = [ 'cp', 'copy' ]

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
            PhpCode(
              "(@copy('${srcpath}', '${dstpath}')&&print(1))||print(0);",
              name = 'php_copy'
              ),
            PhpCode(
              "(@file_put_contents('${dstpath}', file_get_contents('${srcpath}'))&&print(1))||print(0);",
              name = 'php_file_contents'
            ),
            ShellCmd(
              "cp '${srcpath}' '${dstpath}' && echo 1 || echo 0",
              name = 'sh_cp',
              target = Os.NIX
              ),
            ]
        )

        self.register_arguments([
          { 'name' : 'srcpath', 'help' : 'Remote source file path' },
          { 'name' : 'dstpath', 'help' : 'Remote destination file path' },
          { 'name' : '-vector', 'choices' : self.vectors.get_names() }
        ])

    def run(self):

        vector_name, result = self.vectors.find_first_result(
            names = [ self.args.get('vector') ],
             format_args = self.args,
             condition = lambda result: True if result == '1' else False
        )

        if vector_name and result:
            return True

        return False
