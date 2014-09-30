"""
The module `core.module` defines the `Module` class.

The `Module` class has to be inherited to create a new weevely module.

Normally, the following methods have to be overridden:

* `init()`: This defines the basic module initialization. The `init()` method normally calls `register_info()`, `register_vectors()` and `register_arguments()`.
* `check()`: This is called at the first run. Check and set the module status.
* `run()`: This function is called on module run.

"""

from core.vectorslist import VectorsList
from core.weexceptions import DevException
from core.loggers import log
from core import messages
from mako.template import Template
import shlex
import getopt
import utilities

class Status:
    """Represent the module statuses.

    It is stored in the session to keep track of the module status. It is set by `setup()` at the first module run.

    * Status.IDLE: Inactive module. The module has been never been setup or needs a new setup. If a module is run when IDLE, the `setup()` function is automatically called on the first module run.

    * Status.RUN: The module is properly running and can be called.

    * Status.FAIL: The previous setup failed and the module is disabled. Every execution of this module is automatically skipped.
    """

    IDLE = 0
    RUN = 1
    FAIL = 2

class Module:

    def __init__(self, session, name):
        """Module object constructor.

        This call the overridable `init()` method.

        Normally does not need to be overridden.
        """

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
        """Execute the module from command line.

        Get command line string as argument. Called from terminal.

        Normally does not need to be overridden.

        Args:
            line (str): string containing the module arguments.

        Return:
            Object. The result of the module execution.
        """

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
        """Execute the module.

        Get arguments list as argument. The arguments are parsed with getopt,
        and validated. Then calls setup() and run() of module.

        Normally does not need to be overridden.

        Args:
            argv (list of str): The list of arguments.

        Returns:
            Object. The result of the module execution.

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
            self.session[self.name]['status'] = self.setup(args)

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

    def init(self):
        """Module initialization.

        Called at boot.

        Must be overriden to set the basic Module data.

        This normally calls `register_info()`, `register_vectors()` and `register_arguments()`.
        """

        raise DevException(messages.module.error_init_method_required)

    def setup(self, args={}):
        """Module first setup.

        Called at the first module run per session.

        Override this to implement the module setup.

        This should perform the basic check of the module compatibility
        with the remote enviroinment, and return the module Status value.

        If not overridden, always returns Status.RUN.

        Args:
            args (dictionary): Argument passed to the module

        Returns:
            Status value. Must be Status.RUN, Status.FAIL, or Status.IDLE.

        """

        return Status.RUN

    def run(self, args):
        """Module execution.

        Called at every the module executions.

        Override this to implement the module behaviour.

        Args:
            args (dictionary): Argument passed to the module

        Returns:
            Object containing the execution result.

        """

        return

    def help(self):
        """Function called on terminal help command.

        This is binded with the terminal `help_module()` method.

        Normally does not need to be overridden.
        """

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

    def register_info(self, info):
        """Register the module basic information.

        The human-readable description is automatically read from the object
        docstring. With no description set, raise an exception.

        Arbitrary fields can be used.

        Args:
            info (dict): Module information.

        Raises:
            DevException: Missing description

        """

        self.info = info

        # Add description from module __doc__ if missing
        self.info['description'] = (
            self.info.get('description')
            if self.info.get('description')
            else self.__doc__.strip()
        )
        if not self.info['description']:
            raise DevException(messages.module.error_module_missing_description)

    def register_arguments(self, mandatory = [], optional = {}, bind_to_vectors = ''):
        """Register the module arguments.

        Register mandatory and optional arguments.

        An argument can be binded to the vectors names to limit the user choices
        to the vectors names.

        Args:
            mandatory (list of string): List of mandatory arguments.

            optional (dict of strings): Dictionary whith optional arguments as
            keys, and default values as values.

            bind_to_vectors (string): Limit the given argument choices to the
            vectors names stored in `self.vectors`.
        """

        self.args_mandatory = mandatory
        self.args_optional = optional.copy()

        # Arguments in session has more priority than registered variables
        optional.update(self.session[self.name]['stored_args'])
        self.session[self.name]['stored_args'] = optional

        self.bind_to_vectors = bind_to_vectors

    def register_vectors(self, vectors):
        """Register the module vectors.

        The passed vectors are stored in `self.vectors`, a VectorsList object.

        Args:
            vectors (list of vectors objects): List of ShellCmd, PhpCmd, and
            ModuleCmd to use as module vectors.
        """

        self.vectors.extend(vectors)

    def _store_result(self, field, value):
        """Store persistent module result.

        Store data in the module session structure as result.

        Args:
            field (string): The key name to label the result.

            value (obj): The result to store.
        """

        self.session[self.name]['results'][field] = value

    def _get_stored_result(self, field, module = None, default=None):
        """Get stored module result.

        Get the modle result stored in the session structure.

        Args:
            field (string): The key name which contains the result.

            module (string): The module name. If not set, the current
            module is used.

            default: The value to be returned in case key does not exist.
        """

        if module is not None:
            return self.session[module][
                'results'].get(field, default)
        else:
            return self.session.get(field, default)
