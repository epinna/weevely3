from core.channels.channels import get_channel
from testsuite.config import script_folder, script_folder_url
from core.commons import randstr
from unittest import TestCase
from generate import generate, save_generated
import hashlib
import os
import shutil
import logging
import random

class BaseDefaultChannel(TestCase):
   
    @classmethod
    def _randomize_bd(cls):
        cls.password = randstr(10)
        password_hash = hashlib.md5(cls.password).hexdigest()
        filename = '%s_%s_%s.php'% (__name__, password_hash[:3], password_hash[3:6])
        cls.url = os.path.join(script_folder_url, filename)
        cls.path = os.path.join(script_folder, filename)
       
    @classmethod
    def setUpClass(cls):
        
        cls._randomize_bd()
        
        obfuscated = generate(cls.password)
        save_generated(obfuscated, cls.path)


    @classmethod
    def tearDownClass(cls):
        #os.remove(cls.path)
        pass
       
    def setUp(self):
        self.channel = get_channel(self.url, self.password)
        
    
    def _incremental_requests(self, size_start, size_to, step_rand_start, step_rand_to):
        
        for i in range(size_start, size_to, random.randint(step_rand_start, step_rand_to)):
            payload = randstr(i)
            self.assertEqual(self.channel.send('echo("%s");' % payload), payload)
            