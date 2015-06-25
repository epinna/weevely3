"""
The module `core.vectorlist` defines a `VectorList` object, normally used
to store the module vectors.

Module class executes `_register_vectors()` at init to initialize the `VectorList`
object as `self.vectors` module attribute.

The methods exposed by VectorList can be used to get the result of a
given vector execution with `get_result()`, get all the results of a bunch of
vectors with `get_results()`, or get the result of the first vector that
response in the way we want with `find_first_result()`.

"""

from core.vectors import Os
from mako.template import Template
from core.weexceptions import DevException
from core.loggers import log, dlog
from core import modules
import utils
from core import messages

class VectorList(list):

    def __init__(self, session, module_name):

        self.session = session
        self.module_name = module_name

        list.__init__(self)

    def find_first_result(self, names = [], format_args = {}, condition = None, store_result = False, store_name = ''):
        """ Execute all the vectors and return the first result matching the given condition.

        Return the name and the result of the first vector execution response that satisfy
        the given condition.

        With unspecified names, execute all the vectors. Optionally store results.

        Exceptions triggered checking condition function are catched and logged.

        Args:
            names (list of str): The list of names of vectors to execute.

            format_args (dict): The arguments dictionary used to format the vectors with.

            condition (function): The function or lambda to check certain conditions on result.
            Must returns boolean.

            store_result (bool): Store as result.

            store_name (str): Store the found vector name in the specified argument.

        Returns:
            Tuple. Contains the vector name and execution result in the
            `( vector_name, result )` form.

        """

        if not callable(condition):
            raise DevException(messages.vectors.wrong_condition_type)
        if not isinstance(store_name, str):
            raise DevException(messages.vectors.wrong_store_name_type)

        for vector in self:

            # Skip with wrong vectors
            if not self._os_match(vector.target): continue

            # Clean names filter from empty objects
            names = [ n for n in names if n ]

            # Skip if names filter is passed but current vector is missing
            if names and not any(n in vector.name for n in names): continue

            # Add current vector name
            format_args['current_vector'] = vector.name

            # Run
            result = vector.run(format_args)

            # See if condition is verified
            try:
                condition_result = condition(result)
            except Exception as e:
                import traceback; log.info(traceback.format_exc())
                log.debug(messages.vectorlist.vector_s_triggers_an_exc % vector.name)

                condition_result = False

            # Eventually store result or vector name
            if condition_result:
                if store_result:
                    self.session[self.module_name]['results'][vector.name] = result
                if store_name:
                    self.session[self.module_name]['stored_args'][store_name] = vector.name

                return vector.name, result

        return None, None

    def get_result(self, name, format_args = {}, store_result = False):
        """Execute one vector and return the result.

        Run the vector with specified name. Optionally store results.

        Args:
            name (str): The name of vector to execute.

            format_args (dict): The arguments dictionary used to format the vectors with.

            store_result (bool): Store result in session.

        Returns:
            Object. Contains the vector execution result.

        """

        vector = self.get_by_name(name)

        if vector and self._os_match(vector.target):

            # Add current vector name
            format_args['current_vector'] = vector.name

            result = vector.run(format_args)

            if store_result:
                self.session[self.module_name]['results'][name] = result

            return result


    def get_results(self, names = [], format_args = {}, results_to_store = [ ]):
        """Execute all the vectors and return the results.

        With unspecified names, execute all the vectors. Optionally store results.
        Returns a dictionary with results.

        Args:
            names (list of str): The list of names of vectors to execute.

            format_args (dict): The arguments dictionary used to format the vectors with.

            results_to_store (list of str): The list of names of the vectors which
            store the execution result.

        Returns:
            Dictionary. Contains all the vector results in the
            `{ vector_name : result }` form.
        """

        response = {}

        for vector in self:

            if not self._os_match(vector.target): continue

            if names and not any(x in vector.name for x in names): continue

            # Add current vector name
            format_args['current_vector'] = vector.name

            response[vector.name] = vector.run(format_args)

            if not any(x in vector.name for x in results_to_store): continue

            self.session[self.module_name]['results'][vector.name] = response[vector.name]

        return response

    def _os_match(self, os):
        """Check if vector os is compatible with the remote os."""

        os_string = self.session['system_info']['results'].get('os')

        # If os_string is not set, just return True and continue
        if not os_string: return True

        os_current = Os.WIN if os_string.lower().startswith('win') else Os.NIX

        return os in (os_current, Os.ANY)

    def get_by_name(self, name):
        """Get the vector object by name.

        Args:
            name (str): the name of the requested vector.

        Returns:
            Vector object.
        """
        return next((v for v in self if v.name == name), None)

    def get_names(self):
        """Get the vectors names.

        Returns:
            List of strings. Contain vectors names.
        """
        return [ v.name for v in self ]
