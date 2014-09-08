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

    def run_until(self, values = {}, until_return = None, store_result = False):
        """Run the next vectors until returns a specified result.

        Run next vectors in lists until returns specified value.
        Optionally store result.

        Args:
            values: The dictionary of arguments to format the vectors with.
            until_return: Run all vectors until returns this value.
            store_result: Store result,
            

        Returns:
            A tuple containing the vector name, and the vector result.

        Raises:
            Could returns Mako library exceptions while formatting.

        """

        for vector in self:

            if not self._os_match(vector.target): continue

            result = vector.run(values)

            if result == which_returns:

                if store_as_default_vector:
                    self.session[self.module_name]['stored_args']['vector'] = response[vector.name]
                
                return vector_name, result

        return None, None

    def run_one(self, name, values = {}, store = False):
        """Run one module vector.

        Run the vectors with specified name. With unspecified names,
        run all the vectors. Optionally store results.

        Args:
            values: The dictionary of arguments to format the vectors with.
            name: The name string of vector to execute.
            store: The boolean value to store the result.

        Returns:
            A string with the execution result.

        Raises:
            Could returns Mako library exceptions while formatting.

        """

        vector = self.get_by_name(name)

        if vector and self._os_match(vector.target):
            result = vector.run(values)

            if store:
                self.session[self.module_name]['results'][name] = result

            return result


    def run_all(self, names = [ '' ], values = {}, names_to_store = [ ]):
        """Run all the vectors.

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

            if not self._os_match(vector.target): continue
            
            if not any(x in vector.name for x in names): continue

            response[vector.name] = vector.run(values)
                
            if not any(x in vector.name for x in names_to_store): continue

            self.session[self.module_name]['results'][vector.name] = response[vector.name]

        return response

    def _os_match(self, os):
        """Check if vector os is compatible with the remote os
        """

        os_string = self.session['system_info']['results'].get('os')

        # If os_string is not set, just return True and continue
        if not os_string: return True

        os_current = s.WIN if os_string.lower().startswith('win') else Os.NIX
        
        return os in (os_current, Os.ANY)

    def get_by_name(self, name):
        for vector in self:
            if vector.name == name:
                return vector

    def get_names(self):
        return [ v.name for v in self ]
