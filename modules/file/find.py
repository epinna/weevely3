from core.vectors import PhpFile, ShellCmd
from core.module import Module
from core.loggers import log
from core import messages
import random
import os


class Find(Module):

    """Find files with given names and attributes."""

    aliases = [ 'find' ]

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
              name = 'php_find',
            ),
            ShellCmd(
              # -print -quit must be at the end of the command
              payload = """find ${rpath} ${ '-maxdepth 1' if no_recursion else '' } ${ '-writable' if writable else '' } ${ '-readable' if readable else '' } ${ '-executable' if executable else '' } ${ '-type %s' % (ftype) if (ftype == 'd' or ftype == 'f') else '' } ${ "-%sregex '.*%s.*'" % ( '' if case else 'i', expression) if expression else '' } ${ '-print -quit' if quit else '' }""",
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
          { 'name' : 'expression', 'help' : 'Regular expression to match file name', 'nargs' : '?' },
          { 'name' : '-quit', 'action' : 'store_true', 'default' : False, 'help' : 'Quit at first result' },
          { 'name' : '-writable', 'action' : 'store_true' },
          { 'name' : '-readable', 'action' : 'store_true' },
          { 'name' : '-executable', 'action' : 'store_true' },
          { 'name' : '-ftype', 'help' : 'File type', 'choices' : ( 'f', 'd' ) },
          { 'name' : '-no-recursion', 'action' : 'store_true', 'default' : False },
          { 'name' : '-vector', 'choices' : self.vectors.get_names(), 'default' : 'php_find' },
          { 'name' : '-case', 'help' : 'Case sensitive', 'action' : 'store_true', 'default' : False },
        ])

    def run(self):
        result = self.vectors.get_result(
                    self.args['vector'],
                    self.args
                )

        return result.rstrip().split('\n') if isinstance(result, str) else result

    def print_result(self, result):
        if result: log.info('\n'.join(result))
