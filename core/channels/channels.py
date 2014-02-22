from core.channels.stegaref.stegaref import StegaRef
from core.weexceptions import FatalException
from core import messages


def get_channel(url, password, channel = 'stegaref'):
    
    if channel == 'stegaref':
        return StegaRef(url, password)
    else:
        raise FatalException(messages.channels.error_loading_channel_s % channel)
    return