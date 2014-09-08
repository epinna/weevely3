from testsuite.base_test import BaseTest
from core.vector import Vector
from core import modules
from core import sessions
from core import messages
import logging
import os

class SystemInfo(BaseTest):

    def setUp(self):
        self.session = sessions.start_session_by_url(self.url, self.password, volatile = True)
        modules.load_modules(self.session)

        self.run_argv = modules.loaded['shell_sh'].run_argv

    def test_run_unless(self):

        vector_safe_name = 'proc_open'

        # Spoil all the module sessions but the safe one
        for i in range(0, len(modules.loaded['shell_sh'].vectors)):
            name = modules.loaded['shell_sh'].vectors[i].name
            payload = modules.loaded['shell_sh'].vectors[i].payload

            if name != vector_safe_name:
                modules.loaded['shell_sh'].vectors[i] = Vector('\'"%s' % payload, name)

        # Check correctness of execution
        self.assertEqual(self.run_argv(["echo 1"]), "1");

        # Check stored vector
        self.assertEqual(self.session['shell_sh']['stored_args']['vector'], vector_safe_name)

    def test_param_vector(self):

        vector_safe_name = 'proc_open'

        # Check correctness of execution
        self.assertEqual(self.run_argv(["echo 1", "--vector=%s" % vector_safe_name]), "1");

        # Check stored vector
        self.assertEqual(self.session['shell_sh']['stored_args']['vector'], vector_safe_name)


