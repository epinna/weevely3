from unittest import TestCase
from core.utilities import randstr
from testsuite.config import script_folder, script_folder_url
from generate import generate, save_generated
import hashlib
import os

class BaseTest(TestCase):

    @classmethod
    def _randomize_bd(cls):
        cls.password = randstr(10)
        password_hash = hashlib.md5(cls.password).hexdigest().lower()
        filename = '%s_%s.php' % (
            __name__, cls.password)
        cls.url = os.path.join(script_folder_url, filename)
        cls.path = os.path.join(script_folder, filename)

    @classmethod
    def setUpClass(cls):

        cls._randomize_bd()

        obfuscated = generate(cls.password)
        save_generated(obfuscated, cls.path)

    @classmethod
    def tearDownClass(cls):

        # Check the agent presence, could be already deleted 
        if not os.path.isfile(cls.path): return
        #os.remove(cls.path)
        
