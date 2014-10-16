from testsuite.base_test import BaseTest
from core.channels.channel import Channel
from core.utilities import randstr
from testsuite.config import script_folder, script_folder_url, test_stress_channels
from generate import generate, save_generated
import os
import random
import unittest

class BaseDefaultChannel(BaseTest):

    def setUp(self):
        self.channel = Channel(self.url, self.password)

    def _incremental_requests(
            self,
            size_start,
            size_to,
            step_rand_start,
            step_rand_to):

        for i in range(size_start, size_to, random.randint(step_rand_start, step_rand_to)):
            payload = randstr(i)
            self.assertEqual(
                self.channel.send(
                    'echo("%s");' %
                    payload)[0],
                payload)

@unittest.skipIf(
    not test_stress_channels,
    "Test only default generator agent")
class AgentDEFAULTObfuscatorDefault(BaseDefaultChannel):

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
