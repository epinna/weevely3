from core.vectors import Os, Vectors
from docopt import docopt, formal_usage
import logging
import shlex

class Module:

    def __init__(self, terminal, name):
        """ Initialize module data structures. """
        
        self.name = name
        self.terminal = terminal
        self.vectors = Vectors(terminal, name)

        # Initialize session db for current session
        if name not in self.terminal.session:
            self.terminal.session[self.name] = { 'options' : {}, 'results' : {}, 'enabled' : None}
         
        self.initialize()


    def do_module(self, line):
        """ Function called from terminal to run module. Accepts command line string. """

        logging.info(self.run_module(shlex.split(line)))

    def run_module(self, argv):
        """ Main function to run module. Accepts arguments lists. Calls check() and run() of module. """
        
        try:
            line_args = docopt(self.__doc__, argv=argv)
        except SystemExit:
            logging.info(self.__doc__)
            return
        
        # Merge options with line arguments    
        args = self.terminal.session[self.name]['options'].copy()
        args.update(line_args)

        # If module is not already enable, launch check()
        if not self.terminal.session[self.name]['enabled']:
            enabled = self.check(args)
            self.terminal.session[self.name]['enabled'] = enabled
        
            
        if self.terminal.session[self.name]['enabled']:
            return self.run(args)
    
    def check(self, args):
        """ Override to implement module check """
        
        return True
        
    def _register_options(self, options):
        """ Register additional modules options """ 
        
        # Options saved in session has more priority than registered
        # variables 
        
        options.update(self.terminal.session[self.name]['options'])
        self.terminal.session[self.name]['options'] = options
        

    def _register_vectors(self, vectors):
        """ Add module vectors """ 
        
        self.vectors.extend(vectors)
    
    
    def _session_save(self, field, value):
        """ Save persistent data """
        
        self.terminal.session[self.name]['results'][field] = value
        
    def _session_get(self, field):
        """ Recover saved data """
        
        return self.terminal.session[self.name]['results'].get(field)
    