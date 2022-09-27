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
            {'name': 'rpath', 'help': 'Remote starting path (default: /)', 'default': '/', 'nargs': '?'},
            {'name': '-only-suid', 'help': 'Find only suid', 'action': 'store_true', 'default': False},
            {'name': '-only-sgid', 'help': 'Find only sgid', 'action': 'store_true', 'default': False},
            {'name': '-uid', 'help': 'Filter by owner (default: -1, do not filter)', 'type': int, 'default': -1},
            {'name': '-maxdepth', 'help': 'Max depth of recursion (default: 3)', 'default': 3},
        ])

    def run(self):
        result = ShellCmd(
            payload="""
                find ${rpath} -type f ${ ("-uid " + str(uid)) if uid > -1 else '' } \\
                \( \\
                  ${ '-perm -04000' if not only_sgid else '' } \\
                  ${ '-o' if not only_suid and not only_sgid else '' } \\
                  ${ '-perm -02000' if not only_suid else '' } \\
                \) \\
                -exec ls -hal {} +
            """,
            arguments=[
                "-stderr_redirection",
                " 2>/dev/null",
            ]).run(self.args)

        if result:
            return result.split('\n')
