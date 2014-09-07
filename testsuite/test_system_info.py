from testsuite.base_test import BaseTest
from core import modules
from core import sessions
from core import messages
import logging
import os

class SystemInfo(BaseTest):

    def setUp(self):
        session = sessions.start_session_by_url(self.url, self.password, volatile = True)
        modules.load_modules(session)

        self.run_argv = modules.loaded['system_info'].run_argv

    def test_commands(self):

        # Get all infos
        vectors_names = [v.name for v in modules.loaded['system_info'].vectors ]
        self.assertEqual(set(self.run_argv([]).keys()), set(vectors_names));

        # Get just one info
        self.assertEqual(
                      os.path.split(self.run_argv(["--info=script"])['script'])[1],
                      os.path.split(self.path)[1]
        );  

        # Pass unexistant info
        self.assertEqual(self.run_argv(["--info=BOGUS"]), {});

