from core.vectors import Vectors
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

        Receives arguments as list, parse with getopt, and validate
        them. Then calls setup() and run() of module.

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

        # Check if argument passed to vector_argument matches with
        # some vector
        vect_arg_value = args.get(self.vector_argument)
        if vect_arg_value and vect_arg_value not in self.vectors.get_names():
            log.warn(messages.module.argument_s_must_be_a_vector % self.vector_argument)
            return

        # If module is not already enable, launch setup()
        if not self.session[self.name]['enabled']:
            self.session[self.name]['enabled'] = self.setup(args)

        # Merge again stored arguments with current args, cause setup() method could
        # store additional args.
        # TODO: This still need some fix (what if I want to store ''?)
        args.update(
            dict(
                (key, value) for key, value in self.session[self.name]['stored_args'].items()
                    if value != ''
                )
        )

        if self.session[self.name]['enabled']:
            return self.run(args)

    def setup(self, args={}):
        """ Override to implement module setup """

        return True

    def _register_infos(self, infos):
        self.infos = infos

    def _register_arguments(self, arguments = [], options = {}, vector_argument = ''):
        """ Register additional modules options """

        self.args_mandatory = arguments
        self.args_optional = options

        # Arguments in session has more priority than registered variables

        options.update(self.session[self.name]['stored_args'])
        self.session[self.name]['stored_args'] = self.args_optional

        self.vector_argument = vector_argument

    def _register_vectors(self, vectors):
        """ Add module vectors """

        self.vectors.extend(vectors)

    def _store_result(self, field, value):
        """ Save persistent data """

        self.session[self.name]['results'][field] = value

    def _get_stored_result(self, field, module = None, default=None):
        """ Recover saved data """

        if module is not None:
            return self.session[module][
                'results'].get(field, default)
        else:
            return self.session.get(field, default)

    def _store_arg(self, field, value):
        """ Stored arguments """

        self.session[self.name]['stored_args'][field] = value
