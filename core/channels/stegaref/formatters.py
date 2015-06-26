import random
import urlparse
import string
import urllib
import utils
from core import messages


class FirstRefererFormat:

    def __init__(self, url):

        self.url = url
        self.chunks_sizes = []

    def target_name(self):

        parsed_url = urlparse.urlparse(self.url)
        if parsed_url.netloc:
            domain_classes_num = parsed_url.netloc.count('.') + 1

            return '.'.join(
                parsed_url.netloc.split('.')[
                    1:random.randint(
                        1,
                        domain_classes_num)])

        else:
            return self.url

    def target_url_encoded(self):

        parsed_url = urlparse.urlparse(self.url)
        return urllib.quote_plus(
            '%s://%s' %
            (parsed_url.scheme, parsed_url.netloc))

    def rand_number(self, max_size, min_size=1):

        return utils.strings.randstr(max_size, min_size, string.digits)

    def rand_chars(self, max_size, min_size=1):

        return utils.strings.randstr(max_size, min_size, string.ascii_letters)


    def rand_int(self, minint, maxint):

        return random.randint(minint, maxint)

    def payload_chunk(self, max_size, min_size=None):
        """Return the parameter ${ chunk } formatted when sent"""

        if min_size is None:
            min_size = max_size

        self.chunks_sizes.append((min_size, max_size))

        return '${ chunk }'

    def get_url_base(self):
        """Return the parameter ${ url_base } formatted when sent"""

        return '${ url_base }'

    def get_url_agent(self):
        """Return the parameter ${ url_agent } formatted when sent"""

        return '${ url_agent }'

    def rand_domain(self):
        return random.choice(['com', 'ad', 'ae', 'al', 'am', 'as', 'at', 'az',
                              'ba', 'be', 'bf', 'bg', 'bi', 'bj', 'bs', 'bt',
                              'by', 'ca', 'cd', 'cf', 'cg', 'ch', 'ci', 'cl',
                              'cm', 'cn', 'cv', 'cz', 'de', 'dj', 'dk', 'dm',
                              'dz', 'ee', 'es', 'fi', 'fm', 'fr', 'ga', 'ge',
                              'gg', 'gl', 'gm', 'gp', 'gr', 'gy', 'hn', 'hr',
                              'ht', 'hu', 'ie', 'im', 'iq', 'is', 'it', 'je',
                              'jo', 'ki', 'kg', 'kz', 'la', 'li', 'lk', 'lt',
                              'lu', 'lv', 'md', 'me', 'mg', 'mk', 'ml', 'mn',
                              'ms', 'mu', 'mv', 'mw', 'ne', 'nl', 'no', 'nr',
                              'nu', 'pl', 'pn', 'ps', 'pt', 'ro', 'ru', 'rw',
                              'sc', 'se', 'sh', 'si', 'sk', 'sn', 'so', 'sm',
                              'st', 'td', 'tg', 'tk', 'tl', 'tm', 'tn', 'to',
                              'tt', 'vg', 'vu', 'ws', 'rs', 'cat'])

    def rand_google_domain(self):

        # http://www.google.com/supported_domains

        return random.choice(['com', 'ad', 'ae', 'com.af', 'com.ag', 'com.ai',
                              'al', 'am', 'co.ao', 'com.ar', 'as', 'at', 'com.au',
                              'az', 'ba', 'com.bd', 'be', 'bf', 'bg', 'com.bh',
                              'bi', 'bj', 'com.bn', 'com.bo', 'com.br', 'bs', 'bt',
                              'co.bw', 'by', 'com.bz', 'ca', 'cd', 'cf', 'cg',
                              'ch', 'ci', 'co.ck', 'cl', 'cm', 'cn', 'com.co',
                              'co.cr', 'com.cu', 'cv', 'com.cy', 'cz', 'de', 'dj',
                              'dk', 'dm', 'com.do', 'dz', 'com.ec', 'ee', 'com.eg',
                              'es', 'com.et', 'fi', 'com.fj', 'fm', 'fr', 'ga', 'ge',
                              'gg', 'com.gh', 'com.gi', 'gl', 'gm', 'gp', 'gr', 'com.gt',
                              'gy', 'com.hk', 'hn', 'hr', 'ht', 'hu', 'co.id', 'ie',
                              'co.il', 'im', 'co.in', 'iq', 'is', 'it', 'je', 'com.jm',
                              'jo', 'co.jp', 'co.ke', 'com.kh', 'ki', 'kg', 'co.kr',
                              'com.kw', 'kz', 'la', 'com.lb', 'li', 'lk', 'co.ls',
                              'lt', 'lu', 'lv', 'com.ly', 'co.ma', 'md', 'me', 'mg', 'mk',
                              'ml', 'com.mm', 'mn', 'ms', 'com.mt', 'mu', 'mv', 'mw',
                              'com.mx', 'com.my', 'co.mz', 'com.na', 'com.nf', 'com.ng',
                              'com.ni', 'ne', 'nl', 'no', 'com.np', 'nr', 'nu', 'co.nz',
                              'com.om', 'com.pa', 'com.pe', 'com.pg', 'com.ph', 'com.pk',
                              'pl', 'pn', 'com.pr', 'ps', 'pt', 'com.py', 'com.qa', 'ro',
                              'ru', 'rw', 'com.sa', 'com.sb', 'sc', 'se', 'com.sg', 'sh',
                              'si', 'sk', 'com.sl', 'sn', 'so', 'sm', 'st', 'com.sv',
                              'td', 'tg', 'co.th', 'com.tj', 'tk', 'tl', 'tm', 'tn', 'to',
                              'com.tr', 'tt', 'com.tw', 'co.tz', 'com.ua', 'co.ug', 'co.uk',
                              'com.uy', 'co.uz', 'com.vc', 'co.ve', 'vg', 'co.vi', 'com.vn',
                              'vu', 'ws', 'rs', 'co.za', 'co.zm', 'co.zw', 'cat'])
