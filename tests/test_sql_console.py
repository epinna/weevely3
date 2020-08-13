from tests.base_test import BaseTest
from testfixtures import log_capture
from core import modules
from core.sessions import SessionURL
from core import messages
from tests import config
import unittest
import subprocess
import os

def setUpModule():
    try:
        # This workaround fixes https://github.com/docker/for-linux/issues/72
        subprocess.check_output("""find /var/lib/mysql -type f -exec touch {} \; && service mysql start""", shell=True)
    except Exception as e:
        print('[!] Failed mysql')
        print(subprocess.check_output("""grep "" /var/log/mysql/*""", shell=True))
        raise

class MySQLConsole(BaseTest):

    def setUp(self):
        self.session = SessionURL(self.url, self.password, volatile = True)
        modules.load_modules(self.session)

        self.run_argv = modules.loaded['sql_console'].run_argv
        self.run_cmdline = modules.loaded['sql_console'].run_cmdline

    @unittest.skipIf(not config.sql_autologin,
                    "Autologin is not set")
    def test_autologin(self):
        self.assertEqual(self.run_argv(['-query', "select 'A';"]), { 'error' : '', 'result' : [["A"], ["A"]] })
        self.assertEqual(self.run_argv(['-query', 'select @@hostname;'])['error'], '')
        self.assertEqual(self.run_argv(['-query', 'show databases;'])['error'], '')

    @log_capture()
    @unittest.skipIf(not config.sql_autologin,
                    "Autologin is not set")
    def test_wrongcommand(self, log_captured):
        # Wrong command
        self.assertEqual(self.run_cmdline('-query bogus')['result'], [])

        # Checking if the error message start about the missing comma is ok
        self.assertEqual('%s %s' % (messages.module_sql_console.no_data,
                                    messages.module_sql_console.check_credentials),
                         log_captured.records[-2].msg)


    def test_wronglogin(self):

        wrong_login = '-user bogus -passwd bogus -query "select \'A\';"'

        # Using run_cmdline to test the outputs
        self.assertIn('Access denied for user', self.run_cmdline(wrong_login)['error'])

    def test_login(self):

        login = ['-user', config.sql_user, '-passwd', config.sql_passwd ]

        self.assertEqual(self.run_argv(login + [ '-query', "select 'A';"]), { 'error' : ' ', 'result' :  [['A'], ['A']] })
        self.assertEqual(self.run_argv(login + ['-query', 'select @@hostname;'])['error'], ' ')
        self.assertEqual(self.run_argv(login + ['-query', 'show databases;'])['error'], ' ')

        # The user is returned in the form `[[ user@host ]]`
        self.assertEqual(
            self.run_argv(login + ['-query', 'SELECT USER();'])['result'][1][0][:len(config.sql_user)],
            config.sql_user
        )
        self.assertEqual(
            self.run_argv(login + ['-query', 'SELECT CURRENT_USER();'])['result'][1][0][:len(config.sql_user)],
            config.sql_user
        )
