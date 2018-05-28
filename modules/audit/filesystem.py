from core.vectors import PhpCode, ShellCmd, ModuleExec, Os
from core.module import Module
from core.loggers import log
from core import modules
import utils

class Filesystem(Module):

    """Audit the file system for weak permissions."""

    def init(self):

        self.register_info(
            {
                'author': [
                    'Emilio Pinna'
                ],
                'license': 'GPLv3'
            }
        )

        self.check_functions = [ f for f in dir(self) if f.startswith('check_') ]

        self.register_arguments([
          { 'name' : 'check', 'choices' : self.check_functions, 'nargs' : '?' }
        ])


    def check_writable_binaries(self):
        """Search writable files in binary folders"""

        results = []

        for path in [ '/bin/', '/usr/bin/', '/usr/sbin',
                      '/sbin', '/usr/local/bin', '/usr/local/sbin',
                      '/lib/', '/usr/lib/',
                      '/usr/local/lib' ]:

            result = ModuleExec("file_find",
                                [ '-writable', path ]).run()

            if result and any(r for r in result if r):
                results += result


        return results

    def check_writable_etc(self):
        """Search writable files in etc folder"""

        result = ModuleExec("file_find",
                            [ '-writable', '/etc/' ]
                ).run()

        if result and any(r for r in result if r):
            return result

    def check_writable_root(self):
        """Search writable files in / folder"""

        result = ModuleExec("file_find",
                            [   '-no-recursion',
                                '-writable',
                                '/' ]
                ).run()

        if result and any(r for r in result if r):
            return result

    def check_home_writable(self):
        """Search writable files in /home/ folder"""

        result = ModuleExec("file_find",
                            [   '-no-recursion',
                                '-writable',
                                '/home/' ]
                ).run()

        if result and any(r for r in result if r):
            return result

    def check_spool_crons(self):
        """Search writable files in /var/spool/cron/ folder"""

        result = ModuleExec("file_find",
                            [ '-writable',
                            '/var/spool/cron/' ]
                ).run()

        if result and any(r for r in result if r):
            return result

    def check_home_executable(self):
        """Search executable files in /home/ folder"""

        result = ModuleExec("file_find",
                            [   '-no-recursion',
                                '-executable',
                                '/home/' ]
                ).run()

        if result and any(r for r in result if r):
            return result

    def check_readable_etc(self):
        """Search certain readable files in etc folder"""

        readable_files = ModuleExec("file_find",
                            [ '-readable', '/etc/' ]
                ).run()

        files_paths = [ 'shadow', 'ap-secrets',
                      'mysql/debian.cnf', 'sa_key$', 'keys',
                      '\.gpg', 'sudoers' ]

        return [ f for f in readable_files
                if f and any(p for p in files_paths if p and p in f)]


    def check_readable_logs(self):
        """Search certain readable log files"""

        readable_files = ModuleExec("file_find",
                            [ '-readable', '/var/log/' ]
                ).run()

        files_paths = [ 'lastlog', 'dpkg', 'Xorg', 'wtmp',
                        'pm', 'alternatives', 'udev', 'boot' ]

        return [
                f for f in readable_files
                if f
                and not f.endswith('gz')
                and not f.endswith('old')
                and any(p for p in files_paths if p and p in f)]

    def run(self):

        results = {}

        for func_name in [
                            # Execute every function starting with check_*
                            fn for fn in self.check_functions
                            # if the user does not specify any name
                            if not self.args.get('check')
                            # of if specify the current function name
                            or self.args.get('check') == fn
                        ]:

            function = getattr(self, func_name)
            log.warn(function.__doc__)

            result = function()

            if result:
                log.info('\n'.join(result))
                results.update({ func_name : result })

        return results

    def print_result(self, result):
        pass
