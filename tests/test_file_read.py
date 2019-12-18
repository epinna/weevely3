from tests.base_test import BaseTest
from testfixtures import log_capture
from tests import config
from core.sessions import SessionURL
from core import modules
from core import messages
import subprocess
import tempfile
import datetime
import logging
import os

def setUpModule():
    subprocess.check_output("""
BASE_FOLDER="{config.base_folder}/test_file_read/"
rm -rf "$BASE_FOLDER"

mkdir -p "$BASE_FOLDER"
echo -n 'OK' > "$BASE_FOLDER/ok.test"
echo -n 'KO' > "$BASE_FOLDER/ko.test"
# Set ko.test to ---x--x--x 0111 execute, should be no readable
chmod 0111 "$BASE_FOLDER/ko.test"
""".format(
config = config
), shell=True)

class FileRead(BaseTest):

    def setUp(self):
        session = SessionURL(self.url, self.password, volatile = True)
        modules.load_modules(session)

        self.run_argv = modules.loaded['file_read'].run_argv

    def test_read_php(self):

        # Simple download
        self.assertEqual(self.run_argv(['test_file_read/ok.test']), b'OK')

        # Downoad binary. Skip check cause I don't know the remote content, and
        # the md5 check is already done inside file_download.
        self.assertTrue(self.run_argv(['/bin/ls']))

        # Download of an unreadable file
        self.assertEqual(self.run_argv(['test_file_read/ko.test']), None)

        # Download of an remote unexistant file
        self.assertEqual(self.run_argv(['bogus']), None)


    def test_read_allvectors(self):

        for vect in modules.loaded['file_download'].vectors.get_names():
            self.assertEqual(self.run_argv(['-vector', vect, 'test_file_read/ok.test']), b'OK')

    def test_read_sh(self):

        # Simple download
        self.assertEqual(self.run_argv(['-vector', 'base64', 'test_file_read/ok.test']), b'OK')

        # Downoad binary. Skip check cause I don't know the remote content, and
        # the md5 check is already done inside file_download.
        self.assertTrue(self.run_argv(['-vector', 'base64', '/bin/ls']))

        # Download of an unreadable file
        self.assertEqual(self.run_argv(['-vector', 'base64', 'test_file_read/ko.test']), None)

        # Download of an remote unexistant file
        self.assertEqual(self.run_argv(['-vector', 'base64', 'bogus']), None)
