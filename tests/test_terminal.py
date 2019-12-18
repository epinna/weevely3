from tests.base_test import BaseTest
from core.weexceptions import FatalException
from testfixtures import log_capture
from core.terminal import Terminal
from core.sessions import SessionURL, SessionFile
from core import modules
from core import messages
import subprocess

def setUpModule():
    subprocess.check_output("""
echo 1 > "/tmp/sessionfile1"
echo 'url: http://localhost:123' > "/tmp/sessionfile2"
echo '' > "/tmp/sessionfile3"
""", shell=True)

class TerminalTest(BaseTest):

    @log_capture()
    def setUp(self, log_captured):

        session = SessionURL(self.url, self.password, volatile = True)
        modules.load_modules(session)

        self.terminal = Terminal(session)

        self.brokensessionfiles = [
            '/nonexistent',
            '/tmp/sessionfile1',
            '/tmp/sessionfile2',
            '/tmp/sessionfile3'
        ]

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
        self._assert_exec(':shell_php -postfix-string echo(3); "echo(1); echo(2);"', '123', log_captured)

        # Module with mandatory and optional arguments wrongly passed but precisely fixed
        self._assert_exec(':shell_php -postfix-string echo(3); echo(1); echo(2);', '123', log_captured)

    @log_capture()
    def test_session(self, log_captured):

        # Test to open a session from wrong files
        for path in self.brokensessionfiles:
            self.assertRaises(FatalException, lambda: SessionFile(path))
                
    @log_capture()
    def test_run_wrong_pass(self, log_captured):

        session = SessionURL(self.url, 'BOGUS', volatile = True)
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

        session = SessionURL(self.url + 'BOGUS', 'BOGUS', volatile = True)
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

    @log_capture()
    def test_quote_error(self, log_captured):

        err_msg = 'Error parsing command: No closing quotation'

        self._assert_exec(':shell_php \'', err_msg, log_captured)
        self._assert_exec(':set shell_php "', err_msg, log_captured)


    @log_capture()
    def test_set(self, log_captured):

        self._assert_exec(':set', messages.terminal.set_usage, log_captured)
        self._assert_exec(':set ASD', messages.terminal.set_usage, log_captured)
        self._assert_exec(':set asd asd', messages.sessions.error_session_s_not_modified % 'asd', log_captured)
        self._assert_exec(':set asd asd asd', messages.sessions.error_session_s_not_modified % 'asd', log_captured)
        self._assert_exec(':set channel asd', messages.sessions.set_s_s % ('channel', 'asd'), log_captured)
        self._assert_exec(':set shell_sh.vector asd', messages.sessions.set_module_s_s_s % ('shell_sh', 'vector', 'asd'), log_captured)

    @log_capture()
    def test_unset(self, log_captured):

        self._assert_exec(':unset', messages.terminal.unset_usage, log_captured)
        self._assert_exec(':unset ASD', messages.sessions.error_session_s_not_modified % 'ASD', log_captured)
        self._assert_exec(':unset asd asd', messages.sessions.error_session_s_not_modified % 'asd asd', log_captured)
        self._assert_exec(':unset channel', messages.sessions.unset_s % ('channel'), log_captured)
        self._assert_exec(':set shell_sh.vector asd', messages.sessions.set_module_s_s_s % ('shell_sh', 'vector', 'asd'), log_captured)
        self._assert_exec(':unset shell_sh.vector', messages.sessions.unset_module_s_s % ('shell_sh', 'vector'), log_captured)


    @log_capture()
    def test_session_shell_vector(self, log_captured):

        self._assert_exec(':set shell_sh.vector BOGUS', messages.sessions.set_module_s_s_s % ('shell_sh', 'vector', 'BOGUS'), log_captured)
        self._assert_exec(':show shell_sh.vector', messages.sessions.set_module_s_s_s % ('shell_sh', 'vector', 'BOGUS'), log_captured)

        # Vectorlist methods ignore bogus vectors and just keep trying.
        # TODO: should warn about unexistant vector, but seems too messy to fix
        self._assert_exec('echo 1', '1', log_captured)
        self._assert_exec(':show shell_sh.vector', messages.sessions.set_module_s_s_s % ('shell_sh', 'vector', 'system'), log_captured)

        self._assert_exec(':set shell_sh.vector passthru', messages.sessions.set_module_s_s_s % ('shell_sh', 'vector', 'passthru'), log_captured)
        self._assert_exec(':show shell_sh.vector', messages.sessions.set_module_s_s_s % ('shell_sh', 'vector', 'passthru'), log_captured)        
        self._assert_exec('echo 1', '1', log_captured)
        self._assert_exec(':show shell_sh.vector', messages.sessions.set_module_s_s_s % ('shell_sh', 'vector', 'passthru'), log_captured)


    @log_capture()
    def test_session_channel(self, log_captured):

        self._assert_exec('echo 1', '1', log_captured)
        self._assert_exec(':set channel BOGUS', messages.sessions.set_s_s % ('channel', 'BOGUS'), log_captured)
        self._assert_exec('echo 1', messages.channels.error_loading_channel_s % 'BOGUS', log_captured)
        self._assert_exec(':unset channel', messages.sessions.unset_s % ('channel'), log_captured)

    @log_capture()
    def test_session_proxy(self, log_captured):

        self._assert_exec('echo 1', '1', log_captured)
        self._assert_exec(':set proxy BOGUS', messages.sessions.set_s_s % ('proxy', 'BOGUS'), log_captured)
        self._assert_exec('echo 1', messages.channels.error_proxy_format, log_captured)
        self._assert_exec(':unset proxy', messages.sessions.unset_s % ('proxy'), log_captured)
        # TODO: move unset and set output in messages
        self._assert_exec('echo 1', '1', log_captured)
        self._assert_exec(':set proxy http://127.0.0.1:12782', 'proxy = http://127.0.0.1:12782', log_captured)
        # Test the behaviour when starting terminal on wrong remote pass
        self._assert_exec('echo 1', messages.terminal.backdoor_unavailable, log_captured)
        self._assert_exec(':unset proxy', messages.sessions.unset_s % ('proxy'), log_captured)
