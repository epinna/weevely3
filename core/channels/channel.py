from core.channels.stegaref.stegaref import StegaRef
from core.weexceptions import FatalException
from urllib2 import HTTPError, URLError
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
        self.channel_loaded = channel_object(url, password)
        self.channel_name = channel_name

    def send(self, payload):

        response = ''
        code = 200

        try:
            response = self.channel_loaded.send(payload)
        except HTTPError as e:
            if e.code:
                code = e.code
        except URLError as e:
            code = -1

        return response, code
