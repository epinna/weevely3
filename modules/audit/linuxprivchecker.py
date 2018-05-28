from core.vectors import ShellCmd, ModuleExec
from core.module import Module
from core import modules
import random
import os

class Linuxprivchecker(Module):

    """Upload and execute linuxprivchecker."""

    def init(self):

        self.register_info(
            {
                'author': [
                    'Ganapati'
                ],
                'license': 'GPLv3'
            }
        )

        self.register_arguments([
          { 'name' : 'rpath', 'help' : 'Remote file path', 'default' : '/tmp/%s' % (random.randint(1,99999)), 'nargs' : '?' },
          { 'name' : 'rpython', 'help' : 'Remote python interpreter path', 'default' : 'python', 'nargs' : '?' },
        ])

        self.register_vectors(
            [
            ModuleExec(
              module = 'file_upload',
              arguments = [os.path.join(self.folder, 'linuxprivchecker.py'), '${rpath}'],
              name = 'upload_script'
            ),
            ShellCmd(
                payload = """${rpython} '${rpath}'""",
                name = 'exec_script'
            )
            ]
        )

    def run(self):

        if self.vectors.get_result('upload_script', format_args=self.args):
            return self.vectors.get_result('exec_script', format_args=self.args)
