import readline
import cmd
import glob
import os
import logging
import shlex
import pprint

class Terminal(cmd.Cmd):
    """ Weevely terminal. """
        
    def __init__(self, session):
        
        self.session = session
        self._load_modules()
        
        logging.debug(pprint.pformat(dict(session)))
        
        cmd.Cmd.__init__(self)
    
    
    def emptyline(self):
        """ Disable repetition of last command. """
        
        pass
    
    def default(self, line):
        """ Direct command line send. """
        
        # Probe shell_sh if is enabled or never tried
        if self.session['shell_sh']['enabled'] in (True, None):
            result = self.run_shell_sh([ line ])
     
        # Probe shell_php if shell_sh failed
        if self.session['shell_sh']['enabled'] == False:
            result = self.run_shell_php([ line ])
                 
        if result:
            logging.info(result)
        

    def _load_modules(self):
        """ Load all modules assigning corresponding do_* functions. """
        
        modules_paths = glob.glob('modules/*/[a-z]*py')
        
        for module_path in modules_paths:
            
            module_group, module_filename = module_path.split(os.sep)[-2:]
            module_name = os.path.splitext(module_filename)[0]
            classname = module_name.capitalize()
            
            # Import module
            module = __import__('modules.%s.%s' % (module_group, module_name), fromlist = ["*"])
            # Initialize class, passing current terminal instance and module name
            module_class = getattr(module, classname)(self, '%s_%s' % (module_group, module_name))
            
            # Set module.run_terminal_module() function as terminal self.do_modulegroup_modulename()
            class_do = getattr(module_class, 'do_module') 
            setattr(Terminal, 'do_%s_%s' % (module_group, module_name), class_do)

            # Set module.run_terminal_module() function as terminal self.do_modulegroup_modulename()
            class_run = getattr(module_class, 'run_module') 
            setattr(Terminal, 'run_%s_%s' % (module_group, module_name), class_run)
                        
    