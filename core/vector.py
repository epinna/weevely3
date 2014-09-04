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

    def __init__(self, payload, name = None, module = 'shell_php', target = 0):

        self.name = name if name else commons.randstr()

        if not isinstance(target, int) or not target < 3:
            raise DevException(messages.vectors.wrong_target_type)

        self.module = module
        self.payload = payload
        self.target = target

    def format(self, args):
        return Template(self.payload).render(**args)

    def run(self, args = {}):

        try:
            formatted = self.format(args)
        except TypeError as e:
            import traceback
            traceback.print_exc()
            raise DevException(messages.vectors.wrong_arguments_type)
        
        return modules.loaded[self.module].run_argv([formatted])
