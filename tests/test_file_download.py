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
BASE_FOLDER="{config.base_folder}/test_file_download/"
rm -rf "$BASE_FOLDER"
mkdir -p "$BASE_FOLDER"
echo -n 'OK' > "$BASE_FOLDER/ok.test"
echo -n 'KO' > "$BASE_FOLDER/ko.test"
# Set ko.test to ---x--x--x 0111 execute, should be no readable
chmod 0111 "$BASE_FOLDER/ko.test"
""".format(
config = config
), shell=True)


class FileDownload(BaseTest):

    file_ok = os.path.join(config.base_folder, '/test_file_download/ok.test')
    file_ko = os.path.join(config.base_folder, '/test_file_download/ko.test')

    def setUp(self):
        session = SessionURL(self.url, self.password, volatile = True)
        modules.load_modules(session)

        self.run_argv = modules.loaded['file_download'].run_argv

    def test_download_php(self):
        temp_file = tempfile.NamedTemporaryFile()

        # Simple download
        self.assertEqual(self.run_argv(['test_file_download/ok.test', temp_file.name]), b'OK')
        with open(temp_file.name, 'r') as temp_file2:
            self.assertEqual(temp_file2.read(), 'OK')
        temp_file.truncate()

        # Downoad binary. Skip check cause I don't know the remote content, and
        # the md5 check is already done inside file_download.
        self.assertTrue(self.run_argv(['/bin/ls', temp_file.name]))
        with open(temp_file.name, 'rb') as temp_file2:
            self.assertTrue(temp_file2.read())
        temp_file.truncate()

        # Download of an unreadable file
        self.assertEqual(self.run_argv(['test_file_download/ko.test', temp_file.name]), None)

        with open(temp_file.name, 'r') as temp_file2:
            self.assertEqual(temp_file2.read(), '')

        # Download of an remote unexistant file
        self.assertEqual(self.run_argv(['bogus', temp_file.name]), None)
        with open(temp_file.name, 'r') as temp_file2:
            self.assertEqual(temp_file2.read(), '')


        # Download to a local unexistant folder
        self.assertEqual(self.run_argv(['test_file_download/ok.test', '/tmp/bogus/bogus']), None)
        with open(temp_file.name, 'r') as temp_file2:
            self.assertEqual(temp_file2.read(), '')


        # Download to a directory
        self.assertEqual(self.run_argv(['ok.test', '/tmp/']), None)
        with open(temp_file.name, 'r') as temp_file2:
            self.assertEqual(temp_file2.read(), '')


        temp_file.close()


    def test_download_sh(self):
        temp_file = tempfile.NamedTemporaryFile()

        # Simple download
        self.assertEqual(self.run_argv(['-vector', 'base64', 'test_file_download/ok.test', temp_file.name]), b'OK')
        with open(temp_file.name, 'r') as temp_file2:
            self.assertEqual(temp_file2.read(), 'OK')

        temp_file.truncate()

        # Downoad binary. Skip check cause I don't know the remote content, and
        # the md5 check is already done inside file_download.
        self.assertTrue(self.run_argv(['-vector', 'base64', '/bin/ls', temp_file.name]))
        with open(temp_file.name, 'rb') as temp_file2:
            self.assertTrue(temp_file2.read())

        temp_file.truncate()

        # Download of an unreadable file
        self.assertEqual(self.run_argv(['-vector', 'base64', 'test_file_download/ko.test', temp_file.name]), None)
        with open(temp_file.name, 'r') as temp_file2:
            self.assertEqual(temp_file2.read(), '')


        # Download of an remote unexistant file
        self.assertEqual(self.run_argv(['-vector', 'base64', 'bogus', temp_file.name]), None)
        with open(temp_file.name, 'r') as temp_file2:
            self.assertEqual(temp_file2.read(), '')


        # Download to a local unexistant folder
        self.assertEqual(self.run_argv(['-vector', 'base64', 'test_file_download/ok.test', '/tmp/bogus/bogus']), None)
        with open(temp_file.name, 'r') as temp_file2:
            self.assertEqual(temp_file2.read(), '')


        # Download to a directory
        self.assertEqual(self.run_argv(['-vector', 'base64', 'test_file_download/ok.test', '/tmp/']), None)
        with open(temp_file.name, 'r') as temp_file2:
            self.assertEqual(temp_file2.read(), '')


        temp_file.close()
