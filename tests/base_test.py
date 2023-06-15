from unittest import TestCase
from . import config
from os import environ


class BaseTest(TestCase):
    agent = environ.get('AGENT', 'agent.php')
    url = config.base_url + agent
    password = config.password
    path = config.base_folder + agent

    def shortDescription(self):
        doc = super().shortDescription()
        doc = doc if doc else ''
        return f'[PHP{8 if self.agent == "agent.phar" else 7}] {doc}'
