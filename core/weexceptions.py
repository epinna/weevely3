""" Fatal errors """
class FatalException(Exception):
    pass

""" Fatal errors on module development """
class DevException(Exception):
    pass

""" Error on module execution """
class ModuleError(Exception):
    pass

""" Argument parsing tried to Exit """
class ArgparseError(Exception):
    pass

""" Error on channel internals """
class ChannelException(Exception):
    pass
