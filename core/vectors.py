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

    def run(self, args):

        try:
            formatted = self.format(args)
        except TypeError as e:
            import traceback
            traceback.print_exc()
            raise DevException(messages.vectors.wrong_arguments_type)
        
        return modules.loaded[self.module].run_argv([formatted])


class Vectors(list):

    def __init__(self, session, module_name):

        self.session = session
        self.module_name = module_name

        list.__init__(self)

    def get_by_name(self, name):
        for vector in self:
            if vector.name == name:
                return vector

    def get_default_vector(self):
        """ Get default vector by name """

        default_vector = self.get_by_name(
            self.session[
                self.module_name]['options']['vector'])

        if not default_vector:
            raise ModuleError(messages.vectors.default_vector_not_set)

        return default_vector

    def save_default_vector(self, vector_name):
        """ Save default vector name """

        self.session[self.module_name][
            'options']['vector'] = vector_name
