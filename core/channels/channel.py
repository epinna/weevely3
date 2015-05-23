from core.channels.stegaref.stegaref import StegaRef
from core.weexceptions import FatalException
from urllib2 import HTTPError, URLError
from core import messages
from core.loggers import log
import socks
import sockshandler
import urllib2
import re

url_dissector = re.compile(
    r'^(https?|socks4|socks5)://'  # http:// or https://
    # domain...
    r'((?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'
    r'localhost|'  # localhost...
    r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
    r':(\d+)?'  # optional port
    r'(?:/?|[/?]\S+)$',
    re.IGNORECASE
)

class Channel:

    def __init__(self, channel_name, session):
        """
        Import and instanciate dynamically the channel.

        Given the channel object Mychannel, this should be placed
        in module core.channels.mychannel.mychannel.
        """

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

        self.session = session

        # Create channel instance
        self.channel_loaded = channel_object(
            self.session['url'],
            self.session['password']
        )

        self.channel_name = channel_name

    def _get_proxy(self):

        url_dissected = url_dissector.findall(
            self.session['proxy']
        )

        if url_dissected and len(url_dissected[0]) == 3:
            protocol, host, port = url_dissected[0]
            if protocol == 'socks5':
                return (socks.PROXY_TYPE_SOCKS5, host, int(port))
            if protocol == 'socks4':
                return (socks.PROXY_TYPE_SOCKS4, host, int(port))
            if protocol.startswith('http'):
                return (socks.PROXY_TYPE_HTTP, host, int(port))

        return None, None, None

    def _additional_handlers(self):

        handlers = []

        if self.session.get('proxy'):
            protocol, host, port = self._get_proxy()

            if protocol and host and port:
                handlers.append(
                    sockshandler.SocksiPyHandler(
                        protocol,
                        host,
                        port
                    )
                )
            else:
                raise FatalException(messages.channels.error_proxy_format)

        return handlers

    def send(self, payload):

        response = ''
        code = 200

        try:
            response = self.channel_loaded.send(
                payload,
                self._additional_handlers()
            )
        except socks.ProxyError as e:
            if e.socket_err.errno:
                code = -e.socket_err.errno
        except HTTPError as e:
            if e.code:
                code = e.code
        except URLError as e:
            code = 0

        return response, code
