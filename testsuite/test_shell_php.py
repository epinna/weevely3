from core.channels.channels import get_channel
from testsuite.base_test import BaseTest
from core import modules
from core import sessions

class ShellPHP(BaseTest):

    def setUp(self):
        session = sessions.start_session_by_url(self.url, self.password, volatile = True)
        modules.load_modules(session)

        self.run_cmdline = modules.loaded['shell_php'].run_cmdline


    def test_simple_commands(self):

        self.assertEqual(self.run_cmdline("echo(1);"),"1");
        
