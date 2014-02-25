from core.weexceptions import FatalException
from core import messages
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
        self.prompt = 'weevely> '
        self._load_modules()
        
        logging.debug(pprint.pformat(dict(session)))
        
        cmd.Cmd.__init__(self)
    
    
    def emptyline(self):
        """ Disable repetition of last command. """
        
        pass
    
    def precmd(self, line):
        """ Before to execute a line commands. Confirm shell availability and get basic system infos. """
        
        # Probe shell_sh if is never tried
        if not self.session['shell_sh']['enabled']:
            self.session['shell_sh']['enabled'] = self.check_shell_sh()
            self.run_default_shell = self.run_shell_sh
     
        # Probe shell_php if shell_sh failed
        if not self.session['shell_sh']['enabled']:
            self.session['shell_php']['enabled'] = self.check_shell_php()
            self.run_default_shell = self.run_shell_php
            
        # Check results
        if not self.session['shell_sh']['enabled'] and not self.session['shell_php']['enabled']:
            raise FatalException(messages.terminal.backdoor_unavailable)
        
        # Get current working directory if not set
        if not self.session['file_cd']['results'].get('cwd'):
            self.run_file_cd(["."])

        # Get hostname and whoami if not set
        if not self.session['system_info']['results'].get('hostname'):
            self.run_system_info(["--info=hostname"])
            
        if not self.session['system_info']['results'].get('whoami'):
            self.run_system_info(["--info=whoami"])
            
        return line

    def postcmd(self, stop, line):
        
        # Build next prompt, last command could have changed the cwd
        self.prompt = '{user}@{host}:{path} {prompt} '.format(
                     user=self.session['system_info']['results'].get('whoami', ''), 
                     host=self.session['system_info']['results'].get('hostname', ''), 
                     path=self.session['file_cd']['results'].get('cwd', '.'), 
                     prompt = 'PHP>' if (self.run_default_shell == self.run_shell_php) else '$' )
 
        return stop

    def default(self, line):
        """ Direct command line send. """

        if line:

            result = self.run_default_shell([ line ])
             
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
            
            # Set module.do_terminal_module() function as terminal self.do_modulegroup_modulename()
            class_do = getattr(module_class, 'do_module') 
            setattr(Terminal, 'do_%s_%s' % (module_group, module_name), class_do)

            # Set module.run_terminal_module() function as terminal self.run_modulegroup_modulename()
            class_run = getattr(module_class, 'run_module') 
            setattr(Terminal, 'run_%s_%s' % (module_group, module_name), class_run)
                        
            # Set module.check() function as terminal self.check_modulegroup_modulename()
            class_check = getattr(module_class, 'check') 
            setattr(Terminal, 'check_%s_%s' % (module_group, module_name), class_check)    