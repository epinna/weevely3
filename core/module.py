"""
The module `core.module` defines the `Module` class.

The `Module` class has to be inherited to create a new weevely module.

Normally, the following methods have to be overridden:

* `init()`: This defines the basic module initialization. The `init()` method normally calls `register_info()`, `register_vectors()` and `register_arguments()`.
* `check()`: This is called at the first run. Check and set the module status.
* `run()`: This function is called on module run.

"""

from core.vectorslist import VectorsList
from core.vectors import ModuleCmd
from core.weexceptions import DevException
from core.loggers import log
from core import helpparse
from core import messages
from mako.template import Template
import shlex
import utilities
import ast

class Status:
    """Represent the module statuses.

    Is stored in session[module][status] and is set by `setup()` call at the first run.

    * Status.IDLE: The module is inactive. This state is set if the module has been never been setup, of if it needs a new setup. If a module is run in this state, the `Module.setup()` function is automatically called.

    * Status.RUN: The module is properly running and can be call.

    * Status.FAIL: The module setup failed. The execution of this module is automatically skipped.
    """

    IDLE = 0
    RUN = 1
    FAIL = 2

class Module:

    aliases = []

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

        # HelpParser is a slightly changed `ArgumentParser`
        self.argparser = helpparse.HelpParser(
            prog = self.name,
            description = self.__doc__
        )

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
            import traceback; log.debug(traceback.format_exc())
            log.warn(messages.generic.error_parsing_command_s % str(e))
            return

        self.print_result(result)

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

        # Merge stored arguments with line arguments
        stored_args = self.session[self.name]['stored_args'].copy()
        args = stored_args.copy()

        try:
            user_args = self.argparser.parse_args(argv)
        except SystemExit:
            return

        args.update(
            dict(
                (key, value) for key, value in user_args.__dict__.items() if value != None
            )
        )

        # If module status is IDLE, launch setup()
        if self.session[self.name]['status'] == Status.IDLE:
            self.session[self.name]['status'] = self.setup(args)

        # If module status is FAIL, return
        if self.session[self.name]['status'] == Status.FAIL:
            log.debug(messages.module.module_s_inactive % self.name)
            return

        # Setup() could has been stored additional args, so all the updated
        # stored arguments are applied to args
        args.update(
            dict(
                (key, value) for key, value in self.session[self.name]['stored_args'].items()
                if value != stored_args.get(key)
                )
        )

        return self.run(args)

    def run_alias(self, line):
        """Execute the module as alias from command line.

        This is invoked if some alias defined in `Module.alias`
        is called from terminal command line.

        Get command line string as argument. Called from terminal.

        Normally does not need to be overridden.

        Args:
            line (str): string containing the module arguments.

        Return:
            Object. The result of the module execution.
        """

        return self.run_cmdline(line)

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

        Called at every module executions.

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

        self.run_argv([ '-h' ])

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

        self.argparser.description =  (
            self.info.get('description')
            if self.info.get('description')
            else self.__doc__.strip()
        )

        if not self.argparser.description:
            raise DevException(messages.module.error_module_missing_description)

    def register_arguments(self, arguments = []):
        """Register the module arguments.

        Register arguments to be added to the argparse parser.

        Args:
            arguments (list of dict): List of dictionaries in the form
            `[{ 'name' : 'arg1', 'opt' : '', .. }, {'name' : 'arg2', 'opt' : '', .. }]`
            to be passed to the `ArgumentParser.add_argument()` method.
        """

        try:
            for arg_opts in arguments:

                # Handle if the argument registration is done before
                # The vector registration. This should at least warn
                if arg_opts.get('choices') == []:
                    log.warn(messages.module.error_choices_s_s_empty % (self.name,
                                                                        arg_name))

                self.argparser.add_argument(
                    arg_opts['name'],
                    **dict((k, v) for k, v in arg_opts.items() if k != 'name')
                )
        except Exception as e:
            raise DevException(messages.module.error_setting_arguments_s % (e))


    def register_vectors(self, vectors):
        """Register the module vectors.

        The passed vectors are stored in `self.vectors`, a VectorsList object.

        Args:
            vectors (list of vectors objects): List of ShellCmd, PhpCmd, and
            ModuleCmd to use as module vectors.
        """

        self.vectors.extend(vectors)

    def print_result(self, result):
        """Format and print execution result.

        Called at every executions from command line.

        Override this to implement a different result print format.

        Args:
            result (Object): The result to format and print.

        """

        if result not in (None, ''):
            log.info(utilities.stringify(result))


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
