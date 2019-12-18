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
            result = self.channel.send(
                    'echo("%s");' %
                    payload.decode('utf-8'))[0]
            self.assertEqual(
                result,
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
        
