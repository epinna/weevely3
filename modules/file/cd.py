from core.vectors import Os, Vector
from core.module import Module
from core import messages
import logging, random

class Cd(Module):

    """Change current working directory.
    
    Usage:
      file_cd <dir>
    
    """
    
    def initialize(self):
        
        self._register_infos(
                             {
                             'name' : 'Change directory',
                             'description' : __doc__,
                             'author' : [ 
                                         'Emilio Pinna' 
                                         ],
                              'license' : 'GPLv3'
                              }
                             )
        
        self._register_arguments(
            # Declare mandatory arguments
            arguments = [ 
                         'dir' 
                         ])

        self._register_vectors([
            Vector("chdir", 'shell_php', """@chdir("${args['dir']}") && print(getcwd());"""),
        ])
        

    def run(self, args):

        dir = self.terminal.run_shell_php([ self.vectors.get_by_name('chdir').format(args=args) ])
        
        if dir:
            # Store cwd used by other modules
            self._store_result('cwd', dir)
        else:
            logging.info(messages.module_file_cd.error_folder_s_change_failed % (args['dir']))