from tests.config import base_folder, base_url
from core.generate import generate, save_generated
from core.channels.channel import Channel
from unittest import TestCase
import subprocess
import utils
import random
import hashlib
import os

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

        for i in range(0, 100):
            self._randomize_bd()
            obfuscated = generate(self.password.decode('utf-8'))
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
                payload)

    @classmethod
    def _randomize_bd(cls):
        cls.password = utils.strings.randstr(10)
        password_hash = hashlib.md5(cls.password).hexdigest().lower()
        filename = '%s_%s.php' % (
            __name__, cls.password)
        cls.url = os.path.join(base_url, 'generators', filename)
        cls.path = os.path.join(base_folder, 'generators', filename)

    @classmethod
    def _clean_bd(cls):
        os.remove(cls.path)
