from unittest import TestCase
import config

class BaseTest(TestCase):
    
    url = config.url
    password = config.password
    path = config.agent