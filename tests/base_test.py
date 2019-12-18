from unittest import TestCase
from . import config

class BaseTest(TestCase):
    
    url = config.url
    password = config.password
    path = config.agent