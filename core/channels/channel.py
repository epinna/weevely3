from core.channels.stegaref.stegaref import StegaRef
from core.weexceptions import ChannelHTTPError404, ChannelHTTPError500, ChannelHTTPError
from core.weexceptions import FatalException
from urllib2 import HTTPError
from core import config
from core import messages

class Channel:

    def __init__(self, url, password, channel_name = None):
        """
        Import and instanciate dynamically the channel.

        Given the channel object Mychannel, this should be placed
        in module core.channels.mychannel.mychannel.
        """

        if not channel_name:
            channel_name = config.channel_default

        module_name = channel_name.lower()

        try:
            # Import module
            module = __import__(
                'core.channels.%s.%s' %
                (module_name, module_name), fromlist=["*"])
                
            # Import object
            channel_object = getattr(module, channel_name)
        except:
            raise FatalException(messages.channels.error_loading_channel_s % (channel_name))
            
        # Create channel instance
        self.channel = channel_object(url, password)

    def send(self, payload):

        try:
            self.channel.send(payload)
        except HTTPError as e:
            if e.code == 404:
                raise ChannelHTTPError404
            elif e.code == 500:
                raise ChannelHTTPError500
            else:
                raise ChannelHTTPError
