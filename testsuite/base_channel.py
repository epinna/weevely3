from core.channels.channel import Channel
from testsuite.base_test import BaseTest
from core.utilities import randstr
import random

class BaseDefaultChannel(BaseTest):

    def setUp(self):
        self.channel = Channel(self.url, self.password)

    def _incremental_requests(
            self,
            size_start,
            size_to,
            step_rand_start,
            step_rand_to):

        for i in range(size_start, size_to, random.randint(step_rand_start, step_rand_to)):
            payload = randstr(i)
            self.assertEqual(
                self.channel.send(
                    'echo("%s");' %
                    payload)[0],
                payload)
