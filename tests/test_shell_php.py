from tests.base_test import BaseTest
from testfixtures import log_capture
from core import modules
from core.sessions import SessionURL
from core import messages


class ShellPHP(BaseTest):

    def setUp(self):
        session = SessionURL(self.url, self.password, volatile=True)
        modules.load_modules(session)

        self.run_argv = modules.loaded['shell_php'].run_argv

    @log_capture()
    def test_commands(self, log_captured):
        self.assertEqual(self.run_argv(["echo(1);"]), "1")

        # Check remote error warning
        self.assertEqual(self.run_argv(['throw new Exception("Don\'t panic!");']), "")
        self.assertEqual('[ERR:500] eval: Don\'t panic!',
                         log_captured.records[-1].msg)

        # Check generic remote error
        self.assertEqual(self.run_argv(["echo(1)"]), "")
        self.assertRegex(log_captured.records[-2].msg,
                         messages.module_shell_php.missing_php_trailer_s % ".*echo\\(1\\)")
        self.assertEqual(messages.module_shell_php.error_500_executing,
                         log_captured.records[-1].msg)

        # Check warnings on 404.
        self.assertEqual(self.run_argv(["header('HTTP/1.0 404 Not Found');"]), "")
        self.assertEqual(messages.module_shell_php.error_404_remote_backdoor,
                         log_captured.records[-1].msg)
