from core.vectors import ShellCmd
from core.module import Module

class Suidsgid(Module):

    """Find files with SUID or SGID flags."""

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
          { 'name' : 'rpath', 'help' : 'Remote starting path', 'default' : '/' },
          { 'name' : '-only-suid', 'help' : 'Find only suid', 'action' : 'store_true', 'default' : False },
          { 'name' : '-only-sgid', 'help' : 'Find only sgid', 'action' : 'store_true', 'default' : False },
        ])

    def run(self):

        result = ShellCmd(
          payload = """find ${rpath} -type f ${ '-perm -04000' if not only_sgid else '' } ${ '-o' if not only_suid and not only_sgid else '' } ${ '-perm -02000' if not only_suid else '' }""",
          arguments = [
            "-stderr_redirection",
            " 2>/dev/null",
          ]).run(self.args)

        if result:
            return result.split('\n')
