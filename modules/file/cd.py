from core.vectors import PhpCode, ModuleExec
from core.module import Module
from core import messages
from core.loggers import log
import random


class Cd(Module):

    """Change current working directory."""

    aliases = [ 'cd' ]

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
          { 'name' : 'dir', 'help' : 'Target folder', 'nargs' : '?' }
        ])

    def run(self):

        # When no folder is specified, change folder to SCRIPT_NAME to
        # simulate the bash behaviour. If not available, use current dir.

        if not self.args.get('dir'):
            script_folder = ModuleExec(
                        'system_info',
                        [ '-info', 'script_folder' ]
                    ).load_result_or_run(
                        result_name = 'script_folder'
                    )

            self.args['dir'] = script_folder if script_folder else '.'

        # The execution and result storage is done manually cause
        # no result has to be stored if the execution fails. This
        # is not simple to implement using
        # self.vectors.get_result(.., store_result).

        folder = PhpCode("""@chdir('${dir}')&&print(@getcwd());""", "chdir").run(
                    self.args
                )

        if folder:
            self._store_result('cwd', folder)
        else:
            log.warning(
                messages.module_file_cd.failed_directory_change_to_s %
                (self.args['dir'])
            )

    def run_alias(self, line, cmd):

        # Run this alias independently from the shell_sh status
        return self.run_cmdline(line)
