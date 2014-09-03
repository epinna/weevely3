from testsuite.base_test import BaseTest
from core import modules
from core import sessions

class ShellPHP(BaseTest):

    def setUp(self):
        session = sessions.start_session_by_url(self.url, self.password, volatile = True)
        modules.load_modules(session)

        self.run_argv = modules.loaded['shell_php'].run_argv


    def test_simple_commands(self):

        self.assertEqual(self.run_argv(["echo(1);"]),"1");
        self.assertEqual(self.run_argv(["echo(1)"]),"");
        
