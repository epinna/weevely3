from tests.base_test import BaseTest
from core.channels.channel import Channel
from core.weexceptions import DevException
import utils
from core.generate import generate, save_generated
import os
import random
import unittest
from tests import config
from core.loggers import stream_handler
import logging
import subprocess
import tempfile
import core.config
import socket


def _get_google_ip():
    try:
        data = socket.gethostbyname('www.google.com')
        ip = repr(data)
        if ip:
            return ip
    except Exception:
        pass

class StegaRefChannel(BaseTest):

    def setUp(self):
        self.channel = Channel(
            'StegaRef',
            {
                'url' : self.url,
                'password' : self.password
            }
        )

    def _incremental_requests(
            self,
            size_start,
            size_to,
            step_rand_start,
            step_rand_to):

        for i in range(size_start, size_to, random.randint(step_rand_start, step_rand_to)):
            payload = utils.strings.randstr(i)
            self.assertEqual(
                self.channel.send(
                    'echo("%s");' %
                    payload)[0],
                payload)


class StegaRefChannelAdditionalHeaders(StegaRefChannel):

    def test_additional_headers(self):
        self.channel.channel_loaded.additional_headers = [
            ( 'Cookie', 'C1=F1; C2=F2; C3=F3; C4=F4'),
            ( 'Accept', 'ACCEPT1'),
            ( 'Referer', 'REFERER1'),
            ( 'X-Other-Cookie', 'OTHERCOOKIE')
        ]

        headers_string = self.channel.send(
                            'print_r(getallheaders());'
        )[0]

        # Cookiejar used to add cookies in additional headers add them in casual orders
        self.assertIn('C1=F1', headers_string)
        self.assertIn('C2=F2', headers_string)
        self.assertIn('C3=F3', headers_string)
        self.assertIn('C4=F4', headers_string)
        self.assertNotIn('ACCEPT1', headers_string)
        self.assertNotIn('REFERER1', headers_string)
        self.assertIn('OTHERCOOKIE', headers_string)



class StegaRefChannelWrongCert(BaseTest):

    def setUp(self):
        
        ip = _get_google_ip()
        if not ip:
            return 
            
        url = 'https://%s/nonexistent' % (ip)
        
        self.channel = Channel(
            'StegaRef',
            {
                'url' : url,
                'password' : 'none'
            }
        )

    def test_wrong_cert(self):
        
        try:
            self.channel.send('echo("1");')
        except Exception as e:
            self.fail("test_wrong_cert exception\n%s" % (str(e)))

@unittest.skipIf(
    not config.test_stress_channels,
    "Test only default generator agent")
class AgentDEFAULTObfuscatorDefault(StegaRefChannel):

    def test_1_100_requests(self):
        self._incremental_requests(1, 100, 1, 3)

    def test_100_1000_requests(self):
        self._incremental_requests(100, 1000, 90, 300)

    def test_1000_10000_requests(self):
        self._incremental_requests(1000, 10000, 900, 3000)

    def test_10000_50000_requests(self):
        self._incremental_requests(10000, 50000, 9000, 30000)


@unittest.skipIf(
    not config.test_stress_channels,
    "Test only default generator agent")
class LegacyCookieChannel(BaseTest):

    url = config.base_url + '/test_channels/legacycookie_php.php'

    def setUp(self):
        
        self.channel = Channel(
            'LegacyCookie',
            {
                'url' : self.url,
                'password' : self.password
            }
        )

    def _incremental_requests(
            self,
            size_start,
            size_to,
            step_rand_start,
            step_rand_to):

        for i in range(size_start, size_to, random.randint(step_rand_start, step_rand_to)):
            payload = utils.strings.randstr(i)
            self.assertEqual(
                self.channel.send(
                    'echo("%s");' %
                    payload)[0],
                payload)

    def test_1_100_requests(self):
        self._incremental_requests(1, 100, 1, 2)

    def test_100_1000_requests(self):
        self._incremental_requests(100, 1000, 10, 20)

    def test_additional_headers(self):
        self.channel.channel_loaded.additional_headers = [
            ( 'Cookie', 'C1=F1; C2=F2; C3=F3; C4=F4;'),
            ( 'User-Agent', 'CLIENT'),
            ( 'X-Other-Cookie', 'OTHER')
        ]

        headers_string = self.channel.send(
                            'print_r(getallheaders());'
        )[0]

        self.assertRegexpMatches(headers_string, '\[Cookie\] => [A-Z0-9]+=[^ ]{2}; C1=F1; C2=F2; C3=F3; C4=F4(; [A-Z0-9]+=[^ ]+)+')
        self.assertRegexpMatches(headers_string, '\[User-Agent\] => CLIENT')
        self.assertRegexpMatches(headers_string, '\[X-Other-Cookie\] => OTHER')

        self.channel.channel_loaded.additional_headers = [ ]

    def test_wrong_cert(self):
        
        ip = _get_google_ip()
        if not ip:
            return 
            
        url = 'https://%s/nonexistent' % (ip)
        
        channel = Channel(
            'LegacyCookie',
            {
                'url' : url,
                'password' : 'none'
            }
        )
        
        try:
            channel.send('echo("1");')
        except Exception as e:
            self.fail("LegacyCookie test_wrong_cert exception\n%s" % (str(e)))

@unittest.skipIf(
    not config.test_stress_channels,
    "Test only default generator agent")
class AgentDEBUGObfuscatorCLEARTEXT(AgentDEFAULTObfuscatorDefault):

    url = config.base_url + '/test_channels/stegaref_php_debug.php'


@unittest.skipIf(
    not config.test_stress_channels,
    "Test only default generator agent")
class LegacyReferrerChannel(BaseTest):

    url = config.base_url + '/test_channels/legacyreferrer.php'
    password = 'asdasd'

    def setUp(self):
        self.channel = Channel(
            'LegacyReferrer',
            {
                'url' : self.url,
                'password' : self.password
            }
        )

    def _incremental_requests(
            self,
            size_start,
            size_to,
            step_rand_start,
            step_rand_to):

        for i in range(size_start, size_to, random.randint(step_rand_start, step_rand_to)):
            payload = utils.strings.randstr(i)
            self.assertEqual(
                self.channel.send(
                    'echo("%s");' %
                    payload)[0],
                payload)

    def test_1_100_requests(self):
        self._incremental_requests(1, 100, 1, 2)

    def test_100_1000_requests(self):
        self._incremental_requests(100, 1000, 10, 20)

    def test_additional_headers(self):
        self.channel.channel_loaded.additional_headers = [
            ( 'Cookie', 'C1=F1; C2=F2; C3=F3; C4=F4'),
            ( 'Referer', 'REFERER'),
            ( 'X-Other-Cookie', 'OTHER')
        ]

        headers_string = self.channel.send(
                            'print_r(getallheaders());'
        )[0]

        self.assertIn('[Cookie] => C1=F1; C2=F2; C3=F3; C4=F4', headers_string)
        self.assertNotIn('REFERER1', headers_string)
        self.assertIn('[X-Other-Cookie] => OTHER', headers_string)


    def test_wrong_cert(self):
        
        ip = _get_google_ip()
        if not ip:
            return 
            
        url = 'https://%s/nonexistent' % (ip)
        
        channel = Channel(
            'LegacyReferrer',
            {
                'url' : url,
                'password' : 'none'
            }
        )
        
        try:
            channel.send('echo("1");')
        except Exception as e:
            self.fail("LegacyReferrer test_wrong_cert exception\n%s" % (str(e)))
