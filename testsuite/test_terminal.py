from testsuite.base_test import BaseTest
from core.weexceptions import FatalException
from testfixtures import log_capture
from core.terminal import Terminal
from core import sessions
from core import modules
from core import messages


class TermExcept(BaseTest):

    @log_capture()
    def setUp(self, log_captured):

        session = sessions.start_session_by_url(self.url, self.password, volatile = True)
        modules.load_modules(session)

        self.terminal = Terminal(session)

    def _assert_exec(self, line, expected, log_captured):
        line = self.terminal.precmd(line)
        stop = self.terminal.onecmd(line)
        stop = self.terminal.postcmd(stop, line)

        self.assertEqual(log_captured.records[-1].msg, expected)

    @log_capture()
    def test_base(self, log_captured):

        # Basic
        self._assert_exec('echo 1', '1', log_captured)

        # Module with single argument
        self._assert_exec(':shell_php echo(1);', '1', log_captured)

        # Module with multiple argument wrognly passed and precisely fixed
        self._assert_exec(':shell_php echo(1); echo(2);', '12', log_captured)

        # Module with multiple argument properly passed
        self._assert_exec(':shell_php "echo(1); echo(2);"', '12', log_captured)

        # Module with mandatory and optional arguments properly passed
        self._assert_exec(':shell_php --postfix_string=" echo(3);" "echo(1); echo(2);"', '123', log_captured)

        # Module with mandatory and optional arguments wrongly passed but precisely fixed
        self._assert_exec(':shell_php --postfix_string=" echo(3);" echo(1); echo(2);', '123', log_captured)

    @log_capture()
    def test_session(self, log_captured):

        # Test to generate a session with a wrong file
        self.assertRaises(FatalException, lambda: sessions.start_session_by_file('BOGUS'))

    @log_capture()
    def test_run_wrong_pass(self, log_captured):

        session = sessions.start_session_by_url(self.url, 'BOGUS', volatile = True)
        modules.load_modules(session)

        terminal = Terminal(session)
        line = 'echo 1'
        line = terminal.precmd(line)
        stop = terminal.onecmd(line)
        stop = terminal.postcmd(stop, line)

        # Test the behaviour when starting terminal on wrong remote pass
        self.assertTrue(
            log_captured.records[-1].msg.endswith(
                messages.terminal.backdoor_unavailable
            )
        )

    @log_capture()
    def test_run_wrong_url(self, log_captured):

        session = sessions.start_session_by_url(self.url + 'BOGUS', 'BOGUS', volatile = True)
        modules.load_modules(session)

        terminal = Terminal(session)
        line = 'echo 1'
        line = terminal.precmd(line)
        stop = terminal.onecmd(line)
        stop = terminal.postcmd(stop, line)

        # Test the behaviour when starting terminal on wrong remote URL
        self.assertTrue(
            log_captured.records[-1].msg.endswith(
                messages.terminal.backdoor_unavailable
            )
        )
