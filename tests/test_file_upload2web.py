from testfixtures import log_capture
from tests.base_test import BaseTest
from tests import config
from core.sessions import SessionURL
from core import modules
import utils
from core import messages
import subprocess
import tempfile
import os

def setUpModule():
    subprocess.check_output("""
BASE_FOLDER="{config.base_folder}/test_file_upload2web/"
rm -rf "$BASE_FOLDER"

mkdir -p "$BASE_FOLDER/0777/0555/0777/0555"
chown www-data: -R "$BASE_FOLDER/"
chmod 0777 "$BASE_FOLDER/0777" 
chmod 0777 "$BASE_FOLDER/0777/0555/0777/"
chmod 0555 "$BASE_FOLDER/0777/0555" 
chmod 0555 "$BASE_FOLDER/0777/0555/0777/0555"
""".format(
config = config
), shell=True)

class UploadWeb(BaseTest):

    def setUp(self):
        self.session = SessionURL(
                    self.url,
                    self.password,
                    volatile = True
                    )

        modules.load_modules(self.session)

        # Create the folder tree
        self.folders_rel = [
            'test_file_upload2web/0777/',
            'test_file_upload2web/0777/0555/',
            'test_file_upload2web/0777/0555/0777/',
            'test_file_upload2web/0777/0555/0777/0555'
        ]

        self.run_argv = modules.loaded['file_upload2web'].run_argv


    def _get_path_url(self, folder_deepness, filename):
        
        rurl = os.path.sep.join([
                            config.base_url.rstrip('/'),
                            self.folders_rel[folder_deepness].strip('/'),
                            filename.lstrip('/')]
                            )
        rpath = os.path.sep.join([
                            config.base_folder.rstrip('/'),
                            self.folders_rel[folder_deepness].strip('/'),
                            filename.lstrip('/')]
                            )
        return rpath, rurl

    def test_file_uploadweb(self):

        # Upload lfile with a specific path
        temp_file = tempfile.NamedTemporaryFile()
        rpath, rurl = self._get_path_url(0, 'f1')
        self.assertEqual(
            self.run_argv([ temp_file.name, rpath ]),
            [ ( rpath, rurl ) ]
            )
        temp_file.close()

        # Upload lfile guessing first writable path starting from [0]
        temp_file = tempfile.NamedTemporaryFile()
        temp_folder, temp_filename = os.path.split(temp_file.name)
        rpath, rurl = self._get_path_url(0, temp_filename)
        self.assertEqual(
            self.run_argv([ temp_file.name, self.folders_rel[0] ]),
            [ ( rpath, rurl ) ]
            )
        temp_file.close()

        # Upload lfile guessing first writable path from [1],
        # that is [2]
        temp_file = tempfile.NamedTemporaryFile()
        temp_folder, temp_filename = os.path.split(temp_file.name)
        rpath, rurl = self._get_path_url(2, temp_filename)
        self.assertEqual(
            self.run_argv([ temp_file.name, self.folders_rel[1] ]),
            [ ( rpath, rurl ) ]
            )
        temp_file.close()


    def test_file_uploadweb_content(self):

        # Upload content with fake lfile guessing first writable path from [1],
        # that is [2]
        temp_file_name = '/tmp/nonexistant'
        temp_folder, temp_filename = os.path.split(temp_file_name)
        rpath, rurl = self._get_path_url(2, temp_filename)
        self.assertEqual(
            self.run_argv([ temp_file_name, self.folders_rel[1], '-content', '1' ]),
            [ ( rpath, rurl ) ]
            )

    @log_capture()
    def test_uploadweb_errs(self, log_captured):

        # Upload a not existant lpath
        self.assertIsNone(self.run_argv([ 'bogus', self.folders_rel[0] ]))
        self.assertEqual(log_captured.records[-1].msg[:18],
                         messages.generic.error_loading_file_s_s[:18])

        # Upload a not existant rpath
        temp_file = tempfile.NamedTemporaryFile()
        self.assertIsNone(self.run_argv([ temp_file.name, self.folders_rel[0] + '/bogus/bogus' ]))
        self.assertEqual(log_captured.records[-1].msg,
                         messages.module_file_upload.failed_upload_file)

        # Upload a not writable folder
        temp_file = tempfile.NamedTemporaryFile()
        self.assertIsNone(self.run_argv([ temp_file.name, self.folders_rel[3] + '/bogus' ]))
        self.assertEqual(log_captured.records[-1].msg,
                         messages.module_file_upload.failed_upload_file)
