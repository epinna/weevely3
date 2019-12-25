from core.vectors import PhpCode, ShellCmd, ModuleExec, Os
from core.module import Module
from core import modules
from core import messages
from core.loggers import log

class Enum(Module):

    """Check existence and permissions of a list of paths."""

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
          { 'name' : 'paths', 'help' : 'One or more paths', 'nargs' : '*' },
          { 'name' : '-lpath-list', 'help' : 'The local file containing the list of paths' },
          { 'name' : '-print', 'help' : 'Print the paths not found too', 'action' : 'store_true', 'default' : False }
        ])

    def run(self):

        paths = []

        lpath = self.args.get('lpath_list')
        if lpath:

            try:
                with open(lpath, 'r') as lfile:
                    paths = lfile.read().split('\n')
            except Exception as e:
                log.warning(
                  messages.generic.error_loading_file_s_s % (lpath, str(e)))
                return

        paths += self.args.get('paths') if self.args.get('paths') else []

        results = {}

        for path in paths:

            result = ModuleExec( "file_check", [ path, "perms" ]).run()
            if result or self.args.get('print'):
                results[path] = result

        return results


    def print_result(self, result):

        if not result: return

        result_verbose = {}

        for path, perms in result.items():

            if len(perms) == 1 and perms[0] == 'e':
                result_verbose[path] = 'exists'
            else:
                verbose_string = ' '.join([
                    'writable' if 'w' in perms else '',
                    'readable' if 'r' in perms else '',
                    'executable' if 'x' in perms else ''
                ])

                # Re split to delete multiple whitespaces
                result_verbose[path] = ' '.join(
                    verbose_string.strip().split()
                )

        return Module.print_result(self, result_verbose)
