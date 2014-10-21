from core.vectors import PhpFile, ShellCmd
from core.module import Module
from core.loggers import log
from core import messages
import random
import os


class Perms(Module):

    """Find files with given write, read, or execute permission."""

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
              payload_path = os.path.join(self.folder, 'bfs_walker.tpl'),
              name = 'php_recursive',
            ),
            ShellCmd(
              # -print -quit must be at the end of the command
              payload = """find ${rpath} ${ '-maxdepth 1' if no_recursion else '' } ${ '-writable' if writable else '' } ${ '-readable' if readable else '' } ${ '-executable' if executable else '' } ${ '-type %s' % (ftype) if (ftype == 'd' or ftype == 'f') else '' } ${ "-regex '.*%s.*'" % (name_regex) if name_regex else '' } ${ '-print -quit' if quit else '' }""",
              name = "sh_find",
              arguments = [
                "-stderr_redirection",
                " 2>/dev/null",
              ]
            )
            ]
        )

        self.register_arguments([
          { 'name' : 'rpath', 'help' : 'Starting path' },
          { 'name' : '-quit', 'action' : 'store_true', 'default' : False, 'help' : 'Quit at first result' },
          { 'name' : '-writable', 'action' : 'store_true' },
          { 'name' : '-readable', 'action' : 'store_true' },
          { 'name' : '-executable', 'action' : 'store_true' },
          { 'name' : '-ftype', 'help' : 'File type', 'choices' : ( 'f', 'd' ) },
          { 'name' : '-name-regex', 'help' : 'Regular expression to match file name' },
          { 'name' : '-no-recursion', 'action' : 'store_true', 'default' : False },
          { 'name' : '-vector', 'choices' : self.vectors.get_names(), 'default' : 'php_recursive' },
        ])

    def run(self, args):
        result = self.vectors.get_result(args['vector'], args)
        return result.split('\n') if isinstance(result,str) else result

    def print_result(self, result):
        if result: log.info('\n'.join(result))
