from core.vectors import Os, Vectors
from core import messages
import logging
import shlex
import getopt
import commons

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
        """ Main function to run module. Parse arguments list with getopt. Calls check() and run() of module. """
        
        try:
            line_args_optional, line_args_mandatory = getopt.getopt(argv, '', [ '%s=' % a for a in self.args_optional.keys() ])
        except getopt.GetoptError as e:
            logging.info('%s\n%s' % (e, self.__doc__))
            return
        
        if len(line_args_mandatory) != len(self.args_mandatory):
            logging.info('%s\n%s' % (messages.generic.error_missing_arguments_s % (' '.join(self.args_mandatory)), self.__doc__))
            return
            
        # Merge options with line arguments    
        args = self.terminal.session[self.name]['options'].copy()
        args.update(dict((key.strip('-'), value) for (key, value) in line_args_optional))
        args.update(dict((key, line_args_mandatory.pop(0)) for key in self.args_mandatory))

        # If module is not already enable, launch check()
        if not self.terminal.session[self.name]['enabled']:
            enabled = self.check(args)
            self.terminal.session[self.name]['enabled'] = enabled
        
        if self.terminal.session[self.name]['enabled']:
            return commons.stringify(self.run(args))
    
    def check(self, args = {}):
        """ Override to implement module check """
        
        return True
    
    def _register_infos(self, infos):
        self.infos = infos
        
    def _register_arguments(self, arguments = [], options = {}):
        """ Register additional modules options """ 
        
        self.args_mandatory = arguments
        self.args_optional = options
        
        # Options saved in session has more priority than registered
        # variables 
        
        options.update(self.terminal.session[self.name]['options'])
        self.terminal.session[self.name]['options'] = self.args_optional
        

    def _register_vectors(self, vectors):
        """ Add module vectors """ 
        
        self.vectors.extend(vectors)
    
    
    def _store_result(self, field, value):
        """ Save persistent data """
        
        self.terminal.session[self.name]['results'][field] = value
        
    def _get_result(self, field):
        """ Recover saved data """
        
        self._get_module_result(self.name, field)
    
    def _get_module_result(self, module_name, field):
        """ Recover another module saved data """
        
        return self.terminal.session[module_name]['results'].get(field)
    
    def _register_storable_results(self, storable_results):
        """ Register storable_results that should be saved. 
        Only missing keys are modified. 
        Storage procedure should be handled manually in run().
        """
        
        self.storable_results = storable_results
        
        for key, value in storable_results.items():
            if self.terminal.session[self.name]['results'].get('key') == None:
                self.terminal.session[self.name]['results'][key] = value
            
   