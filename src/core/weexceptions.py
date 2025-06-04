""" Fatal errors """
class FatalException(Exception):
    pass

""" Fatal errors on module development """
class DevException(Exception):
    pass

""" Argument parsing tried to Exit """
class ArgparseError(Exception):
    pass

""" Error on channel internals """
class ChannelException(Exception):
    # This should be intercepted not at send()
    # but at some level before (e.g. when) calling
    # setup to interrupt directly the cmd execution
    pass
