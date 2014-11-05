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

class FileUpload(BaseTest):

    def setUp(self):
        session = SessionURL(self.url, self.password, volatile = True)
        modules.load_modules(session)

        self.filenames = [ 'ok.test' ]
        self.check_call(
            config.cmd_env_content_s_to_s % ('OK', os.path.join(config.script_folder, self.filenames[0])),
            shell=True)

        self.run_argv = modules.loaded['file_upload'].run_argv


    def tearDown(self):

        for f in self.filenames:
            self.check_call(
                config.cmd_env_remove_s % (os.path.join(config.script_folder, f)),
                shell=True)

    @log_capture()
    def test_upload(self, log_captured):

        # Upload content
        self.filenames.append('f1')
        self.assertTrue(self.run_argv([ self.filenames[-1], '-content', 'CONTENT' ]))

        # Upload lfile
        temp_file = tempfile.NamedTemporaryFile()
        temp_file.write('CONTENT')
        self.filenames.append('f2')
        self.assertTrue(self.run_argv([ temp_file.name, self.filenames[-1] ]))
        temp_file.close()

    @log_capture()
    def test_upload_fwrite(self, log_captured):

        # Upload content
        self.filenames.append('f1')
        self.assertTrue(self.run_argv([ self.filenames[-1], '-content', 'CONTENT', '-vector', 'fwrite' ]))

        # Upload lfile
        temp_file = tempfile.NamedTemporaryFile()
        temp_file.write('CONTENT')
        self.filenames.append('f2')
        self.assertTrue(self.run_argv([ temp_file.name, self.filenames[-1], '-vector', 'fwrite' ]))
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

        # Upload content ()
        self.filenames.append('f3')
        self.assertTrue(self.run_argv([ self.filenames[-1], '-content', '' ]))

        # Upload lfile
        temp_file = tempfile.NamedTemporaryFile()
        self.filenames.append('f4')
        self.assertTrue(self.run_argv([ temp_file.name, self.filenames[-1] ]))
        temp_file.close()


    @log_capture()
    def test_upload_overwrite(self, log_captured):

        # Create an overwritable remote file
        self.filenames.append('f5')
        self.check_call(
            config.cmd_env_content_s_to_s % ('OK', os.path.join(config.script_folder, self.filenames[-1])),
            shell=True)
        self.check_call(
            config.cmd_env_chmod_s_s % ('0777', os.path.join(config.script_folder, self.filenames[-1])),
            shell=True)

        # Try to overwrite
        self.assertFalse(self.run_argv([ 'f5', '-content', 'CONTENT' ]))
        self.assertEqual(log_captured.records[-1].msg,
                         messages.generic.error_file_s_already_exists % 'f5')

        # Now force
        self.assertTrue(self.run_argv([ 'f5', '-content', 'CONTENT', '-force' ]))

    @log_capture()
    def test_upload_overwrite_fwrite(self, log_captured):

        # Create an overwritable remote file
        self.filenames.append('f5')
        self.check_call(
            config.cmd_env_content_s_to_s % ('OK', os.path.join(config.script_folder, self.filenames[-1])),
            shell=True)
        self.check_call(
            config.cmd_env_chmod_s_s % ('0777', os.path.join(config.script_folder, self.filenames[-1])),
            shell=True)

        # Try to overwrite
        self.assertFalse(self.run_argv([ 'f5', '-content', 'CONTENT', '-vector', 'fwrite' ]))
        self.assertEqual(log_captured.records[-1].msg,
                         messages.generic.error_file_s_already_exists % 'f5')

        # Now force
        self.assertTrue(self.run_argv([ 'f5', '-content', 'CONTENT', '-force', '-vector', 'fwrite' ]))

    @log_capture()
    def test_upload_binary(self, log_captured):

        binary_content = '\xbe\x00\xc8d\xf8d\x08\xe4'

        # Upload content
        self.filenames.append('f6')
        self.assertTrue(self.run_argv([ self.filenames[-1], '-content', binary_content ]))

        # Upload lfile
        temp_file = tempfile.NamedTemporaryFile()
        temp_file.write(binary_content)
        self.filenames.append('f7')
        self.assertTrue(self.run_argv([ temp_file.name, self.filenames[-1] ]))
        temp_file.close()

    @log_capture()
    def test_upload_binary_fwrite(self, log_captured):

        binary_content = '\xbe\x00\xc8d\xf8d\x08\xe4'

        # Upload content
        self.filenames.append('f6')
        self.assertTrue(self.run_argv([ self.filenames[-1], '-content', binary_content, '-vector', 'fwrite' ]))

        # Upload lfile
        temp_file = tempfile.NamedTemporaryFile()
        temp_file.write(binary_content)
        self.filenames.append('f7')
        self.assertTrue(self.run_argv([ temp_file.name, self.filenames[-1], '-vector', 'fwrite' ]))
        temp_file.close()
