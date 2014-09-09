from mako.template import Template
from core.weexceptions import DevException, ModuleError
from core import modules
from core import commons
from core import messages

class Os:
    ANY = 0
    NIX = 1
    WIN = 2


class Vector:

    def __init__(self, payload, name = None, module = 'shell_php', target = 0, postprocess = lambda x: x):

        self.name = name if name else commons.randstr()

        if isinstance(payload, basestring):
            self.payload = [ payload ]
        elif isinstance(payload, list):
            self.payload = payload
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
        return [ Template(payload).render(**values) for payload in self.payload ]

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
