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
        subprocess.check_call(
            config.cmd_env_content_s_to_s % ('OK', self.file_ok),
            shell=True)

        self.file_ko = os.path.join(config.script_folder, 'ko.test')
        subprocess.check_call(
            config.cmd_env_content_s_to_s % ('KO', self.file_ko),
            shell=True)
        # Set ko.test to ---x--x--x 0111 execute, should be no readable
        subprocess.check_call(
            config.cmd_env_chmod_s_s % ('0111', self.file_ko),
            shell=True)

        self.run_argv = modules.loaded['file_download'].run_argv


    def tearDown(self):

        subprocess.check_call(
            config.cmd_env_chmod_s_s % ('0777', '%s %s' % (self.file_ok, self.file_ko)),
            shell=True)

        subprocess.check_call(
            config.cmd_env_remove_s % ('%s %s' % (self.file_ok, self.file_ko)),
            shell=True)

    def test_download(self):
        temp_file = tempfile.NamedTemporaryFile()

        # Correct download
        self.assertEqual(self.run_argv(['ok.test', temp_file.name]), 'OK')
        self.assertEqual(open(temp_file.name,'r').read(), 'OK')
