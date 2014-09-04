from testsuite.base_test import BaseTest
from testfixtures import log_capture
from core import modules
from core import sessions
from core import messages
import logging

class ShellPHP(BaseTest):

    def setUp(self):
        session = sessions.start_session_by_url(self.url, self.password, volatile = True)
        modules.load_modules(session)

        self.run_argv = modules.loaded['shell_php'].run_argv

    @log_capture()
    def test_commands(self, log_captured):
                
        self.assertEqual(self.run_argv(["echo(1);"]),"1");
        self.assertEqual(self.run_argv(["echo(1)"]),"");        
        self.assertEqual(messages.module_shell_php.missing_php_trailer_s % "');echo(1)",
                        log_captured.records[-1].msg)
