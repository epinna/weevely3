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
BASE_FOLDER="{config.base_folder}/test_file_upload/"
rm -rf "$BASE_FOLDER"

mkdir -p "$BASE_FOLDER"
echo -n 'KO' > "$BASE_FOLDER/ok.test"
chown www-data: -R "$BASE_FOLDER/"
""".format(
config = config
), shell=True)

class FileUpload(BaseTest):

    def setUp(self):
        session = SessionURL(self.url, self.password, volatile = True)
        modules.load_modules(session)

        self.run_argv = modules.loaded['file_upload'].run_argv

    @log_capture()
    def test_upload(self, log_captured):

        # Upload content
        self.assertTrue(self.run_argv([ 'test_file_upload/f1', '-content', 'CONTENT' ]))

        # Upload lfile
        temp_file = tempfile.NamedTemporaryFile()
        temp_file.write(b'CONTENT')
        self.assertTrue(self.run_argv([ temp_file.name, 'test_file_upload/f2' ]))
        temp_file.close()

    @log_capture()
    def test_upload_fwrite(self, log_captured):

        # Upload content
        self.assertTrue(self.run_argv([ 'test_file_upload/f3', '-content', 'CONTENT', '-vector', 'fwrite' ]))

        # Upload lfile
        temp_file = tempfile.NamedTemporaryFile()
        temp_file.write(b'CONTENT')
        self.assertTrue(self.run_argv([ temp_file.name, 'test_file_upload/f4', '-vector', 'fwrite' ]))
        temp_file.close()

    @log_capture()
    def test_upload_errs(self, log_captured):

        # Do not specify content or lpath
        self.assertFalse(self.run_argv([ 'bogus' ]))
        self.assertEqual(log_captured.records[-1].msg,
                         messages.module_file_upload.error_content_lpath_required)

        # Upload a not existant lpath
        self.assertFalse(self.run_argv([ 'bogus', 'bogus' ]))
        self.assertEqual(log_captured.records[-1].msg[:18],
                         messages.generic.error_loading_file_s_s[:18])

        # Upload to a not existant rpath
        self.assertFalse(self.run_argv([ 'asd/asd/asd/asd', '-content', 'CONTENT' ]))
        self.assertEqual(log_captured.records[-1].msg,
                         messages.module_file_upload.failed_upload_file)

    def test_upload_empty(self):

        # Upload content
        self.assertTrue(self.run_argv([ 'test_file_upload/f5', '-content', '' ]))

        # Upload lfile
        temp_file = tempfile.NamedTemporaryFile()
        self.assertTrue(self.run_argv([ temp_file.name, 'test_file_upload/f6' ]))
        temp_file.close()


    @log_capture()
    def test_upload_overwrite(self, log_captured):

        # Try to overwrite
        self.assertFalse(self.run_argv([ 'test_file_upload/ok.test', '-content', 'CONTENT' ]))
        self.assertEqual(log_captured.records[-1].msg,
                         messages.generic.error_file_s_already_exists % 'test_file_upload/ok.test')

        # Now force
        self.assertTrue(self.run_argv([ 'test_file_upload/ok.test', '-content', 'CONTENT', '-force' ]))

    @log_capture()
    def test_upload_overwrite_fwrite(self, log_captured):

        # Try to overwrite
        self.assertFalse(self.run_argv([ 'test_file_upload/ok.test', '-content', 'CONTENT', '-vector', 'fwrite' ]))
        self.assertEqual(log_captured.records[-1].msg,
                         messages.generic.error_file_s_already_exists % 'test_file_upload/ok.test')

        # Now force
        self.assertTrue(self.run_argv([ 'test_file_upload/ok.test', '-content', 'CONTENT', '-force', '-vector', 'fwrite' ]))

    @log_capture()
    def test_upload_binary(self, log_captured):

        binary_content = b'\xbe\x00\xc8d\xf8d\x08\xe4'

        # Upload lfile
        temp_file = tempfile.NamedTemporaryFile()
        temp_file.write(binary_content)
        self.assertTrue(self.run_argv([ temp_file.name, 'test_file_upload/f8' ]))
        temp_file.close()

    @log_capture()
    def test_upload_binary_fwrite(self, log_captured):

        binary_content = b'\xbe\x00\xc8d\xf8d\x08\xe4'

        # Upload lfile
        temp_file = tempfile.NamedTemporaryFile()
        temp_file.write(binary_content)
        self.assertTrue(self.run_argv([ temp_file.name, 'test_file_upload/f10', '-vector', 'fwrite' ]))
        temp_file.close()
