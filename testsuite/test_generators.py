from testsuite.config import script_folder, script_folder_url
from core.generate import generate, save_generated
from core.channels.channel import Channel
from unittest import TestCase
import utils
import random
import hashlib
import os

class TestGenerators(TestCase):

    def test_generators(self):

        for i in range(0, 500):
            self._randomize_bd()
            obfuscated = generate(self.password)
            save_generated(obfuscated, self.path)

            self.channel = Channel(
                'StegaRef',
                {
                    'url' : self.url,
                    'password' : self.password
                }
            )

            self._clean_bd()

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
    def _randomize_bd(cls):
        cls.password = utils.strings.randstr(10)
        password_hash = hashlib.md5(cls.password).hexdigest().lower()
        filename = '%s_%s.php' % (
            __name__, cls.password)
        cls.url = os.path.join(script_folder_url, filename)
        cls.path = os.path.join(script_folder, filename)

    @classmethod
    def _clean_bd(cls):
        os.remove(cls.path)
