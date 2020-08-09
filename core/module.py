"""
The module `core.module` defines the `Module` class.

The `Module` class has to be inherited to create a new weevely module.

Normally, the following methods have to be overridden:

* `init()`: This defines the basic module initialization. The `init()` method normally calls `register_info()`, `register_vectors()` and `register_arguments()`.
* `check()`: This is called at the first run. Check and set the module status.
* `run()`: This function is called on module run.

"""

from core.vectorlist import VectorList
from core.vectors import ModuleExec
from core.weexceptions import DevException, ArgparseError
from core.loggers import log
from core import argparsers
from core import messages
from mako.template import Template
from core import modules
import shlex
import utils
import ast
import os

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

    def __init__(self, session, name, folder):
        """Module object constructor.

        This call the overridable `init()` method.

        Normally does not need to be overridden.
        """

        self.session = session
        self.name = name
        self.folder = folder
        self.vectors = VectorList(session, name)

        # init session db for current session
        if name not in self.session:
            self.session[self.name] = {
                'stored_args': {},
                'results': {},
                'status': Status.IDLE
            }

        # HelpParser is a slightly changed `ArgumentParser`
        self.argparser = argparsers.HelpParser(
            prog = self.name,
            description = self.__doc__
        )

        # Arguments dictionary is initially empty
        self.args = {}

        self.init()

    def run_cmdline(self, line, cmd = ''):
        """Execute the module from command line.

        Get command line string as argument. Called from terminal.

        Normally does not need to be overridden.

        Args:
            line (str): the module arguments.
            cmd (str): the executed command

        Return:
            Object. The result of the module execution.
        """

        # Split the command line
        try:
            command = shlex.split(line)
        except Exception as e:
            import traceback; log.debug(traceback.format_exc())
            log.warn(messages.generic.error_parsing_command_s % str(e))
            return

        # Execute the command, catching Ctrl-c, Ctrl-d, argparse exit,
        # and other exceptions
        try:
            result = self.run_argv(command)

        except (KeyboardInterrupt, EOFError):
            log.info(messages.module.module_s_exec_terminated % self.name)
            return

        except ArgparseError:
            return

        except Exception as e:
            import traceback; log.debug(traceback.format_exc())
            log.warn(messages.module.error_module_exec_error_s % str(e))
            return

        self.print_result(
            result[:-1] if (
                isinstance(result, str) and
                result.endswith('\n')
            ) else result
        )

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
        stored_args = self.session[self.name]['stored_args']
        self.args = {}

        try:
            user_args = self.argparser.parse_args(argv)
        except SystemExit:
            raise ArgparseError()

        # The new arg must win over the stored one if:
        # new arg is not none and the value of the old one 
        # is not just the default value
        
        for newarg_key, newarg_value in user_args.__dict__.items():
                        
            # Pick the default argument of the current arg
            default_value = next((action.default for action in self.argparser._actions if action.dest == newarg_key), None)
            stored_value = stored_args.get(newarg_key)
                        
            if newarg_value != None and newarg_value != default_value:
                self.args[newarg_key] = newarg_value
            elif stored_value != None:
                self.args[newarg_key] = stored_value
            else:
                self.args[newarg_key] = default_value

        # If module status is IDLE, launch setup()
        if self.session[self.name]['status'] == Status.IDLE:
            self.session[self.name]['status'] = self.setup()

            # If setup still not set the status to RUN, return
            if self.session[self.name]['status'] != Status.RUN:
                return

        # If module status is FAIL, return
        if self.session[self.name]['status'] == Status.FAIL:
            log.debug(messages.module.module_s_inactive % self.name)
            return

        # Setup() could has been stored additional args, so all the updated
        # stored arguments are applied to args
        stored_args = self.session[self.name]['stored_args']
        for stored_arg_key, stored_arg_value in stored_args.items():
            if stored_arg_key != None and stored_arg_value != self.args.get(stored_arg_key):
                self.args[stored_arg_key] = stored_arg_value


        return self.run()

    def run_alias(self, args, cmd):
        """Execute the module to replace a missing terminal command.

        This runs the module if the direct shell command can't
        be run due to the shell_sh failing.

        It is called when some alias defined in `Module.alias` list
        is executed from the command line.

        Normally does not need to be overridden.

        Args:
            args (str): string containing the module arguments.

        Return:
            Object. The result of the module execution.

        """

        if self.session['default_shell'] != 'shell_sh':
            log.debug(messages.module.running_the_alias_s % self.name)
            return self.run_cmdline(args)
        else:
            modules.loaded['shell_sh'].run_cmdline(
                '%s -- %s' % (cmd, args)
            )

    def init(self):
        """Module initialization.

        Called at boot.

        Must be overriden to set the basic Module data.

        This normally calls `register_info()`, `register_vectors()` and `register_arguments()`.
        """

        raise DevException(messages.module.error_init_method_required)

    def setup(self):
        """Module first setup.

        Called at the first module run per session.

        Override this to implement the module setup.

        This should perform the basic check of the module compatibility
        with the remote enviroinment, and return the module Status value.

        Current execution arguments are in self.args.

        If not overridden, always returns Status.RUN.

        Returns:
            Status value. Must be Status.RUN, Status.FAIL, or Status.IDLE.

        """

        return Status.RUN

    def run(self):
        """Module execution.

        Called at every module executions.

        Override this to implement the module behaviour.

        Current execution arguments are in self.args.

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

        self.info['description'] = (
            info.get('description')
            if info.get('description')
            else self.__doc__.strip()
        )

        self.argparser.description = self.info.get('description')

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

        The passed vectors are stored in `self.vectors`, a VectorList object.

        Args:
            vectors (list of vectors objects): List of ShellCmd, PhpCode, and
            ModuleExec to use as module vectors.
        """

        self.vectors.extend(vectors)

    def print_result(self, result, header=False):
        """Format and print execution result.

        Called at every executions from command line.

        Override this to implement a different result print format.

        Args:
            result (Object): The result to format and print.
            :param result:
            :param header:

        """

        if result not in (None, ''):
            log.info(utils.prettify.tablify(result, header=header))


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
