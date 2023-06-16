from contextlib import redirect_stdout
import hashlib
import os
import random
import subprocess
from contextlib import redirect_stdout
from io import TextIOWrapper, BytesIO
from unittest import TestCase

import utils
from core.channels.channel import Channel
from core.generate import generate, save_generated
from tests.config import base_folder, base_url


def setUpModule():
    subprocess.check_output("""
BASE_FOLDER="{base_folder}/generators/"
rm -rf "$BASE_FOLDER"

mkdir "$BASE_FOLDER"
chown www-data: -R "$BASE_FOLDER/"
""".format(
base_folder = base_folder
), shell=True)

class TestGenerators(TestCase):

    def test_generators(self):
        with TextIOWrapper(buffer=BytesIO()) as buf, redirect_stdout(buf):
            obfuscated = generate('dummy', 'phar')
            save_generated(obfuscated, '-')
            buf.buffer.seek(0)
            output = buf.buffer.read()

        self.assertTrue(output.startswith(b'<?php'))
        self.assertIn(b'__HALT_COMPILER(); ?>', output)

        for i in range(0, 200):
            self._randomize_bd()
            obfuscated = generate(self.password.decode('utf-8'), self.obfuscator)
            save_generated(obfuscated, self.path)

            self.channel = Channel(
                'ObfPost',
                {
                    'url' : self.url,
                    'password' : self.password.decode('utf-8')
                }
            )
            self._incremental_requests(10, 100, 30, 50)

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
                    payload.decode('utf-8'))[0],
                payload, f'Obfuscator failed: {self.obfuscator}')

    @classmethod
    def _randomize_bd(cls):
        cls.obfuscator = 'obfusc1_php' if random.randint(0, 100) > 50 else 'phar'
        cls.password = utils.strings.randstr(10)
        password_hash = hashlib.md5(cls.password).hexdigest().lower()
        filename = '%s_%s.php' % (
            __name__, cls.password)
        cls.url = os.path.join(base_url, 'generators', filename)
        cls.path = os.path.join(base_folder, 'generators', filename)

    @classmethod
    def _clean_bd(cls):
        os.remove(cls.path)
