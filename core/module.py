from core.vectors import Os, Vectors
from core.loggers import log
from core import messages
import shlex
import getopt
import commons


class Module:

    def __init__(self, session, name):
        """ Initialize module data structures. """

        self.name = name
        self.session = session
        self.vectors = Vectors(session, name)

        self._run_vectors = self.vectors.run

        self.__doc__ = self.__doc__.strip()

        # Initialize session db for current session
        if name not in self.session:
            self.session[self.name] = {
                'options': {},
                'results': {},
                'enabled': None}

        self.initialize()

    def run_cmdline(self, line):
        """ Function called from terminal to run module. Accepts command line string. """

        result = self.run_argv(shlex.split(line))

        if result is not None:
            log.info(commons.stringify(result))

        # Data is returned for the testing of _cmdline calls
        return result

    def run_argv(self, argv):
        """ Main function to run module. Parse arguments list with getopt.
        Calls check() and run() of module.
        Set self.last_result and return a stringified result.
        """
        
        try:
            line_args_optional, line_args_mandatory = getopt.getopt(
                argv, '', [
                    '%s=' %
                    a for a in self.args_optional.keys()])
        except getopt.GetoptError as e:
            log.info('%s\n%s' % (e, self.__doc__))
            return

        if len(line_args_mandatory) != len(self.args_mandatory):
            log.info(
                '%s\n%s' %
                (messages.generic.error_missing_arguments_s %
                 (' '.join(
                     self.args_mandatory)),
                    self.__doc__))
            return

        # Merge options with line arguments
        args = self.session[self.name]['options'].copy()
        args.update(
                dict(
                    (key.strip('-'), value) for
                    (key, value) in line_args_optional)
                )
                    
        args.update(dict((key, line_args_mandatory.pop(0))
                         for key in self.args_mandatory))

        # If module is not already enable, launch check()
        if not self.session[self.name]['enabled']:
            self.session[self.name]['enabled'] = self.check(args)

        if self.session[self.name]['enabled']:
            return self.run(args)

    def check(self, args={}):
        """ Override to implement module check """

        return True

    def _register_infos(self, infos):
        self.infos = infos

    def _register_arguments(self, arguments=[], options={}):
        """ Register additional modules options """

        self.args_mandatory = arguments
        self.args_optional = options

        # Options saved in session has more priority than registered
        # variables

        options.update(self.session[self.name]['options'])
        self.session[self.name]['options'] = self.args_optional

    def _register_vectors(self, vectors):
        """ Add module vectors """

        self.vectors.extend(vectors)

    def _store_result(self, field, value):
        """ Save persistent data """

        self.session[self.name]['results'][field] = value

    def _get_result(self, field, default=None):
        """ Recover saved data """

        self._get_module_result(self.name, field, default)

    def _get_module_result(self, module_name, field, default=None):
        """ Recover another module saved data """

        if module_name is not None:
            return self.session[module_name][
                'results'].get(field, default)
        else:
            return self.session.get(field, default)
