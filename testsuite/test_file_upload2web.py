from testfixtures import log_capture
from testsuite.base_fs import BaseFilesystem
from testsuite import config
from core.sessions import SessionURL
from core import modules
import utils
from core import messages
import subprocess
import tempfile
import os

class UploadWeb(BaseFilesystem):

    def setUp(self):
        self.session = SessionURL(
                    self.url,
                    self.password,
                    volatile = True
                    )

        modules.load_modules(self.session)

        # Create the folder tree
        self.folders_abs, self.folders_rel =  self.populate_folders()

        self.check_call(
            config.cmd_env_chmod_s_s % ('0777', self.folders_abs[0]),
            shell=True)

        # Change mode of the folders [1] and [3] to -r-xr-xr-x 0555 read & execute
        for fold in (self.folders_abs[1], self.folders_abs[3]):
            self.check_call(
                config.cmd_env_chmod_s_s % ('0555', fold),
                shell=True)

        self.check_call(
            config.cmd_env_chmod_s_s % ('0777', self.folders_abs[2]),
            shell=True)

        self.filenames = []

        self.run_argv = modules.loaded['file_upload2web'].run_argv

    def tearDown(self):

        for f in self.filenames:
            self.check_call(
                config.cmd_env_remove_s % (os.path.join(config.script_folder, f)),
                shell=True)

        # This has to be done before and in order, since in case of
        # nonwritable/writable folders the writable one can't be deleted.
        for folder in self.folders_abs:
            self.check_call(
                config.cmd_env_chmod_s_s % ('0777', folder),
                shell=True)

        for folder in reversed(self.folders_abs):

            self.check_call(
                config.cmd_env_rmdir_s % (folder),
                shell=True)

    def _get_path_url(self, folder_deepness, filename):
        rurl = os.path.sep.join([
                            config.script_folder_url.rstrip('/'),
                            self.folders_rel[folder_deepness].strip('/'),
                            filename.lstrip('/')]
                            )
        rpath = os.path.sep.join([
                            config.script_folder.rstrip('/'),
                            self.folders_rel[folder_deepness].strip('/'),
                            filename.lstrip('/')]
                            )
        return rpath, rurl

    def test_file_uploadweb(self):

        # Upload lfile with a specific path
        temp_file = tempfile.NamedTemporaryFile()
        rpath, rurl = self._get_path_url(0, 'f1')
        self.filenames.append(rpath)
        self.assertEqual(
            self.run_argv([ temp_file.name, rpath ]),
            [ ( rpath, rurl ) ]
            )
        temp_file.close()

        # Upload lfile guessing first writable path starting from [0]
        temp_file = tempfile.NamedTemporaryFile()
        temp_folder, temp_filename = os.path.split(temp_file.name)
        rpath, rurl = self._get_path_url(0, temp_filename)
        self.filenames.append(rpath)
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
        self.filenames.append(rpath)
        self.assertEqual(
            self.run_argv([ temp_file.name, self.folders_rel[1] ]),
            [ ( rpath, rurl ) ]
            )
        temp_file.close()


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
