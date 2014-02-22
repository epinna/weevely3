

""" Fatal errors """
class FatalException(Exception):
    pass


""" Fatal errors on module development """
class DevException(Exception):
    pass


""" Error communicating with basic interpreter """
class InterpreterException(Exception):
    pass

""" Error on module execution """
class ModuleError(Exception):
    pass