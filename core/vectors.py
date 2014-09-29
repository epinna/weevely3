"""
The module `core.vectors` defines the following vectors classes.

* `PhpCmd` vector contains PHP code, sent through the `shell_php` module.
* `ShellCmd` vector contains a shell command, sent through the `shell_sh` module.
* `ModuleCmd` vector execute the given module with the given arguments.

ShellCmd and PhpCmd inherit from ModuleCmd class.

"""

from mako.template import Template
from core.weexceptions import DevException, ModuleError
from core import modules
from core import utilities
from core import messages

class ModuleCmd:
    """Vector containing module arguments to run via the given module."""

    def __init__(self, module, arguments, name = '', target = 0, postprocess = None):

        self.name = name if name else utilities.randstr()

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

    def format(self, values):
        return [ Template(option).render(**values) for option in self.arguments ]

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
            import traceback
            traceback.print_exc()
            raise DevException(messages.vectors.wrong_arguments_type)

        result = modules.loaded[self.module].run_argv(formatted)

        if self.postprocess:
            result = self.postprocess(result)

        return result

class ShellCmd(ModuleCmd):

    """Vector containing shell command to run via `shell_sh` module. Inherit `ModuleCmd`"""

    def __init__(self, payload, name = None, target = 0, postprocess = None):

        if not isinstance(payload, basestring):
            raise DevException(messages.vectors.wrong_payload_type)

        ModuleCmd.__init__(
            self,
            module = 'shell_sh',
            arguments = [ payload ],
            name = name,
            target = target,
            postprocess = postprocess
        )


class PhpCmd(ModuleCmd):

    """Vector containing PHP code to run via `shell_php` module. Inherit `ModuleCmd`"""

    def __init__(self, payload, name = None, target = 0, postprocess = None):

        if not isinstance(payload, basestring):
            raise DevException(messages.vectors.wrong_payload_type)

        ModuleCmd.__init__(
            self,
            module = 'shell_php',
            arguments = [ payload ],
            name = name,
            target = target,
            postprocess = postprocess
        )
