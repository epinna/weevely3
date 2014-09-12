from mako.template import Template
from core.weexceptions import DevException, ModuleError
from core import modules
from core import utilities
from core import messages
import shlex

class ModuleCmd:

    def __init__(self, module, options, name = '', target = 0, postprocess = lambda x: x):

        self.name = name if name else utilities.randstr()

        if isinstance(options, list):
            self.options = options
        else:
            raise DevException(messages.vectors.wrong_payload_type)

        if not isinstance(target, int) or not target < 3:
            raise DevException(messages.vectors.wrong_target_type)

        if not callable(postprocess):
            raise DevException(messages.vectors.wrong_postprocessing_type)

        self.module = module
        self.target = target
        self.postprocess = postprocess

    def format(self, values):
        return [ Template(option).render(**values) for option in self.options ]

    def run(self, values = {}):

        try:
            formatted = self.format(values)
        except TypeError as e:
            import traceback
            traceback.print_exc()
            raise DevException(messages.vectors.wrong_arguments_type)

        return self.postprocess(
          modules.loaded[self.module].run_argv(formatted)
        )

class ShellCmd(ModuleCmd):

    def __init__(self, payload, name = None, target = 0, postprocess = lambda x: x):

        if not isinstance(payload, basestring):
            raise DevException(messages.vectors.wrong_payload_type)

        ModuleCmd.__init__(
            self,
            module = 'shell_sh',
            options = [ payload ],
            name = name,
            target = target,
            postprocess = postprocess
        )


class PhpCmd(ModuleCmd):

    def __init__(self, payload, name = None, target = 0, postprocess = lambda x: x):

        if not isinstance(payload, basestring):
            raise DevException(messages.vectors.wrong_payload_type)

        ModuleCmd.__init__(
            self,
            module = 'shell_php',
            options = [ payload ],
            name = name,
            target = target,
            postprocess = postprocess
        )
