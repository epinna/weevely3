from core.vectors import Os, Vector
from core.module import Module
from core import messages
import logging, random

class Info(Module):

    """Collect system information.
    
    Usage:
      system_info
      system_info [--info=info]
    
    """
    
    def initialize(self):
        
        self._register_infos(
                             {
                             'name' : 'System information',
                             'description' : __doc__,
                             'author' : [ 
                                         'Emilio Pinna' 
                                         ],
                              'license' : 'GPLv3'
                              }
                             )
        
        self._register_arguments(
            options = {
                       'info' : 'all'
        })

        self._register_vectors([
            Vector('document_root', 'shell.php', "@print($_SERVER['DOCUMENT_ROOT']);"),
            Vector('whoami', 'shell.php', "$u=@posix_getpwuid(posix_geteuid()); if($u) { $u = $u['name']; } else { $u=getenv('username'); } print($u);"),
            Vector('hostname', 'shell.php', "@print(gethostname());"),
            Vector('cwd', 'shell.php', "@print(getcwd());"),
            Vector('open_basedir', 'shell.php', "$v=@ini_get('open_basedir'); if($v) print($v);"),
            Vector('safe_mode', 'shell.php', "(ini_get('safe_mode') && print(1)) || print(0);"),
            Vector('script', 'shell.php', "@print($_SERVER['SCRIPT_NAME']);"),
            Vector('uname', 'shell.php', "@print(php_uname());"),
            Vector('os', 'shell.php', "@print(PHP_OS);"),
            Vector('client_ip', 'shell.php', "@print($_SERVER['REMOTE_ADDR']);"),
            Vector('max_execution_time', 'shell.php', '@print(ini_get("max_execution_time"));'),
            Vector('php_self', 'shell.php', '@print($_SERVER["PHP_SELF"]);'),
            Vector('dir_sep' , 'shell.php',  '@print(DIRECTORY_SEPARATOR);'),
            Vector('php_version' , 'shell.php',  "$v=''; if(function_exists( 'phpversion' )) { $v=phpversion(); } elseif(defined('PHP_VERSION')) { $v=PHP_VERSION; } elseif(defined('PHP_VERSION_ID')) { $v=PHP_VERSION_ID; } print($v);"),
        ])


    def run(self, args):
        
        results = {}
        
        for vector in self.vectors:
            if args['info'] in ('all', vector.name):
                results[vector.name] = self.terminal.run_shell_php([ vector.format() ])
                
                # Store "static" results used by other modules
                if vector.name in ('whoami', 'hostname', 'dir_sep'):
                    self._store_result(vector.name, results[vector.name])
                
        return results

        