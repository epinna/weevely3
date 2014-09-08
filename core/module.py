from core.vectors import Os, Vectors
from core.weexceptions import DevException
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

        self._run_vector = self.vectors.run_one
        self._run_vectors = self.vectors.run_all
        self._run_vectors_until = self.vectors.run_until

        self.__doc__ = self.__doc__.strip()

        # Initialize session db for current session
        if name not in self.session:
            self.session[self.name] = {
                'stored_args': {},
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
        """ Main function to run module.

        Receives arguments as list, and parse them with getopt. Then
        calls check() and run() of module.

        Args:
            argv: The list of arguments to execute the module with.

        Returns:
            An object as result of the module run.

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

        # Merge stored arguments with line arguments
        args = self.session[self.name]['stored_args'].copy()
        args.update(
                dict(
                    (key.strip('-'), value) for
                    (key, value) in line_args_optional)
                )
                    
        args.update(dict((key, line_args_mandatory.pop(0))
                         for key in self.args_mandatory))

        # Dirty filter the module default vectors by operating system, if
        # available.
        # TODO: this check should be done in vector.run
        #~ os_current = self.session['system_info']['results'].get('os')
        #~ if os_current:
            #~ target = Os.WIN if os_current.lower().startswith('win') else Os.NIX
            #~ for vector in self.vectors:
                #~ if not vector.target in (target, Os.ANY):
                    #~ del vector
            
        # If module is not already enable, launch check()
        # TODO: change check method name with some more intuitive, e.g. .setup()
        if not self.session[self.name]['enabled']:
            self.session[self.name]['enabled'] = self.check(args)

        # Merge again stored arguments with current args, the check() method can
        # has stored additional parameters in session. This still need some fix
        # (what if I want to store ''?)
        args.update(
            dict(
                (key, value) for key, value in self.session[self.name]['stored_args'].items()
                    if value != ''
                )
        )

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

        options.update(self.session[self.name]['stored_args'])
        self.session[self.name]['stored_args'] = self.args_optional

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

    def _store_arg(self, field, value):
        """ Stored arguments """
        
        self.session[self.name]['stored_args'][field] = value
