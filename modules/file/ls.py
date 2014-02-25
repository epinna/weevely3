from core.vectors import Os, Vector
from core.module import Module
from core import messages
import logging, random

class Ls(Module):

    """List directory content (replacement)
    
    Usage:
      file_ls [--dir=./folder]
    
    """
    
    def initialize(self):
        
        self._register_infos(
                             {
                             'name' : 'List files',
                             'description' : __doc__,
                             'author' : [ 
                                         'Emilio Pinna' 
                                         ],
                              'license' : 'GPLv3'
                              }
                             )
        
        self._register_arguments(
            options = { 
                         'dir' : '.' 
                         })

        self._register_vectors([
            Vector("ls", 'shell_php', """$p="${args['dir']}";if(@is_dir($p)){$d=@opendir($p);$a=array();if($d){while(($f=@readdir($d))){$a[]=$f;};sort($a);print(join('\n', $a));}}"""),
        ])
        

    def run(self, args):

        return self.terminal.run_shell_php([ self.vectors.get_by_name('ls').format(args=args) ])
    