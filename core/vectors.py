from mako.template import Template
from core.weexceptions import DevException, ModuleError
from core import messages

class Os:
    ANY = 0
    NIX = 1
    WIN = 2

class Vector:
    
    def __init__(self, name, module, payload, target = 0):
        self.name = name
        
        if not isinstance(target, int):
            raise DevException(core.messages.wrong_target_type)
        
        self.module = module
        self.payload = payload
        self.target = target

    def format(self, arguments = {}):
        return Template(self.payload).render(args=arguments)


class Vectors(list):
    
    def __init__(self, terminal, module_name):
        
        self.terminal = terminal
        self.module_name = module_name
        
        list.__init__(self)
    
    def get_by_name(self, name):
        for vector in self:
            if vector.name == name:
                return vector
        
    def get_default_vector(self):
        """ Get default vector by name """

        default_vector = self.get_by_name(self.terminal.session[self.module_name]['options']['vector'])
        
        if not default_vector:
            raise ModuleError(messages.vectors.default_vector_not_set)
        
        return default_vector
    
    
    def save_default_vector(self, vector_name):
        """ Save default vector name """

        self.terminal.session[self.module_name]['options']['vector'] = vector_name
        