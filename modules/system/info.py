from core.vectors import PhpCode
from core.module import Module
from core import messages
from core.loggers import log
from core import modules
import random


class Info(Module):

    """Collect system information."""

    aliases = [
        'whoami',
        'hostname',
        'pwd',
        'uname'
    ]

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
            PhpCode("print(@$_SERVER['DOCUMENT_ROOT']);", 'document_root'),
            PhpCode("""
                if(is_callable('posix_getpwuid')&&is_callable('posix_geteuid')) {
                    $u=@posix_getpwuid(@posix_geteuid());
                    if($u){
                        $u=$u['name'];
                    } else {
                        $u=getenv('username');
                    }
                    print($u);
                }
            """, 'whoami'),
            PhpCode("print(@gethostname());", 'hostname'),
            PhpCode("@print(getcwd());", 'pwd'),
            PhpCode("$v=@ini_get('open_basedir'); if($v) print($v);", 'open_basedir'),
            PhpCode("(@ini_get('safe_mode') && print(1)) || print(0);", 'safe_mode',
             postprocess = lambda x: True if x=='1' else False
            ),
            PhpCode("print(@$_SERVER['SCRIPT_NAME']);", 'script'),
            PhpCode("print(dirname(__FILE__));", 'script_folder'),
            PhpCode("print(@php_uname());", 'uname'),
            PhpCode("print(@php_uname('s'));", 'os'),
            PhpCode("print(@$_SERVER['REMOTE_ADDR']);", 'client_ip'),
            PhpCode('print(@ini_get("max_execution_time"));', 'max_execution_time',
             postprocess = lambda x: int(x) if x and x.isdigit() else False
            ),
            PhpCode('print(@$_SERVER["PHP_SELF"]);', 'php_self'),
            PhpCode('@print(DIRECTORY_SEPARATOR);', 'dir_sep'),
            PhpCode("""
                $v='';
                if(function_exists('phpversion')) {
                    $v=phpversion();
                } elseif(defined('PHP_VERSION')) {
                    $v=PHP_VERSION;
                } elseif(defined('PHP_VERSION_ID')) {
                    $v=PHP_VERSION_ID;
                }
                print($v);""", 'php_version')
            ]
        )

        self.register_arguments([
          { 'name' : '-info',
            'help' : 'Select information',
            'choices' : self.vectors.get_names(),
            'nargs' : '+' }
        ])

    def run(self):

        result = self.vectors.get_results(
            names = self.args.get('info', []),
            results_to_store = (
                            'whoami',
                            'hostname',
                            'dir_sep',
                            'os',
                            'script_folder'
            )
        )

        # Returns a string when a single information is requested,
        # else returns a dictionary containing all the results.
        info = self.args.get('info')
        if info and len(info) == 1:
            return result[info[0]]
        else:
            return result


    def run_alias(self, args, cmd):

        if self.session['default_shell'] != 'shell_sh':
            log.debug(messages.module.running_the_alias_s % self.name)
            return self.run_cmdline('-info %s' % cmd)
        else:
            modules.loaded['shell_sh'].run_cmdline(
                '%s -- %s' % (cmd, args)
            )
