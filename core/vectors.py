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


    def run_until(self, values = {}, until_return = None, store_result = False):
        """Run the next vectors until returns a specified result.

        Run next vectors in lists until returns specified value.
        Optionally store result.

        Args:
            values: The dictionaries of arguments to format the vectors with.
            until_return: Run all vectors until returns this value.
            store_result: Store result,
            

        Returns:
            A tuple containing the vector name, and the vector result.

        Raises:
            Could returns Mako library exceptions while formatting.

        """

        for vector in self:

            result = vector.run(values)

            if result == which_returns:

                if store_as_default_vector:
                    self.session[self.module_name]['options']['vector'] = response[vector.name]
                
                return vector_name, result

        return None, None
        

    def run(self, values = {}, names = [ '' ], names_to_store = [ ]):
        """Run the vectors in names.

        Run all the vectors which match passed names. With unspecified names,
        run all the vectors. Optionally store results.

        Args:
            values: The dictionary of arguments to format the vectors with.
            names: The names lists of vectors to execute.
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

            response[vector.name] = vector.run(values)
                
            if not any(x in vector.name for x in names_to_store): continue

            self.session[self.module_name]['results'][vector.name] = response[vector.name]

        return response
