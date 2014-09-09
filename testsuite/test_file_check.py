from testsuite.base_test import BaseTest
from testfixtures import log_capture
from testsuite.config import script_folder
from core import modules
from core import sessions
from core import messages
import datetime
import logging
import os

class FileCheck(BaseTest):

    def setUp(self):
        session = sessions.start_session_by_url(self.url, self.password, volatile = True)
        modules.load_modules(session)

        self.run_argv = modules.loaded['file_check'].run_argv

    def test_check(self):

        # Some check on a privileged file
        self.assertTrue(self.run_argv(['/etc/passwd', 'exists']))
        self.assertTrue(self.run_argv(['/etc/passwd', 'readable']))
        self.assertTrue(self.run_argv(['/etc/passwd', 'file']))
        self.assertFalse(self.run_argv(['/etc/passwd', 'executable']))
        self.assertFalse(self.run_argv(['/etc/passwd', 'writable']))

        # Some check on an unexistant file
        self.assertFalse(self.run_argv(['/etc/BOGUS', 'exists']))
        self.assertFalse(self.run_argv(['/etc/BOGUS', 'readable']))
        self.assertFalse(self.run_argv(['/etc/BOGUS', 'file']))
        self.assertFalse(self.run_argv(['/etc/BOGUS', 'executable']))
        self.assertFalse(self.run_argv(['/etc/BOGUS', 'writable']))

        # Some check on an accessible folder
        self.assertTrue(self.run_argv(['/tmp', 'exists']))
        self.assertTrue(self.run_argv(['/tmp', 'readable']))
        self.assertFalse(self.run_argv(['/tmp', 'file']))
        self.assertTrue(self.run_argv(['/tmp', 'executable']))
        self.assertTrue(self.run_argv(['/tmp', 'writable']))

        # Some check, with also md5 and time check
        # First check if the current folder is writable
        self.assertTrue(
            self.run_argv(['.', 'writable']),
            'Error: please set the script folder \'%s\' writable by the httpd user and re-run the test' % script_folder
        )
        # Create a test file
        self.assertTrue(self.run_argv(['/tmp', 'writable']))
        modules.loaded['shell_php'].run_argv(['file_put_contents("ftest","1");'])
        # Get the remote timestamp
        rtime = int(modules.loaded['shell_php'].run_argv(['print(time());']))
        rdatetime = datetime.datetime.fromtimestamp(float(rtime)).strftime('%Y-%m-%d')

        self.assertTrue(self.run_argv(['ftest', 'exists']))
        self.assertTrue(self.run_argv(['ftest', 'readable']))
        self.assertTrue(self.run_argv(['ftest', 'file']))
        self.assertFalse(self.run_argv(['ftest', 'executable']))
        self.assertTrue(self.run_argv(['ftest', 'writable']))
        self.assertEqual(self.run_argv(['ftest', 'size']), 1)
        self.assertEqual(self.run_argv(['ftest', 'md5']), 'c4ca4238a0b923820dcc509a6f75849b')
        self.assertAlmostEqual(self.run_argv(['ftest', 'time']), rtime, delta = 20)
        self.assertEqual(self.run_argv(['ftest', 'datetime']).split(' ')[0], rdatetime)
