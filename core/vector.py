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

    # TODO: The vector still does not support modules != 'shell_php'.
    # Could just accept payload as list to send to run_argv. OK to format the whole list.

    def __init__(self, payload, name = None, module = 'shell_php', target = 0, args = [], postprocess = lambda x: x):

        self.name = name if name else commons.randstr()

        if not isinstance(target, int) or not target < 3:
            raise DevException(messages.vectors.wrong_target_type)

        if not callable(postprocess):
            raise DevException(messages.vectors.wrong_postprocessing_type)

        self.module = module
        self.payload = payload
        self.target = target
        self.args = []
        self.postprocess = postprocess

    def format(self, values):
        return Template(self.payload).render(**values)

    def run(self, values = {}):

        try:
            formatted = self.format(values)
        except TypeError as e:
            import traceback
            traceback.print_exc()
            raise DevException(messages.vectors.wrong_arguments_type)
        
        return self.postprocess(
                                  modules.loaded[self.module].run_argv(
                                    [ formatted ] + self.args
                                  )
                )
