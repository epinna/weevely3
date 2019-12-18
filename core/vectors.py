"""
The module `core.vectors` defines the following vectors classes.

* `ModuleExec` vector executes a given module with given arguments.
* `PhpCode` vector contains PHP code, executed via `shell_php` module.
* `PhpFile` vector loads PHP code from an external file, and execute it via `shell_php` module.
* `ShellCmd` vector contains a shell command, executed via `shell_sh` module.

"""

from mako.template import Template
from mako.lookup import TemplateLookup
from core.weexceptions import DevException
from core.loggers import log
from core import modules
import utils
from core import messages
import re
import os
import _thread

class Os:
    """Represent the operating system vector compatibility.

    It is passed as vectors `target` argument.

    * `Os.ANY` if the vector is compatible with every operating system

    * `Os.NIX` if the vector is compatible only with Unix/Linux enviroinments

    * `Os.WIN` if the vector is compatible only with Microsoft Windows enviroinments

    """
    ANY = 0
    NIX = 1
    WIN = 2

class ModuleExec:

    """This vector contains commands to execute other modules.

    Args:
        module (str): Module name.

        arguments (list of str): arguments passed as command line splitted string, e.g. `[ '--optional=o', 'mandatory1, .. ]`.

        name (str): This vector name.

        target (Os): The operating system supported by the vector.

        postprocess (func): The function which postprocess the execution result.

        background (bool): Execute in a separate thread on `run()`

    """

    def __init__(self, module, arguments, name = '', target = 0, postprocess = None, background = False):

        self.name = name if name else utils.strings.randstr()

        if isinstance(arguments, list):
            self.arguments = arguments
        else:
            raise DevException(messages.vectors.wrong_payload_type)

        if not isinstance(target, int) or not target < 3:
            raise DevException(messages.vectors.wrong_target_type)

        if not callable(postprocess) and postprocess is not None:
            raise DevException(messages.vectors.wrong_postprocessing_type)

        self.module = module
        self.target = target
        self.postprocess = postprocess
        self.background = background

    def format(self, values):
        """Format the arguments.

        This format the vector payloads using Mako template.

        Args:
            values (dict): The values passed as arguments of Mako
            `template.Template(arg[n]).render(**values)`

        Returns:
            A list of string containing the formatted payloads.

        """

        return [ Template(arg).render(**values) for arg in self.arguments ]

    def run(self, format_args = {}):
        """Run the module with the formatted payload.

        Render the contained payload with mako and pass the result
        as argument to the given module. The result is processed by the
        `self.postprocess` method.

        Args:
            format_arg (dict): The dictionary to format the payload with.

        Return:
            Object. Contains the postprocessed result of the `run_argv`
            module execution.

        """

        try:
            formatted = self.format(format_args)
        except TypeError as e:
            import traceback; log.debug(traceback.format_exc())
            raise DevException(messages.vectors.wrong_arguments_type)

        # The background argument is set at vector init in order
        # to threadify vectors also if called by VectorList methods.
        if self.background:
            _thread.start_new_thread(modules.loaded[self.module].run_argv, (formatted, ))
            result = None
        else:
            result = modules.loaded[self.module].run_argv(formatted)

        if self.postprocess:
            result = self.postprocess(result)

        return result

    def load_result_or_run(self, result_name, format_args = {}):
        """Load a result stored in module session or run the module.

        Return the variable stored or run the `self.run` method.

        Args:
            field (string): The variable name.
            format_arg (dict): The dictionary to format the payload with.

        Return:
            Object. Contains the postprocessed result of the `run_argv`
            module execution.

        """

        result = modules.loaded[self.module].session[self.module]['results'].get(result_name)

        if result: return result
        else: return self.run(format_args)



class PhpCode(ModuleExec):

    """This vector contains PHP code.

    The PHP code is executed via the module `shell_php`. Inherit `ModuleExec`.

    Args:
        payload (str): PHP code to execute.

        name (str): This vector name.

        target (Os): The operating system supported by the vector.

        postprocess (func): The function which postprocess the execution result.

        arguments (list of str): Additional arguments for `shell_php`

        background (bool): Execute in a separate thread on `run()`
    """

    def __init__(self, payload, name = None, target = 0, postprocess = None, arguments = [], background = False):

        if not isinstance(payload, str):
            raise DevException(messages.vectors.wrong_payload_type)

        ModuleExec.__init__(
            self,
            module = 'shell_php',
            arguments = [ payload ] + arguments,
            name = name,
            target = target,
            postprocess = postprocess,
            background = background
        )

    def format(self, values):
        """Format the payload.

        This format the vector payloads using Mako template.

        Args:
            values (dict): The values passed as arguments of Mako
            `template.Template(arg[n]).render(**values)`

        Returns:
            A list of string containing the formatted payloads.

        """

        return [
                    Template(arg).render(**values)
                    for arg in self.arguments
                ]

class PhpFile(PhpCode):

    """This vector contains PHP code imported from a template.

    The PHP code in the given template is executed via the module `shell_php`.
    Inherit `PhpCode`.

    Args:
        payload_path (str): Path of the template to execute, usually placed in self.folder.

        name (str): This vector name.

        target (Os): The operating system supported by the vector.

        postprocess (func): The function which postprocess the execution result.

        arguments (list of str): Additional arguments for `shell_php`

        background (bool): Execute in a separate thread on `run()`
    """

    def __init__(self, payload_path, name = None, target = 0, postprocess = None, arguments = [], background = False):

        if not isinstance(payload_path, str):
            raise DevException(messages.vectors.wrong_payload_type)

        try:
            with open(payload_path, 'r') as templatefile:
                payload = templatefile.read()
        except Exception as e:
            raise DevException(messages.generic.error_loading_file_s_s % (payload_path, e))

        self.folder, self.name = os.path.split(payload_path)

        ModuleExec.__init__(
            self,
            module = 'shell_php',
            arguments = [ payload ] + arguments,
            name = name,
            target = target,
            postprocess = postprocess,
            background = background
        )

    def format(self, values):
        """Format the payload.

        This format the vector payloads using Mako template.
        Also set a TemplateLookup to the template folder, to allow an easy
        `<% include>` tag usage.

        Args:
            values (dict): The values passed as arguments of Mako
            `template.Template(arg[n]).render(**values)`

        Returns:
            A list of string containing the formatted payloads.

        """

        return [
                 Template(
                        text = arg,
                        lookup = TemplateLookup(directories = [ self.folder ]),
                        ).render(**values)
                 for arg in self.arguments
                ]

class ShellCmd(PhpCode):

    """This vector contains a shell command.

    The shell command is executed via the module `shell_sh`. Inherit `ModuleExec`.

    Args:
        payload (str): Command line to execute.

        name (str): This vector name.

        target (Os): The operating system supported by the vector.

        postprocess (func): The function which postprocess the execution result.

        arguments (list of str): Additional arguments for `shell_php`

        background (bool): Execute in a separate thread on `run()`
    """

    def __init__(self, payload, name = None, target = 0, postprocess = None, arguments = [], background = False):

        if not isinstance(payload, str):
            raise DevException(messages.vectors.wrong_payload_type)

        ModuleExec.__init__(
            self,
            module = 'shell_sh',
            arguments = [ payload ] + arguments,
            name = name,
            target = target,
            postprocess = postprocess,
            background = background
        )
