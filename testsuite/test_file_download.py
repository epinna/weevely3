from testsuite.base_test import BaseTest
from testfixtures import log_capture
from testsuite import config
from core.sessions import SessionURL
from core import modules
from core import messages
import subprocess
import tempfile
import datetime
import logging
import os

class FileDOwnload(BaseTest):

    def setUp(self):
        session = SessionURL(self.url, self.password, volatile = True)
        modules.load_modules(session)

        self.file_ok = os.path.join(config.script_folder, 'ok.test')
        self.check_call(
            config.cmd_env_content_s_to_s % ('OK', self.file_ok),
            shell=True)

        self.file_ko = os.path.join(config.script_folder, 'ko.test')
        self.check_call(
            config.cmd_env_content_s_to_s % ('KO', self.file_ko),
            shell=True)
        # Set ko.test to ---x--x--x 0111 execute, should be no readable
        self.check_call(
            config.cmd_env_chmod_s_s % ('0111', self.file_ko),
            shell=True)

        self.run_argv = modules.loaded['file_download'].run_argv


    def tearDown(self):

        self.check_call(
            config.cmd_env_chmod_s_s % ('0777', '%s %s' % (self.file_ok, self.file_ko)),
            shell=True)

        self.check_call(
            config.cmd_env_remove_s % ('%s %s' % (self.file_ok, self.file_ko)),
            shell=True)

    def test_download_php(self):
        temp_file = tempfile.NamedTemporaryFile()

        # Simple download
        self.assertEqual(self.run_argv(['ok.test', temp_file.name]), 'OK')
        self.assertEqual(open(temp_file.name,'r').read(), 'OK')
        temp_file.truncate()

        # Downoad binary. Skip check cause I don't know the remote content, and
        # the md5 check is already done inside file_download.
        self.assertTrue(self.run_argv(['/bin/ls', temp_file.name]))
        self.assertTrue(open(temp_file.name,'r').read(), 'OK')
        temp_file.truncate()

        # Download of an unreadable file
        self.assertEqual(self.run_argv(['ko.test', temp_file.name]), None)
        self.assertEqual(open(temp_file.name,'r').read(), '')

        # Download of an remote unexistant file
        self.assertEqual(self.run_argv(['bogus', temp_file.name]), None)
        self.assertEqual(open(temp_file.name,'r').read(), '')

        # Download to a local unexistant folder
        self.assertEqual(self.run_argv(['ok.test', '/tmp/bogus/bogus']), None)
        self.assertEqual(open(temp_file.name,'r').read(), '')

        # Download to a directory
        self.assertEqual(self.run_argv(['ok.test', '/tmp/']), None)
        self.assertEqual(open(temp_file.name,'r').read(), '')

        temp_file.close()


    def test_download_sh(self):
        temp_file = tempfile.NamedTemporaryFile()

        # Simple download
        self.assertEqual(self.run_argv(['-vector', 'base64', 'ok.test', temp_file.name]), 'OK')
        self.assertEqual(open(temp_file.name,'r').read(), 'OK')
        temp_file.truncate()

        # Downoad binary. Skip check cause I don't know the remote content, and
        # the md5 check is already done inside file_download.
        self.assertTrue(self.run_argv(['-vector', 'base64', '/bin/ls', temp_file.name]))
        self.assertTrue(open(temp_file.name,'r').read(), 'OK')
        temp_file.truncate()

        # Download of an unreadable file
        self.assertEqual(self.run_argv(['-vector', 'base64', 'ko.test', temp_file.name]), None)
        self.assertEqual(open(temp_file.name,'r').read(), '')

        # Download of an remote unexistant file
        self.assertEqual(self.run_argv(['-vector', 'base64', 'bogus', temp_file.name]), None)
        self.assertEqual(open(temp_file.name,'r').read(), '')

        # Download to a local unexistant folder
        self.assertEqual(self.run_argv(['-vector', 'base64', 'ok.test', '/tmp/bogus/bogus']), None)
        self.assertEqual(open(temp_file.name,'r').read(), '')

        # Download to a directory
        self.assertEqual(self.run_argv(['-vector', 'base64', 'ok.test', '/tmp/']), None)
        self.assertEqual(open(temp_file.name,'r').read(), '')

        temp_file.close()
