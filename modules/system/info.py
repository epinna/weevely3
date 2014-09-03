from core.vectors import Os, Vector
from core.module import Module
from core import messages
import random


class Info(Module):

    """Collect system information.

    Usage:
      system_info
      system_info [--info=info]

    """

    def initialize(self):

        self._register_infos(
            {
                'name': 'System information',
                'description': __doc__,
                'author': [
                    'Emilio Pinna'
                ],
                'license': 'GPLv3'
            }
        )

        self._register_arguments(
            options={
                'info': 'all'
            })

        self._register_vectors(
            [
                Vector(
                    'document_root', 'shell_php', "@print($_SERVER['DOCUMENT_ROOT']);"), Vector(
                    'whoami', 'shell_php', "$u=@posix_getpwuid(posix_geteuid()); if($u) { $u = $u['name']; } else { $u=getenv('username'); } print($u);"), Vector(
                    'hostname', 'shell_php', "@print(gethostname());"), Vector(
                        'cwd', 'shell_php', "@print(getcwd());"), Vector(
                            'open_basedir', 'shell_php', "$v=@ini_get('open_basedir'); if($v) print($v);"), Vector(
                                'safe_mode', 'shell_php', "(ini_get('safe_mode') && print(1)) || print(0);"), Vector(
                                    'script', 'shell_php', "@print($_SERVER['SCRIPT_NAME']);"), Vector(
                                        'uname', 'shell_php', "@print(php_uname());"), Vector(
                                            'os', 'shell_php', "@print(PHP_OS);"), Vector(
                                                'client_ip', 'shell_php', "@print($_SERVER['REMOTE_ADDR']);"), Vector(
                                                    'max_execution_time', 'shell_php', '@print(ini_get("max_execution_time"));'), Vector(
                                                        'php_self', 'shell_php', '@print($_SERVER["PHP_SELF"]);'), Vector(
                                                            'dir_sep', 'shell_php', '@print(DIRECTORY_SEPARATOR);'), Vector(
                                                                'php_version', 'shell_php', "$v=''; if(function_exists( 'phpversion' )) { $v=phpversion(); } elseif(defined('PHP_VERSION')) { $v=PHP_VERSION; } elseif(defined('PHP_VERSION_ID')) { $v=PHP_VERSION_ID; } print($v);"), ])

    def run(self, args):

        results = {}

        for vector in self.vectors:
            if args['info'] in ('all', vector.name):
                results[vector.name] = self.terminal.run_shell_php(
                    [vector.format()])

                # Store "static" results used by other modules
                if vector.name in ('whoami', 'hostname', 'dir_sep'):
                    self._store_result(vector.name, results[vector.name])

        return results
