from unittest import TestCase
from core.utilities import randstr
from testsuite import config
from generate import generate, save_generated
import subprocess
import tempfile
import hashlib
import os

class BaseTest(TestCase):

    paths_to_delete = []

    @classmethod
    def _randomize_bd(cls):
        cls.password = randstr(10)
        password_hash = hashlib.md5(cls.password).hexdigest().lower()
        filename = '%s_%s.php' % (
            __name__, cls.password)
        cls.url = os.path.join(config.script_folder_url, filename)
        cls.path = os.path.join(config.script_folder, filename)

    @classmethod
    def setUpClass(cls):

        cls._randomize_bd()

        obfuscated = generate(cls.password)

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
