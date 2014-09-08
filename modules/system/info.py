from core.vector import Os, Vector
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
                'info': '' # Comma separated information to request
            },
            vector_argument = 'info')

        self._register_vectors(
            [
            Vector("print(@$_SERVER['DOCUMENT_ROOT']);", 'document_root'),
            Vector("$u=@posix_getpwuid(@posix_geteuid());if($u){$u=$u['name'];} else{$u=getenv('username');} print($u);", 'whoami'),
            Vector("print(@gethostname());", 'hostname'),
            Vector("@print(getcwd());", 'cwd'),
            Vector("$v=@ini_get('open_basedir'); if($v) print($v);", 'open_basedir'),
            Vector("(@ini_get('safe_mode') && print(1)) || print(0);", 'safe_mode'),
            Vector("print(@$_SERVER['SCRIPT_NAME']);", 'script'),
            Vector("print(@php_uname());", 'uname'),
            Vector("print(@php_uname('s'));", 'os'),
            Vector("print(@$_SERVER['REMOTE_ADDR']);", 'client_ip'),
            Vector('print(@ini_get("max_execution_time"));', 'max_execution_time'),
            Vector('print(@$_SERVER["PHP_SELF"]);', 'php_self'),
            Vector('@print(DIRECTORY_SEPARATOR);', 'dir_sep'),
            Vector("$v=''; if(function_exists( 'phpversion' )) { $v=phpversion(); } elseif(defined('PHP_VERSION')) { $v=PHP_VERSION; } elseif(defined('PHP_VERSION_ID')) { $v=PHP_VERSION_ID; } print($v);", 'php_version')
            ]
        )

    def run(self, args):

        return self._run_vectors(
                     names = args['info'].split(','),
                     names_to_store = ['whoami', 'hostname', 'dir_sep', 'os'])

