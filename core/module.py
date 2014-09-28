from core.vectorslist import VectorsList
from core.weexceptions import DevException
from core.loggers import log
from core import messages
from mako.template import Template
import shlex
import getopt
import utilities

class Status:
    IDLE = 0
    RUN = 1
    FAIL = 2

class Module:

    def __init__(self, session, name):
        """ init module data structures. """

        self.name = name
        self.session = session
        self.vectors = VectorsList(session, name)

        # init session db for current session
        if name not in self.session:
            self.session[self.name] = {
                'stored_args': {},
                'results': {},
                'status': Status.IDLE
            }

        self.init()

    def run_cmdline(self, line):
        """ Function called from terminal to run module. Accepts command line string. """

        try:
            result = self.run_argv(shlex.split(line))
        except Exception as e:
            log.warn(messages.generic.error_parsing_command_s % str(e))
            return

        if result not in (None, ''):
            log.info(utilities.stringify(result))

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
            log.info('%s' % (e))
            self.help()
            return

        # If less mandatory arguments are passed, abort
        if len(line_args_mandatory) < len(self.args_mandatory):
            log.info(messages.generic.error_missing_arguments_s %
                    (' '.join(self.args_mandatory))
            )
            self.help()
            return

        # If there are more argument and we expect one, join all the
        # Remaining mandatory arguments
        elif len(line_args_mandatory) > 1 and len(self.args_mandatory) == 1:
            line_args_mandatory = [ ' '.join( line_args_mandatory ) ]

        # Merge stored arguments with line arguments
        stored_args = self.session[self.name]['stored_args'].copy()
        args = stored_args.copy()

        args.update(
                dict(
                    (key.strip('-'), value) for
                    (key, value) in line_args_optional)
                )

        args.update(dict((key, line_args_mandatory.pop(0))
                         for key in self.args_mandatory))

        # Check if argument passed to bind_to_vectors matches with
        # some vector
        vect_arg_value = args.get(self.bind_to_vectors)
        if vect_arg_value and vect_arg_value not in self.vectors.get_names():
            log.warn(messages.module.argument_s_must_be_a_vector % self.bind_to_vectors)
            return

        # If module status is IDLE, launch setup()
        if self.session[self.name]['status'] == Status.IDLE:
            self.session[self.name]['status'] = (
                Status.RUN if self.setup(args)
                else Status.FAIL
            )

        # If module status is FAIL, return
        if self.session[self.name]['status'] == Status.FAIL:
            log.warn(messages.module.module_s_inactive % self.name)
            return

        # Setup() could has been stored additional args, so all the updated
        # stored arguments are applied to args
        args.update(
            dict(
                (key, value) for key, value in self.session[self.name]['stored_args'].items()
                if value != stored_args[key]
                )
        )

        return self.run(args)

    def setup(self, args={}):
        """ Override to implement specific module setup """

        return True

    def help(self):
        """ Function called on terminal help command """

        option_args_help = Template(
            messages.help.details
        ).render(
            module_name = self.name,
            description = self.info['description'],
            mand_arguments = self.args_mandatory,
            opt_arguments = self.args_optional,
            stored_arguments = self.session[self.name]['stored_args'],
            vector_arg = (self.bind_to_vectors, self.vectors.get_names())
        )

        log.info(option_args_help)

    def _register_info(self, info):
        self.info = info

        # Add description from module __doc__ if missing
        self.info['description'] = (
            self.info.get('description')
            if self.info.get('description')
            else self.__doc__.strip()
        )
        if not self.info['description']:
            raise DevException(messages.module.error_module_missing_description)

    def _register_arguments(self, mandatory = [], optional = {}, bind_to_vectors = ''):
        """ Register additional modules options """

        self.args_mandatory = mandatory
        self.args_optional = optional.copy()

        # Arguments in session has more priority than registered variables
        optional.update(self.session[self.name]['stored_args'])
        self.session[self.name]['stored_args'] = optional

        self.bind_to_vectors = bind_to_vectors

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
