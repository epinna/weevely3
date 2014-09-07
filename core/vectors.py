from mako.template import Template
from core.weexceptions import DevException, ModuleError
from core.vector import Vector, Os
from core import modules
from core import commons
from core import messages


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

    def run(self, arguments = {}, names = [ '' ], names_to_store = [ ]):
        """Run the vectors.

        Run all the Vector objects in the Vectors list. Optionally filter vectors by name
        and save results.

        Args:
            arguments: The dictnary of arguments to format the vectors with
            names: The names lists of vectors to execute
            names_to_store: The names lists of vectors of which save the
                returned result.

        Returns:
            A dict mapping keys to the corresponding the executed vectors
            results.

        Raises:
            Could returns Mako library exceptions while formatting.

        """
        response = {}
                
        for vector in self:
            
            if not any(x in vector.name for x in names): continue

            response[vector.name] = vector.run(arguments)
                
            if not any(x in vector.name for x in names_to_store): continue

            self.session[self.module_name]['results'][vector.name] = response[vector.name]
            
        return response
