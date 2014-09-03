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

""" Error 404 in the channel HTTP request """
class ChannelHTTPError404(Exception):
    pass

""" Error 500 in the channel HTTP request """
class ChannelHTTPError500(Exception):
    pass

""" Error in the channel HTTP request """
class ChannelHTTPError(Exception):
    pass
