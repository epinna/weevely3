from testsuite.base_channel import BaseDefaultChannel
from core.commons import randstr
from testsuite.config import script_folder, script_folder_url, test_generated_test_all_agents
from generate import generate, save_generated
import os
import unittest

class AgentDEFAULTObfuscatorDefault(BaseDefaultChannel):
    
    def test_1_100_requests(self):
        self._incremental_requests(1,100, 1, 3)

    def test_100_1000_requests(self):
        self._incremental_requests(100,1000, 5, 15)
    
    def test_1000_10000_requests(self):
        self._incremental_requests(1000,10000, 900,1100)

    def test_10000_100000_requests(self):
        self._incremental_requests(1000,100000, 40000, 60000)

@unittest.skipIf(not test_generated_test_all_agents, "Test only default generator agent") 
class AgentDefaultObfuscatorCLEARTEXT(AgentDEFAULTObfuscatorDefault):
       
    @classmethod
    def setUpClass(cls):
        cls._randomize_bd()
        obfuscated = generate(cls.password, obfuscator='cleartext1_php')
        save_generated(obfuscated, cls.path)
      
@unittest.skipIf(not test_generated_test_all_agents, "Test only default generator agent") 
class AgentDEBUGObfuscatorDefault(AgentDEFAULTObfuscatorDefault):
       
    @classmethod
    def setUpClass(cls):
        cls._randomize_bd()
        obfuscated = generate(cls.password, agent='stegaref_php_debug')
        save_generated(obfuscated, cls.path)
         
@unittest.skipIf(not test_generated_test_all_agents, "Test only default generator agent") 
class AgentUNMINIFIEDObfuscatorDefault(AgentDEFAULTObfuscatorDefault):
      
    @classmethod
    def setUpClass(cls):
        cls._randomize_bd()
        obfuscated = generate(cls.password, agent='stegaref_php_unminified')
        save_generated(obfuscated, cls.path)
         