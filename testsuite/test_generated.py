from testsuite.base_channel import BaseDefaultChannel
from core.commons import randstr
from testsuite.config import script_folder, script_folder_url, test_generated_test_all_agents
from generate import generate, save_generated
import os
import unittest

class AgentDEFAULTObfuscatorDefault(BaseDefaultChannel):
    
    def test_100_x_100_requests(self):
        self._multiple_requests(100,100)
               
    def test_10_x_500_requests(self):
        self._multiple_requests(10,500)
                 
    def test_1_x_1000_requests(self):
        self._multiple_requests(1,1000)


@unittest.skipIf(not test_generated_test_all_agents, "Test only default generator agent") 
class AgentDefaultObfuscatorCLEARTEXT(AgentDEFAULTObfuscatorDefault):
       
    @classmethod
    def setUpClass(cls):
        obfuscated = generate(cls.password, obfuscator='cleartext1_php')
        save_generated(obfuscated, cls.path)

    def test_100_x_100_requests(self):
        self._multiple_requests(100,100)
             
    def test_10_x_500_requests(self):
        self._multiple_requests(10,500)
               
    def test_1_x_1000_requests(self):
        self._multiple_requests(1,1000)
      
@unittest.skipIf(not test_generated_test_all_agents, "Test only default generator agent") 
class AgentDEBUGObfuscatorDefault(AgentDEFAULTObfuscatorDefault):
       
    @classmethod
    def setUpClass(cls):
        obfuscated = generate(cls.password, agent='stegaref_php_debug')
        save_generated(obfuscated, cls.path)
         
@unittest.skipIf(not test_generated_test_all_agents, "Test only default generator agent") 
class AgentUNMINIFIEDObfuscatorDefault(AgentDEFAULTObfuscatorDefault):
      
    @classmethod
    def setUpClass(cls):
        obfuscated = generate(cls.password, agent='stegaref_php_unminified')
        save_generated(obfuscated, cls.path)
         