from testsuite.base_test import BaseTest
from core.vectors import Os, Vectors
from core.vector import PhpCmd
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

    def _spoil_vectors_but(self, vector_safe_name):
        # Spoil all the module sessions but the safe one
        for i in range(0, len(modules.loaded['shell_sh'].vectors)):
            name = modules.loaded['shell_sh'].vectors[i].name
            payload = modules.loaded['shell_sh'].vectors[i].options[0]

            if name != vector_safe_name:
                modules.loaded['shell_sh'].vectors[i] = PhpCmd('\'"%s' % payload, name)

    def test_run_unless(self):

        vector_safe_name = 'proc_open'

        self._spoil_vectors_but(vector_safe_name)

        # Check correctness of execution
        self.assertEqual(self.run_argv(["echo 1"]), "1");

        # Check stored vector
        self.assertEqual(self.session['shell_sh']['stored_args']['vector'], vector_safe_name)

    def test_param_vector(self):

        vector_safe_name = 'proc_open'

        # Check correctness of execution
        self.assertEqual(self.run_argv(["--vector=%s" % vector_safe_name, "echo 1"]), "1");

        # Check stored vector
        self.assertEqual(self.session['shell_sh']['stored_args']['vector'], vector_safe_name)

    def test_vector_one_os(self):

        bogus_vector = 'bogus_win'

        # Add a bogus Os.WIN vector
        modules.loaded['shell_sh'].vectors.append(PhpCmd("echo(1);", name=bogus_vector, target=Os.WIN))

        # Check if called forced the bogusv vector name, returns Null
        self.assertIsNone(self.run_argv(["--vector=%s" % (bogus_vector), "echo 1"]));

    def test_vector_all_os(self):

        bogus_vector = 'bogus_win'

        # Add a bogus Os.WIN vector
        modules.loaded['shell_sh'].vectors.append(PhpCmd("echo(1);", name=bogus_vector, target=Os.WIN))

        # Spoil all vectors but bogus_win
        self._spoil_vectors_but(bogus_vector)

        # Check if looping all vectors still returns None
        self.assertIsNone(self.run_argv(["echo 1"]), None);
