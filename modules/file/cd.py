from core.vectors import Os, Vector
from core.module import Module
from core import messages
import logging, random

class Cd(Module):

    """Change current working directory.
    
    Usage:
      file_cd <folder>
    
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
                         'folder' 
                         ])

        self._register_vectors([
            Vector("chdir", 'shell.php', """chdir("${args['folder']}") && print(getcwd());"""),
        ])
        

    def run(self, args):

        folder = self.terminal.run_shell_php([ self.vectors.get_by_name('chdir').format(args) ])
        
        if folder:
            # Store cwd used by other modules
            self._store_result('cwd', folder)
        else:
            logging.info(messages.module_file_cd.error_folder_s_change_failed % (args['folder']))