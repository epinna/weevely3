

""" Fatal errors """
class FatalException(Exception):
    pass


""" Fatal errors on module development """
class DevException(Exception):
    pass


""" Error on module execution """
class ModuleError(Exception):
    pass

""" Error on channel internals """
class ChannelException(Exception):
	pass
